'''
Module for reading data.
'''
from jasmin_cis.data_io.hdf import get_hdf_VD_file_variables

def read_file_variables(filename):
    '''
    Read data from a NetCDF file
    Used for both gridded and ungridded data
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        A cube containing the specified data with unnecessary dimensions removed    
    '''
    from hdf import get_hdf_SD_file_variables
    from read_gridded import get_netcdf_file_variables
    
    try:
        file_variables = get_netcdf_file_variables(filename)
    except RuntimeError:
        file_variables = get_hdf_SD_file_variables(filename)
        file_variables.update(get_hdf_VD_file_variables(filename))
    
    return file_variables

        
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
    except (IrisError, ValueError) as e:
        # Unable to create Cube, trying Ungridded data
        try:
            data = read_ungridded_data(filenames, variable)
        except CISError as ug_e:
            # This is not yet implemented so just rethrows the original
            #  iris error
            raise ug_e
    return data
