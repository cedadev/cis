"""
Module containing NetCDF file reading functions
"""
from jasmin_cis.utils import listify


def get_netcdf_file_attributes(filename):
    """
    Get all the global attributes from a NetCDF file

    :param filename: The filename of the file to get the variables from
    :return: a dictionary of attributes and their values
    """

    from netCDF4 import Dataset
    f = Dataset(filename)

    return f.__dict__


def get_netcdf_file_variables(filename, exclude_coords=False):
    """
    Get all the variables from a NetCDF file
    
    :param filename: The filename of the file to get the variables from
    :param exclude_coords: Exclude coordinate variables
    :return: An OrderedDict containing the variables from the file
    """
    from netCDF4 import Dataset    
    f = Dataset(filename)
    variables = f.variables
    if exclude_coords:
        for var in f.dimensions:
            try:
                del variables[var]
            except KeyError:
                pass
    return variables


def remove_variables_with_non_spatiotemporal_dimensions(variables, spatiotemporal_var_names):
    """
    Remove from a list of netCDF variables any which have dimensionality which is not in an approved list
    of valid spatial or temporal dimensions (e.g. sensor number, pseudo dimensions). CIS currently does not
    support variables with this dimensionality and will fail if they are used.
    :param variables: Dictionary of netCDF variable names : Variable objects
    :param spatiotemporal_var_names: List of valid spatiotemporal dimensions.
    :return: None
    """
    if spatiotemporal_var_names is not None:
        for var in variables.keys():
            for dim in variables[var].dimensions:
                if dim not in spatiotemporal_var_names:
                    del variables[var]
                    break


def read_attributes_and_variables_many_files(filenames):
    """
    Read attributes and variables from a netcdf file collection
    It uses first file as the master from which it reads the data
    :param filenames:  A list of NetCDF filenames to read, or a string with wildcards.
    :return: a dictionary of attributes and their values, a list of variable names, dictionary of variables
    """
    import glob
    from netCDF4 import Dataset

    if len(filenames) == 0:
        raise IOError("No filenames in filename list to read")

    files = glob.glob(filenames[0])
    if len(files) == 0:
        raise IOError("No filenames in filename list to read")

    try:
        datafile = Dataset(files[0])
    except RuntimeError as e:
        raise IOError(e)

    variable_dimensions = {name: variable.dimensions for name, variable in datafile.variables.items()}
    return datafile.__dict__, datafile.variables.keys(), variable_dimensions


def read_many_files(filenames, usr_variables, dim=None):
    """
    Reads a single Variable from many NetCDF files.

        :param filenames: A list of NetCDF filenames to read, or a string with wildcards.
        :param usr_variables: A list of variable (dataset) names to read from the
                       files. The names must appear exactly as in in the NetCDF file.
        :param dim: The name of the dimension on which to aggregate the data. None is the default
                     which tries to aggregate over the unlimited dimension
        :return: A list of variable instances constructed from all of the input files
    """
    from netCDF4 import MFDataset
    from jasmin_cis.exceptions import InvalidVariableError

    usr_variables = listify(usr_variables)

    try:
        datafile = MFDataset(filenames, aggdim=dim)
    except RuntimeError as e:
        raise IOError(e)

    data = {}
    for variable in usr_variables:
        # Get data.
        try:
            data[variable] = datafile.variables[variable]
        except:
            raise InvalidVariableError('Variable {} not found in file {}.'.format(variable, filenames))

    return data


def read_many_files_individually(filenames, usr_variables):
    """
    Read multiple Variables from many NetCDF files manually - i.e. not with MFDataset as this doesn't alays work

        :param filenames: A list of NetCDF filenames to read, or a string with wildcards.
        :param usr_variables: A list of variable (dataset) names to read from the
                       files. The names must appear exactly as in in the NetCDF file.
        :return: A dictionary of lists of variable instances constructed from all of the input files with the variable
                    name as the key
    """
    from jasmin_cis.utils import add_element_to_list_in_dict

    usr_variables = listify(usr_variables)

    var_data = {}

    for filename in filenames:

        var_dict = read(filename, usr_variables)
        for var in var_dict.keys():
            add_element_to_list_in_dict(var_data, var, var_dict[var])

    return var_data


def read(filename, usr_variables):
    """
    Reads a Variable from a NetCDF file

        :param filename: The name (with path) of the NetCDF file to read.
        :param usr_variables: A variable (dataset) name to read from the
                       files. The name must appear exactly as in in the NetCDF file.
        :return: A Variable instance constructed from  the input file

    """
    from netCDF4 import Dataset
    from jasmin_cis.exceptions import InvalidVariableError

    usr_variables = listify(usr_variables)

    try:
        datafile = Dataset(filename)
    except RuntimeError as e:
        raise IOError(str(e))

    data = {}
    for variable in usr_variables:
        # Get data.
        try:
            data[variable] = datafile.variables[variable]
        except:
            raise InvalidVariableError(variable+' could not be found in '+filename)

    return data


def get_metadata(var):
    '''
    Retrieves all metadata

    :param var: the Variable to read metadata from
    :return: A metadata object
    '''
    from jasmin_cis.data_io.ungridded_data import Metadata

    standard_name = getattr(var, 'standard_name', "")
    missing_value = find_missing_value(var)
    long_name = getattr(var, 'long_name', "")
    units = getattr(var, 'units', "")

    history = getattr(var, "history", "")
    shape = getattr(var, "shape", None)
    if shape is None:
        try:
            shape = (var._recLen[0],)
        except AttributeError:
            shape = ()

    metadata = Metadata(
        var._name,
        standard_name,
        long_name,
        units=units,
        missing_value=missing_value,
        shape=shape,
        history=history)

    return metadata


def find_missing_value(var):
    try:
        missing_value = var.missing_value
    except AttributeError:
        try:
            missing_value = var._FillValue
        except AttributeError:
            missing_value = None
    return missing_value


def get_data(var, calipso_scaling=False):
    """
    Reads raw data from a NetCDF.Variable instance.

        :param var: The specific Variable instance to read
        :return:  A numpy maskedarray. Missing values are False in the mask.
    """
    from jasmin_cis.utils import create_masked_array_for_missing_data
    # Note that this will automatically apply any specified scalings and
    #  return a masked array based on _FillValue
    data = var[:]

    return data
