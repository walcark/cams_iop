# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------
from numpy.typing import NDArray
from typing import TypeAlias
from pathlib import Path
import numpy as np
import logging

# -------------------------------------------------------------------------------------------------
# Module-level constants
# -------------------------------------------------------------------------------------------------
MODULE_ROOT = Path(__file__).resolve().parent.parent.parent

# Internal paths
DATA_DIR = MODULE_ROOT / "data"
TMP_DIR = MODULE_ROOT / "tmp"
OUT_DIR = MODULE_ROOT / "out"
SRC_DIR = MODULE_ROOT / "src/maja_lut_prof_sos"
TEST_DIR = MODULE_ROOT / "tests"


# -------------------------------------------------------------------------------------------------
# Physical constants
# -------------------------------------------------------------------------------------------------
WLS = np.array([
    250, 300, 350, 400, 450, 500, 
    550, 600, 650, 700, 750, 800, 
    900, 1000, 1250, 1500, 1750, 
    2000, 2250
])

RHS = np.array([
    0, 10, 20, 30, 40, 50, 
    60, 70, 80, 85, 90, 95
])

# -------------------------------------------------------------------------------------------------
# Type annotations
# -------------------------------------------------------------------------------------------------
np64: TypeAlias = NDArray[np.float64]
np32: TypeAlias = NDArray[np.float32]
int64: TypeAlias = NDArray[np.int64]


# -------------------------------------------------------------------------------------------------
# Logger instanciator
# -------------------------------------------------------------------------------------------------
def get_logger(
    name: str = "LauncherSOS", 
    level: int = logging.INFO
) -> logging.Logger:
    """
    Setup a local logger for a given module.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        formatter = logging.Formatter(
            "[%(asctime)s][%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
