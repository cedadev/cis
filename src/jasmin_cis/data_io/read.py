'''
Module for reading data
'''

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
        
def read_variable(filenames, variable):
    '''
    Read data from a NetCDF file
    Used for both gridded and ungridded data
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        A cube containing the specified data with unnecessary dimensions removed    
    '''
    from read_ungridded import read_ungridded_data
    from read_gridded import read_gridded_data_file_variable
    from iris.exceptions import IrisError
    from jasmin_cis.exceptions import CISError
    try:
        data = read_gridded_data_file_variable(filenames, variable)
    except IrisError as e:
        # Unable to create Cube, trying Ungridded data
        try:
            data = read_ungridded_data(filenames, variable)
        except CISError:
            # This is not yet implemented so just rethrows the original
            #  iris error
            raise e
        except IOError:
            # This can't be thrown yet as it's not implemented
            pass
    return data
