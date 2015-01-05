'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
import logging

types = {'int8': 'i1',
         'int16': "i2",
         'int32': "i4",
         'int64': "i8",
         'uint8': 'u1',
         'uint16': "u2",
         'uint32': "u4",
         'uint64': "u8",
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

    return var


def __get_missing_value(coord):
    f = coord.metadata.missing_value
    if not f and f !=0:
        f = None
    return f


def __create_variable(nc_file, data, prefer_standard_name=False):
    """Creates and writes a variable to a netCDF file.
    :param nc_file: netCDF file to which to write
    :param data: LazyData for variable to write
    :param prefer_standard_name: if True, use the standard name of the variable if defined,
           otherwise use the variable name
    :return: created netCDF variable
    """
    from jasmin_cis.exceptions import InconsistentDimensionsError
    name = None
    if (data.metadata._name is not None) and (len(data.metadata._name) > 0):
        name = data.metadata._name
    if (name is None) or prefer_standard_name:
        if (data.metadata.standard_name is not None) and (len(data.metadata.standard_name) > 0):
            name = data.metadata.standard_name
    logging.info("Creating variable: " + name + "("+index_name+")" + " " + types[str(data.data.dtype)])
    if name not in nc_file.variables:
        var = nc_file.createVariable(name, types[str(data.data.dtype)], index_name, fill_value=__get_missing_value(data))
        var = __add_metadata(var, data)
        try:
            var[:] = data.data.flatten()
        except IndexError as e:
            raise InconsistentDimensionsError(str(e)+"\nInconsistent dimensions in output file, unable to write "
                                                     ""+data.standard_name+" to file (it's shape is "+str(data.shape)+").")
        return var
    else:
        return nc_file.variables[name]


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

    :param data_object:
    :param filename:
    :return:
    """
    write_coordinate_list(data_object.coords(), filename)
    add_data_to_file(data_object, filename)


def write_coordinates(coords, filename):
    """Writes coordinates to a netCDF file.

    :param coords: UngriddedData or UngriddedCoordinates object for which the coordinates are to be written
    :param filename: file to which to write
    """
    coord_list = coords.coords()
    write_coordinate_list(coord_list, filename)


def write_coordinate_list(coord_list, filename):
    """Writes coordinates to a netCDF file.

    :param coord_list: list of Coord objects
    :param filename: file to which to write
    """
    netcdf_file = Dataset(filename, 'w', format="NETCDF4")
    try:
        length = len(coord_list[0].data.flatten())
    except AttributeError:
        length = len(coord_list[0].points.flatten())
    index_dim = __create_index(netcdf_file, length)
    for coord in coord_list:
        __create_variable(netcdf_file, coord, prefer_standard_name=True)
    netcdf_file.close()


def add_data_to_file(data_object, filename):
    """

    :param data_object:
    :param filename:
    :return:
    """
    netcdf_file = Dataset(filename, 'a', format="NETCDF4")
    var = __create_variable(netcdf_file, data_object, prefer_standard_name=False)
    netcdf_file.close()
