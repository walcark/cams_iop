# CAMS IOPs
Generates CAMS Inherent Optical Properties (IOPs) with MOPSMAP v1.0.

# Description
This program uses MOPSMAP v1.0 and a LUT of microphyiscal parameters from the CAMS dataset (https://www.ecmwf.int/en/forecasts/dataset/cams-global-reanalysis) in order the compute the optical properties of the CAMS main aerosols.

The CAMS aerosols are (as of IFS 49r1 cycle for CAMS) :
- Ammonium
- Black carbon
- Dust
- Nitrate
- Organic matter
- Sea Salt
- Suplhate
- Secondary organic

Each aerosol is assumed to follow either of mono-modal or bimodal log-normal distribution. In the case of a bimodal distribution, an aerosol is described with two modes: fine and coarse. For each mode, 4 microphyiscal parameters are required to compute the optical properties:
- the modal radius $r_m$ and standard deviation $\sigma$ of the log-normal distribution. Those parameters depend on the CAMS version and the relative humidity.
- the real and imaginary part of the refractive index $n=m_r + i m_i$. Those parameters depend on the CAMS version, the relative humidity and the wavelength.

Description of the dependance of microphysical parameters on relative humidity, wavelength and CAMS version may be found in https://www.ecmwf.int/en/elibrary/81374-ifs-documentation-cy48r1-part-viii-atmospheric-composition. 

This project stores a Look-Up Table (LUT) of the modal radius, the standard deviation and the refractive index for each mode of the CAMS aerosols (/data/cams_optical_properties.mc). MOPSMAP v1.0 is used to compute the optical properties (phase matrix, single-scattering albedo and extinction coefficient) for different relative humidity and wavelength. The phase matrix is composed of 6 coefficient computed as a function of the scattering angle. The CAMS aerosols are assumed spherical, thus 4 coefficients of the phase matrix are independant and required. However, this library primary use is to compute the optical properties as input for the Smart-G software, which now requires the 6 coefficient of the phase matrix.

# MOPSMAP v1.0
The MOPSMAP software (https://mopsmap.net/) is a dataset of pre-computed optical properties for single particles. It enables to quickly compute optical properties of a mixture of particles e.g specific granulometries.
