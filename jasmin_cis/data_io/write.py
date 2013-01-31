'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset


def write_to_file(data_object, filename):
    netcdf_file = Dataset(filename, 'w')
    netcdf_file.close()
    
write_to_file(None, "test_netcdf_file")