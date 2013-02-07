"""
Module containing NetCDF file reading functions
"""
def get_netcdf_file_variables(filename):
    '''
    Get all the variables from a NetCDF file
    
    args:
        filename: The filename of the file to get the variables from
    
    returns:
        An OrderedDict containing the variables from the file
    '''
    from netCDF4 import Dataset    
    f = Dataset(filename)
    return f.variables


def read(filename, usr_variables=None, datadict=None):
    """
    Reads Variables from a NetCDF file into a dictionary.

    Returns:
        A dictionary containing data for requested variables.
        Missing data is masked as a masked numpy array

    Arguments:
        filename    -- The name (with path) of the NetCDF file to read.
        names       -- A sequence of variable (dataset) names to read from the
                       file (default None, causing all variables to be read).
                       The names must appear exactly as in in the NetCDF file.
        datadic     -- Optional dictionary to add data to, otherwise a new, empty
                       dictionary is created

    """
    from netCDF4 import Dataset
    datafile = Dataset(filename)

    # List of required variable names.
    if usr_variables is None:
        usr_variables = datafile.variables.keys()
    if not isinstance(usr_variables,list): usr_variables = [ usr_variables ]

    # Create dictionary to hold data arrays for returning.
    if datadict is None:
        datadict = {}

    # Get data.
    for usr_variable in usr_variables:
        try:
            datadict[usr_variable] = datafile.variables[usr_variable]
        except:
            # ignore variable that failed
            pass

    return datadict

def get_metadata(var):
    '''
    Retrieves all metadata

    @param var: the Variable to read metadata from
    @return:
    '''
    dict = {}
    dict['info'] = str(var)
    # A list of dimensions the variable is a function of
    dict['dimensions'] = var.dimensions
    # A dictionary of the attributes on the variable, including units, standard_name, long_name
    dict['attributes'] = vars(var)

    return dict

def get_data(var, calipso_scaling=False):
    """
    Reads raw data from a NetCDF.Variable instance.

    Returns:
        A numpy maskedarray. Missing values are False in the mask.

    Arguments:
        var        -- The specific Variable instance to read

    """
    from utils import create_masked_array_for_missing_data
    data = var[:]

    # Missing data.
    missing_val = getattr(var, '_FillValue', None)
    data = create_masked_array_for_missing_data(data, missing_val)

    return data
