"""
Module with standard cis Data Products in it
"""

from .AProduct import AProduct
from .products import Aeronet, ASCII_Hyperpoints, cis
from .cloudsat import CloudSat
from .gridded_NetCDF import NetCDF_Gridded
from .NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from .MODIS import MODIS_L2, MODIS_L3
from .caliop import abstract_Caliop, Caliop_L1, Caliop_L2
from .CCI import Aerosol_CCI_L2, Cloud_CCI_L2
from .HadGEM import HadGEM_PP, HadGEM_CONVSH

# list of all data products
__all__ = [
    "AProduct",
    "NCAR_NetCDF_RAF",
    "NetCDF_Gridded",
    "MODIS_L2",
    "MODIS_L3",
    "Caliop_L1",
    "Caliop_L2",
    "CCI",
    "Cloud_CCI_L2",
    "Aerosol_CCI_L2",
    "Aeronet",
    "ASCII_Hyperpoints",
    "cis",
    "HadGEM_CONVSH",
    "HadGEM_PP"]
