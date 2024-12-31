import json
import numpy as np
from astropy.modeling import models, fitting
import matplotlib.pyplot as plt
import math
from datetime import datetime
from PyAstronomy import pyasl
from matplotlib.backends.backend_pdf import PdfPages
import os


# Constants
c = 299792458  # Speed of light in m/s
central_frequency = 1420.40575e6  # Central frequency in Hz (1420.4 MHz)

# Step 1: Load the JSON file (We utilized HI line software to store data in JSON files. You can extract the data in your desired format by modifying this section of the code accordingly.) 
file_path = r"C:\Users\mitta\OneDrive\Desktop\BTP\Spectrums\Spectrums\Day 1\data(ra=303.64,dec=28.46).json"  # Adjust the path if needed
with open(file_path, 'r') as file:
    data = json.load(file)


# Step 2: Extract frequency list, SNR spectrum, and galactic coordinates
frequency_list = data["Data"]["Frequency list"]
snr_spectrum = data["Data"]["SNR Spectrum"]
galactic_lon = data["Observation results"]["Galactic lon"]
galactic_lat = data["Observation results"]["Galactic lat"]

print(f"Galactic Longitude: {galactic_lon}°")
print(f"Galactic Latitude: {galactic_lat}°")

# Step 3: Convert frequency list to velocity list (before LSR correction)
velocity_list = [(freq - central_frequency) / central_frequency * c for freq in frequency_list]  # Velocity in m/s
velocity_list = [v / 1e3 for v in velocity_list]  # Convert to km/s

# Step 4: Fit Gaussian models and a polynomial continuum (Gaussian for the peaks and the polynomial fitting for the noisy background)
gauss_model1 = models.Gaussian1D(amplitude=1, mean=-6, stddev=10)
gauss_model2 = models.Gaussian1D(amplitude=0.7, mean=-50, stddev=20)
gauss_model3 = models.Gaussian1D(amplitude=-0.2, mean=-150, stddev=10)
gauss_model4 = models.Gaussian1D(amplitude=0.7, mean=80, stddev=10)
gauss_model5 = models.Gaussian1D(amplitude=-0.2, mean=150, stddev=10) 
gauss_model6 = models.Gaussian1D(amplitude=0.5, mean=-170, stddev=10)
# Typically, four Gaussian components along with the continuum are sufficient to fit the data. However, additional Gaussian components may be required in some cases to account for more peaks and refine the background for an optimal fit.
mean_snr = np.mean(snr_spectrum)
continuum = np.where(snr_spectrum > mean_snr, mean_snr, snr_spectrum)
linfitter = fitting.LinearLSQFitter()
poly_cont = linfitter(models.Polynomial1D(1), velocity_list, continuum)

# Combine models
combined_model = gauss_model1 + gauss_model2 + gauss_model3 + gauss_model4 + gauss_model5 + gauss_model6 + poly_cont
fitter = fitting.LevMarLSQFitter()
model = fitter(combined_model, velocity_list, snr_spectrum)

# Extract Gaussian parameters
gaussian1 = model[0]
gaussian2 = model[1]
gaussian3 = model[2]
gaussian4 = model[3]
gaussian5 = model[4]
gaussian6 = model[5]

print("Fitted Gaussian Parameters:")
print(f"Gaussian 1: Amplitude={gaussian1.amplitude.value}, Mean={gaussian1.mean.value}, Stddev={gaussian1.stddev.value}")
print(f"Gaussian 2: Amplitude={gaussian2.amplitude.value}, Mean={gaussian2.mean.value}, Stddev={gaussian2.stddev.value}")
print(f"Gaussian 3: Amplitude={gaussian3.amplitude.value}, Mean={gaussian3.mean.value}, Stddev={gaussian3.stddev.value}")
print(f"Gaussian 4: Amplitude={gaussian4.amplitude.value}, Mean={gaussian4.mean.value}, Stddev={gaussian4.stddev.value}")
print(f"Gaussian 5: Amplitude={gaussian5.amplitude.value}, Mean={gaussian5.mean.value}, Stddev={gaussian5.stddev.value}")
print(f"Gaussian 6: Amplitude={gaussian6.amplitude.value}, Mean={gaussian6.mean.value}, Stddev={gaussian6.stddev.value}")
# Step 5: Plot the data and Gaussian fits
fitted_lines = model(velocity_list)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left subplot: SNR Spectrum with Gaussians
axes[0].plot(velocity_list, snr_spectrum, label='SNR Spectrum', color='blue')
axes[0].plot(velocity_list, gaussian1(velocity_list), label='Gaussian 1', color='red')
axes[0].plot(velocity_list, gaussian2(velocity_list), label='Gaussian 2', color='green')
axes[0].plot(velocity_list, gaussian3(velocity_list), label='Gaussian 3', color='orange')
axes[0].plot(velocity_list, gaussian4(velocity_list), label='Gaussian 4', color='violet')
axes[0].plot(velocity_list, gaussian5(velocity_list), label='Gaussian 5', color='magenta')
axes[0].plot(velocity_list, gaussian6(velocity_list), label='Gaussian 6', color='pink')
axes[0].plot(velocity_list, poly_cont(velocity_list), label='Continuum', color='purple', linestyle='--')
axes[0].plot(velocity_list, fitted_lines, label='Combined Fit', color='black')
axes[0].set_title("SNR Spectrum vs Velocity")
axes[0].set_xlabel("Velocity (km/s)")
axes[0].set_ylabel("SNR")
axes[0].grid(True)
axes[0].legend()

