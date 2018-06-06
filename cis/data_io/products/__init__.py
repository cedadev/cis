"""
Module with standard cis Data Products in it
"""

from .aeronet import aeronet_spec
from .cloudsat import CloudSat
from .gridded_NetCDF import NetCDF_Gridded
from .NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from .MODIS import MODIS_L2, MODIS_L3
from .caliop import abstract_Caliop, Caliop_L1, Caliop_L2
from .CCI import Aerosol_CCI, Cloud_CCI
from .HadGEM import HadGEM_PP, HadGEM_CONVSH
