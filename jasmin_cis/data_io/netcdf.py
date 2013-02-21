"""
Module containing NetCDF file reading functions
"""


def get_netcdf_file_variables(filename):
    '''
    Get all the variables from a NetCDF file
    
    @param filename: The filename of the file to get the variables from
    @return: An OrderedDict containing the variables from the file
    '''
    from netCDF4 import Dataset    
    f = Dataset(filename)
    return f.variables

def read_many_files(filenames, usr_variables, dim=None):
    """
    Reads a single Variable from many NetCDF files.

        @param filenames: A list of NetCDF filenames to read, or a string with wildcards.
        @param usr_variables: A list of variable (dataset) names to read from the
                       files. The names must appear exactly as in in the NetCDF file.
        @param dim: The name of the dimension on which to aggregate the data. None is the default
                     which tries to aggregate over the unlimited dimension
        @return: A list of variable instances constructed from all of the input files
    """
    from netCDF4 import MFDataset
    from jasmin_cis.exceptions import InvalidVariableError

    if not isinstance(usr_variables,list):
        usr_variables = [usr_variables]

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
            raise InvalidVariableError

    return data


def read(filename, usr_variable):
    """
    Reads a Variable from a NetCDF file

        @param filename: The name (with path) of the NetCDF file to read.
        @param usr_variable: A variable (dataset) name to read from the
                       files. The name must appear exactly as in in the NetCDF file.
        @return: A Variable instance constructed from  the input file

    """
    from netCDF4 import Dataset
    from jasmin_cis.exceptions import InvalidVariableError

    try:
        datafile = Dataset(filename)
    except RuntimeError as e:
        raise IOError(str(e))

    try:
        data = datafile.variables[usr_variable]
    except:
        raise InvalidVariableError

    return data

def get_metadata(var):
    '''
    Retrieves all metadata

    @param var: the Variable to read metadata from
    @return: A metadata object
    '''
    from ungridded_data import Metadata
    try:
        standard_name = var.standard_name
    except AttributeError:
        standard_name = ""
    try:
        missing_value = var.missing_value
    except AttributeError:
        try:
            missing_value = var._FillValue
        except AttributeError:
            missing_value = ""
    try:
        shape=(var._recLen[0],)
    except AttributeError:
        shape = ()
    try:
        long_name = var.long_name
    except AttributeError:
        long_name = ""
    metadata = Metadata(var._name, standard_name, long_name, units=var.units, missing_value=missing_value, shape=shape)

    return metadata

def get_data(var, calipso_scaling=False):
    """
    Reads raw data from a NetCDF.Variable instance.

        @param var: The specific Variable instance to read
        @return:  A numpy maskedarray. Missing values are False in the mask.
    """
    from utils import create_masked_array_for_missing_data
    data = var[:] # Note that this will automatically apply any specified scalings

    # Missing data.
    missing_val = getattr(var, '_FillValue', None)
    scale_factor = getattr(var, 'scale_factor', 1)
    if missing_val is not None:
        # Fill value needs to be scaled in order to work
        missing_val = missing_val * scale_factor
    data = create_masked_array_for_missing_data(data, missing_val)

    return data