# Right subplot: Residuals
residuals = snr_spectrum - fitted_lines
axes[1].plot(velocity_list, residuals, label='Residuals', color='brown')
axes[1].axhline(0, color='black', linestyle='--')
axes[1].set_title("Residuals")
axes[1].set_xlabel("Velocity (km/s)")
axes[1].set_ylabel("Residual SNR")
axes[1].grid(True)
axes[1].legend()

# Show the plot
plt.tight_layout()
plt.show()

# "You may omit the previous steps of plotting and printing the fitted values before the LSR correction, as this is performed below. The plots were generated earlier to provide an overview of the data prior to the correction."

# Step 6: Apply LSR correction
# Extract longitude, latitude, and altitude
observer_data = data.get("Observation parameters", {}).get("Observer", {})
latitude = observer_data.get("latitude")
longitude = observer_data.get("longitude")
altitude = observer_data.get("elevation")
# Print the extracted values
print(f"Latitude: {latitude}\u00B0")
print(f"Longitude: {longitude}\u00B0")
print(f"Altitude: {altitude}m")
obs_ra_2000 = data["Observation results"]["RA"]
obs_dec_2000 = data["Observation results"]["Dec"]
obs_time = datetime.strptime(data["Observation results"]["Time"], "%Y-%m-%d %H:%M:%S.%f")

# Calculate Julian date
jd = pyasl.jdcnv(obs_time)

# Calculate barycentric correction
barycorr, hjd = pyasl.helcorr(longitude, latitude, altitude, obs_ra_2000, obs_dec_2000, jd, debug=False)

# Calculate LSR correction
v_sun = 20.5  # Solar peculiar velocity (km/s)
sun_ra = math.radians(270.2)
sun_dec = math.radians(28.7)
obs_ra = math.radians(obs_ra_2000)
obs_dec = math.radians(obs_dec_2000)

a = math.cos(sun_dec) * math.cos(obs_dec)
b = (math.cos(sun_ra) * math.cos(obs_ra)) + (math.sin(sun_ra) * math.sin(obs_ra))
c = math.sin(sun_dec) * math.sin(obs_dec)
v_lsr = v_sun * ((a * b) + c)

lsr_correction = barycorr + v_lsr
print(f"LSR Corr_SUN [km/s]: {v_lsr}")
print(f"LSR Corr_Bary [km/s]: {barycorr}")
print(f"LSR Correction [km/s]: {lsr_correction}")

# Apply correction to velocity list
corrected_velocity_list = [v - lsr_correction for v in velocity_list]

# Step 7: Re-fit the model to the corrected velocity list
corrected_combined_model = gauss_model1 + gauss_model2 + gauss_model3 + gauss_model4 + gauss_model5 + gauss_model6 + poly_cont
corrected_model = fitter(corrected_combined_model, corrected_velocity_list, snr_spectrum)

# Extract corrected Gaussian parameters
gaussian1_corrected = corrected_model[0]
gaussian2_corrected = corrected_model[1]
gaussian3_corrected = corrected_model[2]
gaussian4_corrected = corrected_model[3]
gaussian5_corrected = corrected_model[4]
gaussian6_corrected = corrected_model[5]



