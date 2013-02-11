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

def read_many_files(filenames, usr_variable, dim=None):
    """
    Reads a single Variable from many NetCDF files.

        @param filenames: A list of NetCDF filenames to read, or a string with wildcards.
        @param usr_variable: A variable (dataset) name to read from the
                       files. The name must appear exactly as in in the NetCDF file.
        @param dim: The name of the dimension on which to aggregate the data. None is the default
                     which tries to aggregate over the unlimited dimension
        @return: A Variable instance constructed from all of the input files
    """
    from netCDF4 import MFDataset
    from jasmin_cis.exceptions import InvalidVariableError
    datafile = MFDataset(filenames, aggdim=dim)

    # Get data.
    try:
        data = datafile.variables[usr_variable]
    except:
        raise InvalidVariableError

    return data


def read(filename, usr_variable):
    """
    Reads a Variable from a NetCDF file

        @param filename: The name (with path) of the NetCDF file to read.
        @param usr_variable: A variable (dataset) name to read from the
                       files. The name must appear exactly as in in the NetCDF file.
        @return: A Varaibale instance constructed from  the input file

    """
    from netCDF4 import Dataset
    from jasmin_cis.exceptions import InvalidVariableError
    datafile = Dataset(filename)

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
    # Use class instead of dictionary

    metadata = Metadata()
    metadata.copy_attributes_into(vars(var))


    #metadata = {}
    #metadata['info'] = str(var)
    # A list of dimensions the variable is a function of
    #metadata['dimensions'] = var.dimensions
    # A dictionary of the attributes on the variable, including units, standard_name, long_name
    #metadata['attributes'] = vars(var)

    return metadata

def get_data(var, calipso_scaling=False):
    """
    Reads raw data from a NetCDF.Variable instance.

        @param var: The specific Variable instance to read
        @return:  A numpy maskedarray. Missing values are False in the mask.
    """
    from utils import create_masked_array_for_missing_data
    data = var[:]

    # Missing data.
    missing_val = getattr(var, '_FillValue', None)
    data = create_masked_array_for_missing_data(data, missing_val)

    return data
