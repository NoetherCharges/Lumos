# Lumos!

# Mapping the Milky Way using 21 cm HI line emission

Welcome to the GitHub repository for our **Bachelor’s project** at [IIT Delhi](https://home.iitd.ac.in/). Under the guidance of [Professor Suprit Singh](https://supritsinghlab.github.io/cv/), this project aims to derive the **Rotation curve** and **map the spiral arms of the Milky Way Galaxy** using data from galactic neutral hydrogen (HI) emissions conducted over the course of a single semester. This data is obtained using a **pyramidal horn antenna**, tuned to observe 21 cm (1420.4 MHz) emission from interstellar HI clouds concentrated in the spiral arms of the galaxy, and processed to infer spatial and kinematic properties of the Milky Way.

## Table of Contents 

## Experimental Setup
The experimental setup involves the following signal flow:
1. **Horn Antenna**: The process begins with the pyramidal horn antenna, which captures the 21-cm hydrogen line signals emitted from the galactic plane.
2. **Low-Noise Amplifier (LNA)**: The received signal is directed to a low-noise amplifier equipped with an inbuilt band-pass filter. The LNA amplifies the weak signals and suppresses components outside the allowed band.
3. **Software-Defined Radio (SDR)**: The amplified signal is then fed into a software-defined radio, which digitizes the analog signal for further processing.
4. **Computer / Raspberry Pi**: The processed data is transferred to a computer or Raspberry Pi for further analysis and storage. Here, H-line software extracts data from the RTL-SDR, converts it to an SNR vs. frequency curve, and applies smoothing and corrections for linear trends.

![Experimental setup](images\expsetup.jpg)


## Design of the Horn Antenna

### Why Use a Pyramidal Horn Antenna?
The pyramidal horn antenna was chosen for this project due to its:
- **Ease of Construction**: Simple geometry makes it straightforward to design and fabricate.
- **Cost-Effectiveness**: Requires fewer and inexpensive resources - MDF board, aluminium foil(kitchen foil) and aluminium tape. 
- **Better Directivity**: Horn antennas provide good directivity, making them ideal for capturing signals from specific sky regions.

### How to Select Dimensions of a Horn Antenna
The electrodynamics of the pyramidal horn antenna is analyzed using concepts from Antenna Theory by Constantine A. Balanis. For a detailed explanation, including the procedure to optimize the antenna's directivity, refer to the accompanying theory [pdf]((./path/to/horn_antenna_design.pdf)). The pdf also includes the iterative algorithm used to determine the aperture lengths, along with the corresponding Python [code]((./path/to/horn_antenna_design.pdf)).

add photo of dimensions, horn, radiation pattern


1. **Operating Frequency (\(f\))**: The frequency of the signal to be observed dictates the wavelength (\(\lambda\)) and, consequently, the dimensions of the antenna.
2. **Aperture Dimensions (\(a\) and \(b\))**: These control the gain and beamwidth of the antenna. Larger apertures yield higher gain but narrower beamwidth.
3. **Flare Angles**: The angles of the horn’s walls ensure impedance matching and reduce reflection.
4. **Waveguide Dimensions**: The dimensions of the waveguide feeding the horn must support the desired mode of operation, typically TE\(_{10}\).
5. **Empirical Formulas**:
   - **Aperture width**: \(a = k \lambda\), where \(k\) is a constant based on design specifications.
   - **Horn length**: Calculated to ensure phase alignment of waves at the aperture for maximum gain.

### How to Access More Details
For a detailed explanation of the design process and calculations, refer to the PDF document uploaded in this repository:

- **[Horn Antenna Design Details](./path/to/horn_antenna_design.pdf)**

---

### Note:
Make sure to replace `./path/to/horn_antenna_design.pdf` with the actual path to your PDF in the repository.



## Acknowledgments
This project was presented to an audience of over **3,000 high school students**, fostering interest in astronomy and space science. The event received **national media coverage**, showcasing the importance of science outreach.

I am deeply grateful to **Professor Suprit Singh** for his invaluable guidance and mentorship. His expertise in cosmology and theoretical astrophysics was instrumental in shaping the project and ensuring its success.

---

This repository contains:
- **Code**: Scripts for data processing and mapping.
- **Data**: Observational and processed data from the project.
- **Documentation**: Step-by-step guide to reproduce results and understand the methodology.

Feel free to explore, use, and contribute to this project. Let’s unravel the mysteries of our galaxy together!

## License
This project is licensed under [MIT License](LICENSE).