print("Fitted Gaussian Parameters AFTER Re-fitting to Corrected Velocities:")
print(f"Gaussian 1: Amplitude={gaussian1_corrected.amplitude.value}, Mean={gaussian1_corrected.mean.value}, Stddev={gaussian1_corrected.stddev.value}")
print(f"Gaussian 2: Amplitude={gaussian2_corrected.amplitude.value}, Mean={gaussian2_corrected.mean.value}, Stddev={gaussian2_corrected.stddev.value}")
print(f"Gaussian 3: Amplitude={gaussian3_corrected.amplitude.value}, Mean={gaussian3_corrected.mean.value}, Stddev={gaussian3_corrected.stddev.value}")
print(f"Gaussian 4: Amplitude={gaussian4_corrected.amplitude.value}, Mean={gaussian4_corrected.mean.value}, Stddev={gaussian4_corrected.stddev.value}")
print(f"Gaussian 5: Amplitude={gaussian5_corrected.amplitude.value}, Mean={gaussian5_corrected.mean.value}, Stddev={gaussian5_corrected.stddev.value}")
print(f"Gaussian 6: Amplitude={gaussian6_corrected.amplitude.value}, Mean={gaussian6_corrected.mean.value}, Stddev={gaussian6_corrected.stddev.value}")
# Step 8: Plot the corrected velocities with the re-fitted model
fitted_lines_corrected_refitted = corrected_model(corrected_velocity_list)

plt.figure(figsize=(10, 6))
plt.plot(corrected_velocity_list, snr_spectrum, label='SNR Spectrum (Corrected)', color='blue')
plt.plot(corrected_velocity_list, gaussian1_corrected(corrected_velocity_list), label='Gaussian 1 (Corrected)', color='red')
plt.plot(corrected_velocity_list, gaussian2_corrected(corrected_velocity_list), label='Gaussian 2 (Corrected)', color='green')
plt.plot(corrected_velocity_list, gaussian3_corrected(corrected_velocity_list), label='Gaussian 3 (Corrected)', color='orange')
plt.plot(corrected_velocity_list, gaussian4_corrected(corrected_velocity_list), label='Gaussian 4 (Corrected)', color='violet') 
plt.plot(corrected_velocity_list, gaussian5_corrected(corrected_velocity_list), label='Gaussian 5 (Corrected)', color='magenta')
plt.plot(corrected_velocity_list, gaussian6_corrected(corrected_velocity_list), label='Gaussian 6 (Corrected)', color='pink')
plt.plot(corrected_velocity_list, poly_cont(corrected_velocity_list), label='Continuum (Corrected)', color='purple', linestyle='--')
plt.plot(corrected_velocity_list, fitted_lines_corrected_refitted, label='Combined Fit (Corrected and Re-fitted)', color='black')
plt.title("SNR Spectrum vs Velocity (Corrected and Re-fitted)")
plt.xlabel("Velocity (km/s)")
plt.ylabel("SNR")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Prepare the printed text
data_string = (
    f"Galactic Longitude: {galactic_lon}°\n"
    f"Galactic Latitude: {galactic_lat}°\n"
    f"Latitude: {latitude}\u00B0\n"
    f"Longitude: {longitude}\u00B0\n"
    f"Altitude: {altitude}m\n"
    f"LSR Corr_SUN [km/s]: {v_lsr}\n"
    f"LSR Corr_Bary [km/s]: {barycorr}\n"
    f"LSR Correction [km/s]: {lsr_correction}\n"
    "Fitted Gaussian Parameters AFTER Re-fitting to Corrected Velocities:\n"
    f"Gaussian 1: Amplitude={gaussian1_corrected.amplitude.value}, Mean={gaussian1_corrected.mean.value}, Stddev={gaussian1_corrected.stddev.value}\n"
    f"Gaussian 2: Amplitude={gaussian2_corrected.amplitude.value}, Mean={gaussian2_corrected.mean.value}, Stddev={gaussian2_corrected.stddev.value}\n"
    f"Gaussian 3: Amplitude={gaussian3_corrected.amplitude.value}, Mean={gaussian3_corrected.mean.value}, Stddev={gaussian3_corrected.stddev.value}\n"
    f"Gaussian 4: Amplitude={gaussian4_corrected.amplitude.value}, Mean={gaussian4_corrected.mean.value}, Stddev={gaussian4_corrected.stddev.value}\n"
    f"Gaussian 5: Amplitude={gaussian5_corrected.amplitude.value}, Mean={gaussian5_corrected.mean.value}, Stddev={gaussian5_corrected.stddev.value}\n"
    f"Gaussian 6: Amplitude={gaussian6_corrected.amplitude.value}, Mean={gaussian6_corrected.mean.value}, Stddev={gaussian6_corrected.stddev.value}"
)

