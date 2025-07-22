from main import WLS, RHS, TMP_DIR, OUT_DIR, np64, int64, np32, get_logger
from read_inputs import (read_aerosol_hydrophilicity, 
                         write_refractive_index_files, 
                         read_granulometry)
from structs import Specie, GranuMode, GranuloLN
from datetime import datetime
from pathlib import Path
from typing import List
import xarray as xr
import numpy as np
import subprocess
import time
import os

logger = get_logger(__name__)


def write_launching_file(
    specie: Specie, 
    gm: GranuMode, 
    rh: int,
    wls_nm: np64 = WLS,
    n_theta: int = 2000,
    cams_version: str = "49r1",
    input_filename: str = Path(TMP_DIR) / "launcher.txt",
    output_filename: str = Path(TMP_DIR) / "results.txt",
) -> str:
    """
    Creates the file used to launch MOPSMAP v1.0, and returns the path
    to the file and to the output data.
    """
    iop_f = GranuloLN
    iop_c = GranuloLN
    iop_f, iop_c = read_granulometry(specie, gm, rh, cams_version)
    file_f, file_c = write_refractive_index_files(specie, gm, rh, wls_nm, cams_version)

    with open(input_filename, "w") as file:
        file.write("scatlib '/home/kwalcarius/bin/mopsmap/optical_dataset'\n")
        file.write("water_refrac_file '/home/kwalcarius/bin/mopsmap/data/refr_water_segelstein'\n")

        i: int = 0
        for mode, fname in zip([iop_f, iop_c], [file_f, file_c]):
            file.write("mode {} size log_normal {} {} {} {} {}\n".format(
                i+1, mode.rm, np.exp(mode.sigma), 1.0, 0.001, 40.0
            ))
            file.write("mode {} refrac file '{}'\n".format(i+1, fname))
            file.write(f"mode {i+1} shape sphere\n")
            i+=1

        file.write(f"output num_theta {n_theta}\n")
        file.write("wavelength list {}\n".format(" ".join([str(wl/1E3) for wl in wls_nm])))
        file.write(f"output netcdf '{output_filename}'")
    file.close()    
    return input_filename, output_filename


def launch_mopsmap(
    input_filename: str = Path(TMP_DIR) / "launcher.txt"
) -> None:
    """Launches MOPSMAP v1.0 using the launcher.txt file."""
    path_to_mopsmap: str = os.getenv("MOPSMAP_PATH")
    cmd: List[str] = [f"{path_to_mopsmap}/mopsmap", f"{input_filename}"]
    try:
        result = subprocess.run(
            cmd, check=True, text=True, capture_output=True
        )
        logger.info(result)
    except subprocess.CalledProcessError as e:
        logger.error("[ERROR] MOPSMAP v1.0 failed.")
        logger.error(f"[COMMAND] {' '.join(e.cmd)}")
        logger.error(f"[RETURN CODE] {e.returncode}")
        logger.error(f"[STDOUT]\n{e.stdout}")
        logger.error(f"[STDERR]\n{e.stderr}")
        raise


def create_lut_for_smartg(
    specie: Specie, 
    gm: GranuMode, 
    rhs: int64 = RHS,
    wls: np64 = WLS,
    n_theta: int = 2000,
) -> xr.Dataset:
    """
    Creates a LUT that can be used as input in the AerOPAC class of SMART-G.
    """
    wls_final: int64 = wls
    hum_final: np32 = rhs
    theta_final: np32 = None
    phase_arr: np32 = np.zeros((len(wls), 6, n_theta, len(rhs)))
    ext_arr: np32 = np.zeros((len(wls), len(rhs)))
    ssa_arr: np32 = np.zeros((len(wls), len(rhs)))

    for idx, rh in enumerate(RHS):
        logger.info(f"Computing relative humidity: {rh} ...")
        inf, outf = write_launching_file(specie, gm, rh, wls, n_theta)
        while not (os.path.isfile(inf)):
            time.sleep(0.1)

        launch_mopsmap(inf)
        while not (os.path.isfile(outf)):
            time.sleep(0.1) 

        xrds = xr.load_dataset(outf)
        if (theta_final is None):
            theta_final = xrds["theta"].isel(nreff=0, nphamat=0, nlam=0).to_numpy()  
        phase_arr[:, :, :, idx] = np.float64(xrds["phase"].isel(nreff=0).to_numpy())
        ext_arr[:, idx] = xrds["ext"].isel(nreff=0).to_numpy()
        ssa_arr[:, idx] = xrds["ssa"].isel(nreff=0).to_numpy()
   
    phase_darr = xr.DataArray(
        np.moveaxis(phase_arr, [0, 1, 2, 3], [1, 2, 3, 0]), 
        coords={"theta": theta_final, "wav": wls_final, "hum": hum_final},
        dims=["hum", "wav", "stk", "theta"]
    )

    ext_darr = xr.DataArray(
        np.swapaxes(ext_arr, 0, 1),
        coords={"hum": hum_final, "wav": wls_final},
        dims=["hum", "wav"]        
    )

    ssa_darr = xr.DataArray(
        np.swapaxes(ssa_arr, 0, 1),
        coords={"hum": hum_final, "wav": wls_final},
        dims=["hum", "wav"]        
    )

    dataset: xr.Dataset = xr.Dataset(
        {"phase": phase_darr, "ext": ext_darr, "ssa": ssa_darr},
        attrs = {
            "name": specie.value,
            "H_mix_min": 0,
            "H_mix_max": 99,
            "H_stra_min": 0,
            "H_stra_max": 0,
            "H_free_min": 0,
            "H_free_max": 0,
            "Z_mix": 2.0,
            "Z_free": 0.0,
            "Z_stra": 0.0,
            "date": datetime.today().strftime("%Y-%m-%d"),
            "source": "Created by Kevin Walcarius using MOPSMAP v1.0."
        }
    )
    logger.info(f"Succesfully created the dataset for {specie}: {gm}:\n{dataset}")
    output_filename: str = Path(OUT_DIR) / f"{specie.value}_sol.nc"
    dataset.to_netcdf(output_filename)
    return dataset

    
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    ds = create_lut_for_smartg(Specie.AMMONIUM_CAMS, GranuMode.BI_MODAL)
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    for wl in [400, 500, 600, 700, 800, 900]:
        phase = ds["phase"].interp(wav=wl, hum=50, stk=0).data
        angles = ds["theta"]
        plt.plot(angles, phase)

    plt.yscale("log")
    plt.show()