# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------
from collections import namedtuple
from enum import Enum


# -------------------------------------------------------------------------------------------------
# Structures of interest
# -------------------------------------------------------------------------------------------------
class Specie(str, Enum):
    ZERODEUX = "zerodeux"
    SULFATE_CAMS = "sulphate"
    SEA_SALT_CAMS = "sea_salt"
    DUST_CAMS = "dust"
    BLACK_CARBON_CAMS = "black_carbon"
    NITRATE_CAMS = "nitrate"
    AMMONIUM_CAMS = "ammonium"
    ORGANIC_MATTER_CAMS = "organic_matter"

class GranuMode(Enum):
    MONO_MODAL = 1
    BI_MODAL = 2

class CamsVersion(str, Enum):
    pass

GranuloLN = namedtuple("GranuloLN", ["rm", "sigma"])
