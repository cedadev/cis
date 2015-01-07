"""
Module with standard cis Data Products in it
"""

#list of all data products
__all__ = ["NCAR_NetCDF_RAF", "MODIS", "caliop" "products"]

from products import *
from NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from MODIS import MODIS_L2, MODIS_L3
from caliop import abstract_Caliop, Caliop_L1, Caliop_L2
