"""
Module for writing data to NetCDF files
"""
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

index_name = 'obs'


def __add_metadata(var, data):
    if data.standard_name:
        var.standard_name = data.standard_name
    if data.units:
        var.units = str(data.units)
    if data.long_name:
        var.long_name = data.long_name
    if data.metadata.missing_value:
        var.missing_value = data.metadata.missing_value
    if hasattr(data.units, 'calendar') and data.units.calendar:
        var.calendar = data.units.calendar
    if data.metadata.history:
        var.history = data.metadata.history
    for name, value in data.attributes.items():
        setattr(var, name, value)
    for name, value in data.metadata.misc.items():
        if name not in var.ncattrs():
            try:
                setattr(var, name, value)
            except ValueError:
                logging.warning("Invalid value ({}) for {} attribute. "
                                "Attribute not saved to {}.".format(value, name, var.name))
    return var


def __get_missing_value(coord):
    f = coord.metadata.missing_value
    if not f and f != 0:
        f = None
    return f


def sizeof_fmt(num, suffix='B'):
    """
    Return a human readable size from an integer number of bytes

    From http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param int num: Number of bytes
    :param str suffix: Little or big B
    :return str: Formatted human readable size
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def __check_disk_space(filepath, data):
    """
    Warn if there is insufficient disk space to write the data to the filapath - if the OS supports it
    :param str filepath: Path of file to write
    :param ndarray data: Numpy array of data to write
    :return: None
    """
    try:
        from os import statvfs
        stats = statvfs(filepath)
    except (ImportError, OSError):
        logging.debug("Unable to determine free disk space on this OS.")
    else:
        # available space is the number of available blocks times the fundamental block size
        available = stats.f_bavail * stats.f_frsize
        if available < data.nbytes:
            logging.warning("Free disk space at {path} is {free}, but the array being saved is {size}."
                            .format(path=filepath, free=sizeof_fmt(available), size=sizeof_fmt(data.data.nbytes)))


def __create_variable(nc_file, data, prefer_standard_name=False):
    """Creates and writes a variable to a netCDF file.
    :param nc_file: netCDF file to which to write
    :param data: LazyData for variable to write
    :param prefer_standard_name: if True, use the standard name of the variable if defined,
           otherwise use the variable name
    :return: created netCDF variable
    """
    from cis.exceptions import InconsistentDimensionsError

    name = None
    if (data.metadata._name is not None) and (len(data.metadata._name) > 0):
        name = data.metadata._name
    if (name is None) or prefer_standard_name:
        if (data.metadata.standard_name is not None) and (len(data.metadata.standard_name) > 0):
            name = data.metadata.standard_name
    out_type = types[str(data.data.dtype)]
    logging.info("Creating variable: {name}({index}) {type}".format(name=name, index=index_name, type=out_type))
    if name not in nc_file.variables:
        # Generate a warning if we have insufficient disk space
        __check_disk_space(nc_file.filepath(), data.data)
        var = nc_file.createVariable(name, datatype=out_type, dimensions=index_name,
                                     fill_value=__get_missing_value(data))
        var = __add_metadata(var, data)
        try:
            var[:] = data.data.flatten()
        except IndexError as e:
            raise InconsistentDimensionsError(str(e) + "\nInconsistent dimensions in output file, unable to write "
                                                       "{} to file (it's shape is {}).".format(data.name(), data.shape))
        except:
            logging.error("Error writing data to disk.")
            raise
        return var
    else:
        return nc_file.variables[name]


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
    _ = netcdf_file.createDimension(index_name, length)
    for coord in coord_list:
        __create_variable(netcdf_file, coord, prefer_standard_name=True)
    netcdf_file.close()


def add_data_to_file(data_object, filename):
    """

    :param data_object:
    :param filename:
    :return:
    """
    from cis import __version__
    netcdf_file = Dataset(filename, 'a', format="NETCDF4")
    var = __create_variable(netcdf_file, data_object, prefer_standard_name=False)
    netcdf_file.source = "CIS" + __version__
    netcdf_file.close()
