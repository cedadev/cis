'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
import logging

types = {'int16': "i2",
         'int32': "i4",
         'int64': "i8",
         'float32': "f4",
         'float64': "f8"}

index_name = 'pixel_number'


def __add_metadata(var, data):
    if data.standard_name: var.standard_name = data.standard_name
    if data.units: var.units = str(data.units)
    if data.long_name: var.long_name = data.long_name
    if data.metadata.range : var.valid_range = data.metadata.range
    if data.metadata.missing_value : var.missing_value = data.metadata.missing_value
    if data.metadata.calendar : var.calendar = data.metadata.calendar
    if data.metadata.history : var.history = data.metadata.history
    var.shape = data.shape
    return var


def __get_missing_value(coord):
    f = coord.metadata.missing_value
    if not f and f !=0:
        f = None
    return f


def __create_variable(nc_file, data):
    from jasmin_cis.exceptions import InconsistentDimensionsError
    logging.info("Creating variable: " + data.standard_name + "("+index_name+")" + " " + types[str(data.data.dtype)])
    var = nc_file.createVariable(data.standard_name, types[str(data.data.dtype)], index_name, fill_value=__get_missing_value(data))
    var = __add_metadata(var, data)
    try:
        var[:] = data.data.flatten()
    except IndexError as e:
        raise InconsistentDimensionsError(str(e)+"\nInconsistent dimensions in output file, unable to write "
                                                 ""+data.standard_name+" to file (it's shape is "+str(data.shape)+").")

    return var


def __create_index(nc_file, length):
    import numpy as np
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
