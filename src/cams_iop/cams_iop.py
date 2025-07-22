from pathlib import Path
import numpy as np

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


# Physical constants
WLS = np.array([
    250, 300, 350, 400, 450, 500, 
    550, 600, 650, 700, 750, 800, 
    900, 1000, 1250, 1500, 1750, 
    2000, 2500, 3000, 3200, 3390, 
    3500, 3750, 4000, 4500
])/1E3

RHS = np.array([
    0, 10, 20, 30, 40, 50, 
    60, 70, 80, 85, 90, 95
])