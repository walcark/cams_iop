# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------
from structs import Specie, CamsVersion, GranuMode, GranuloLN
from main import DATA_DIR, TMP_DIR, np64
from typing import Tuple
from pathlib import Path
import xarray as xr
import json
import os


# -------------------------------------------------------------------------------------------------
# Input data readers and formatters
# -------------------------------------------------------------------------------------------------
def read_json_from_data(file_name: str) -> None:
    data_path: str = os.path.join(DATA_DIR, file_name)
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Unable to open file: {data_path}") from e
    

def read_aerosol_hydrophilicity(specie: Specie) -> bool:
    """
    Returns a dictionary of hydrophilicity (True/False) for the given list 
    of aerosol names.

    Parameters
    ----------
    aerosol (Specie): 
        Aerosol model name to query.

    Returns
    -------
    bool
        Whether the aerosol in hydrophile or not.
    """
    data = read_json_from_data("aerosol_hydrophilicity.json")
    name = specie.value
    if name not in data:
        raise KeyError(f"Unable to find hydrophilicity for specie: {name}")
    return data[name]


def read_granulometry(
    specie: Specie,
    mode: GranuMode,
    rh: float,
    cams_version: str = "49r1",
) -> Tuple[GranuloLN, GranuloLN]:
    """
    Extracts the coefficient of the Log-Normal distribution (rm, sigma) for
    a given relative humidity, wavelength and cams_version, and returns 
    them as GranuloLN instance.
    
    Parameters
    ----------
        specie (Specie):
            the CAMS specie
        mode (GranuMode):
            the granulometry type (Mono or Bi-Modal)
        rh (float):
            the relative humidity
        cams_version (str):
            the CAMS version of the granulometry   

    Returns 
    -------
        Tuple[GranuloLN, GranuloLN]
            The fine and coarse instance of Log-Normal parameters.
    """
    data_path: str = os.path.join(DATA_DIR, "cams_optical_properties.nc")
    try:
        xrds = xr.load_dataset(data_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Unable to open file: {data_path}") from e 

    xrds_sel = xrds.sel(aerosols_species=specie.value, cams_versions=cams_version)
    values = xrds_sel.interp(relative_humidity=rh)   

    gnl_f: GranuloLN = GranuloLN(rm=float(values[f'rmodal_f'].data),
                                 sigma=float(values[f'lnvar_f'].data))
    if (mode == GranuMode.MONO_MODAL):
        return gnl_f, gnl_f
    gnl_c: GranuloLN = GranuloLN(rm=float(values[f'rmodal_c'].data),
                                 sigma=float(values[f'lnvar_c'].data))
    
    return gnl_f, gnl_c


def write_refractive_index_files(
    specie: Specie,
    mode: GranuMode,
    rh: float, 
    wls_nm: np64,
    cams_version: str = "49r1",
) -> Tuple[str, str]:
    """
    Extracts the refractive index (real and imaginary part) for all
    wavelengths and store them in two files readable by MOPSMAP v1.0
    (one for the fine mode, one for the coarse mode).
    
    Parameters
    ----------
        specie (Specie):
            the CAMS specie
        mode (GranuMode):
            the granulometry type (Mono or Bi-Modal)
        rh (float):
            the relative humidity
        wls_nm (List[float]):
            the list of wavelengths (in nm)
        cams_version (str):
            the CAMS version of the granulometry   

    Returns 
    -------
        Tuple[str, str]
            The paths to the fine and coarse files.
    """
    data_path: str = os.path.join(DATA_DIR, "cams_optical_properties.nc")
    try:
        xrds = xr.load_dataset(data_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Unable to open file: {data_path}") from e 

    xrds_sel = xrds.sel(aerosols_species=specie.value, cams_versions=cams_version)
    values = xrds_sel.interp(relative_humidity=rh, wavelength=wls_nm)   

    wls_microns: np64 = wls_nm / 1E3
    path_f: str = _write_refractive_index_file(
        "refr_fine.txt", wls_microns, values[f'mr_f'].data, values[f'mi_f'].data
    )
    if (mode == GranuMode.MONO_MODAL):
        return path_f, path_f
    path_c: str = _write_refractive_index_file(
        "refr_coarse.txt", wls_microns, values[f'mr_c'].data, values[f'mi_c'].data
    )
    return path_f, path_c


def _write_refractive_index_file(
    filename: str,
    wls_microns: np64,
    mrs: np64,
    mis: np64
) -> str:
    """
    Writes wavelength, mr and mi to a .txt file, using the opposite sign for 
    mis because imaginary part of the refractive index is positive in 
    MOPSMAP v1.0.
    """
    filepath: str = Path(TMP_DIR) / filename
    length: int = len(wls_microns)
    if (len(mrs) != length) or (len(mis) != length):
        raise ValueError(
            "Refractive index lists and wavelength list should have the same size."
        )
    with open(filepath, "w") as file:
        file.writelines([
            "{: 5.3e} {: 9.7f} {: 9.7f}\n".format(wl, mr, -mi)
            for (wl, mr, mi) in zip(wls_microns, mrs, mis)
        ])
    file.close()
    return filepath


# -------------------------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    a, b = read_granulometry(Specie.DUST_CAMS, GranuMode.BI_MODAL, rh=90, wl_nm=400.0)
    print(a, b)

    for specie in Specie:
        print(f"{specie} hydrophilicity: ", read_aerosol_hydrophilicity(specie))

    