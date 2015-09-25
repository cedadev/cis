"""
Module with standard cis Data Products in it
"""

from AProduct import AProduct
from abstract_NetCDF_CF import abstract_NetCDF_CF
from products import NetCDF_Gridded, Aeronet, ASCII_Hyperpoints, cis, default_NetCDF
from cloudsat import CloudSat
from gridded_NetCDF import abstract_NetCDF_CF_Gridded, NetCDF_Gridded
from NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from MODIS import MODIS_L2, MODIS_L3
from caliop import abstract_Caliop, Caliop_L1, Caliop_L2
from CCI import Aerosol_CCI, Cloud_CCI
from HadGEM import HadGEM_PP, HadGEM_CONVSH

# list of all data products
__all__ = [
    "AProduct",
    "NCAR_NetCDF_RAF",
    "MODIS_L2",
    "MODIS_L3",
    "Caliop_L1",
    "Caliop_L2",
    "CCI",
    "Cloud_CCI",
    "Aerosol_CCI",
    "abstract_NetCDF_CF",
    "default_NetCDF",
    "Aeronet",
    "ASCII_Hyperpoints",
    "cis",
    "HadGEM_CONVSH",
    "HadGEM_PP"]