json_file_name = os.path.splitext(os.path.basename(file_path))[0]
pdf_output_path = f"{json_file_name}.pdf"

# Save everything to the PDF
with PdfPages(pdf_output_path) as pdf:
    # First Plot: Original SNR Spectrum
    fig1, axes = plt.subplots(1, 2, figsize=(14, 6))
    # Left subplot: SNR Spectrum with Gaussians
    axes[0].plot(velocity_list, snr_spectrum, label='SNR Spectrum', color='blue')
    axes[0].plot(velocity_list, gaussian1(velocity_list), label='Gaussian 1', color='red')
    axes[0].plot(velocity_list, gaussian2(velocity_list), label='Gaussian 2', color='green')
    axes[0].plot(velocity_list, gaussian3(velocity_list), label='Gaussian 3', color='orange')
    axes[0].plot(velocity_list, gaussian4(velocity_list), label='Gaussian 4', color='violet')
    axes[0].plot(velocity_list, gaussian5(velocity_list), label='Gaussian 5', color='magenta')
    axes[0].plot(velocity_list, gaussian6(velocity_list), label='Gaussian 6', color='pink')
    axes[0].plot(velocity_list, poly_cont(velocity_list), label='Continuum', color='purple', linestyle='--')
    axes[0].plot(velocity_list, fitted_lines, label='Combined Fit', color='black')
    axes[0].set_title("SNR Spectrum vs Velocity")
    axes[0].set_xlabel("Velocity (km/s)")
    axes[0].set_ylabel("SNR")
    axes[0].grid(True)
    axes[0].legend()
    residuals = snr_spectrum - fitted_lines
    axes[1].plot(velocity_list, residuals, label='Residuals', color='brown')
    axes[1].axhline(0, color='black', linestyle='--')
    axes[1].set_title("Residuals")
    axes[1].set_xlabel("Velocity (km/s)")
    axes[1].set_ylabel("Residual SNR")
    axes[1].grid(True)
    axes[1].legend()
    plt.tight_layout()
    pdf.savefig(fig1)
    plt.close(fig1)

    # Second Plot: LSR-Corrected Spectrum
    fig2 = plt.figure(figsize=(10, 6))
    plt.plot(corrected_velocity_list, snr_spectrum, label='SNR Spectrum (Corrected)', color='blue')
    plt.plot(corrected_velocity_list, gaussian1_corrected(corrected_velocity_list), label='Gaussian 1 (Corrected)', color='red')
    plt.plot(corrected_velocity_list, gaussian2_corrected(corrected_velocity_list), label='Gaussian 2 (Corrected)', color='green')
    plt.plot(corrected_velocity_list, gaussian3_corrected(corrected_velocity_list), label='Gaussian 3 (Corrected)', color='orange')
    plt.plot(corrected_velocity_list, gaussian4_corrected(corrected_velocity_list), label='Gaussian 4 (Corrected)', color='violet')
    plt.plot(corrected_velocity_list, gaussian5_corrected(corrected_velocity_list), label='Gaussian 5 (Corrected)', color='magenta')
    plt.plot(corrected_velocity_list, gaussian6_corrected(corrected_velocity_list), label='Gaussian 6 (Corrected)', color='pink')
    plt.plot(corrected_velocity_list, poly_cont(corrected_velocity_list), label='Continuum (Corrected)', color='purple', linestyle='--')
    plt.plot(corrected_velocity_list, fitted_lines_corrected_refitted, label='Combined Fit (Corrected and Re-fitted)', color='black')
    plt.title("SNR Spectrum vs Velocity (Corrected and Re-fitted)")
    plt.xlabel("Velocity (km/s)")
    plt.ylabel("SNR")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    pdf.savefig(fig2)
    plt.close(fig2)

    # Third Page: Text with Printed Data
    fig3 = plt.figure(figsize=(8.5, 11))  # Standard letter size for the new page
    fig3.text(0.1, 0.9, "Data:", fontsize=14, fontweight="bold", ha="left")
    fig3.text(0.1, 0.8, data_string, fontsize=10, ha="left", va="top", wrap=True)
    pdf.savefig(fig3)  # Save this text-only page to the PDF
    plt.close(fig3)

# Final confirmation message
print(f"Plots and data saved to PDF: {pdf_output_path}")





































