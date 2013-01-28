'''
Module for reading data.
'''
from jasmin_cis.data_io.hdf import get_hdf_VD_file_variables

def read_all_variables_from_file(filename):
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

        
def read_variable_from_files(filenames, variable):
    '''
    Read data from a NetCDF file
    Used for both gridded and ungridded data
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        The specified data with unnecessary dimensions removed    
    '''
    from read_ungridded import read_ungridded_data
    from read_gridded import read_gridded_data_file_variable
    from iris.exceptions import IrisError
    from jasmin_cis.exceptions import CISError
    
    try:
        data = read_gridded_data_file_variable(filenames, variable)
    except (IrisError, ValueError) as e:
        # Unable to create Cube, trying Ungridded data instead
        try:
            data = read_ungridded_data(filenames, variable)
        except CISError as e:
            raise e
    return data

def read_file_coordinates(filename):
    '''
    Read coordinates from a file
    
    args:
        filename:   The filename of the files to read
        
    returns:
        A list of HyperPoints  
    '''
    from read_ungridded import get_netcdf_file_coordinates_points
    from read_gridded import get_netcdf_file_coordinates
    from iris.exceptions import IrisError
    from jasmin_cis.exceptions import CISError
    
    try:
        coords = get_netcdf_file_coordinates(filename)
    except:
        # Unable to read netcdf file, trying Ungridded data
        try:
            coords = get_netcdf_file_coordinates_points(filename)
        except CISError as ug_e:
            raise ug_e
       
    return coords

