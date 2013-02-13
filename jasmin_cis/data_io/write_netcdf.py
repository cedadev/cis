'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
import numpy as np

types = {float: "f",
         'int16': "i",
         'int64': "i",
         'float64': "f"}

index_name = 'pixel_number'

def __add_metadata(var, data):
    if data._metadata.standard_name: var.standard_name = data._metadata.standard_name
    if data._metadata.units: var.units = data._metadata.units
    if data._metadata.long_name: var.long_name = data._metadata.long_name
    if data._metadata.range : var.valid_range = data._metadata.range
    return var

def __get_missing_value(coord):
    f = coord._metadata.missing_value
    if not f and f !=0:
        f = None
    return f

#def __create_dimensions(nc_file, coords):
#    dimensions = ()
#    first_coord = True
#    for coord in coords:
#        if first_coord:
#            dimension = nc_file.createDimension(coord.name(), len(coord.data))
#            dimensions = dimensions + (coord.name(),)
#            first_coord = False
#        var = nc_file.createVariable(coord.name(), types[type(coord.data[0])], dimension._name, fill_value=__get_missing_value(coord))
#        var = __add_metadata(var, coord)
#        var[:] = coord.data
#
#    return dimensions

def __create_variable(nc_file, data):
    var = nc_file.createVariable(data.name(), types[str(data.data.dtype)], index_name, fill_value=__get_missing_value(data))
    var = __add_metadata(var, data)
    var[:] = data.data.flatten()

    return var

def __create_index(nc_file, length):
    dimension = nc_file.createDimension(index_name, length)
    dimensions = ( index_name, )
    var = nc_file.createVariable(index_name, np.int32, dimensions)

    var.valid_range = (0, length)
    var[:] = np.arange(length)

    return dimensions


def write(data_object, filename):
    """

    @param data_object:
    @param filename:
    @return:
    """
    write_coordinates(data_object.coords(), filename)
    add_data_to_file(data_object, filename)

def write_coordinates(coords, filename):
    """

    @param coords:
    @param filename:
    @return:
    """
    netcdf_file = Dataset(filename, 'w', format="NETCDF4_CLASSIC")
    index_dim = __create_index(netcdf_file, len(coords[0].data.flatten()))
    for data in coords:
        coord = __create_variable(netcdf_file, data)
    netcdf_file.close()

def add_data_to_file(data_object, filename):
    """

    @param data_object:
    @param filename:
    @return:
    """
    netcdf_file = Dataset(filename, 'a', format="NETCDF4_CLASSIC")
    var = __create_variable(netcdf_file, data_object)
    netcdf_file.close()
