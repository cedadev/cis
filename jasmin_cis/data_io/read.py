'''
Module for reading data.
'''

import read_gridded,read_ungridded

def read_all_variables_from_file(filename):
    '''
    Read all the variables from a file.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.
    
    args:
        filenames:   The filenames of the files to read
        
    returns:
        A list of variable objects describing the variables
    '''
    from jasmin_cis.exceptions import CISError
    from pyhdf.error import HDF4Error
    try:
        file_variables = read_gridded.get_file_variables(filename)
    except RuntimeError:
        try:
            file_variables = read_ungridded.get_file_variables(filename)
        except HDF4Error as e:
            raise CISError(e)
    
    return file_variables

        
def read_variable_from_files(filenames, variable):
    '''
    Read a specific variable from a list of files
    Files can be either gridded or ungridded but not a mix of both.
    First tries to read data as gridded, if that fails, tries as ungridded.
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        The specified data with unnecessary dimensions removed    
    '''
    from iris.exceptions import IrisError
    from jasmin_cis.exceptions import CISError
    
    try:
        data = read_gridded.read(filenames, variable)
    except (IrisError, ValueError) as e:
        # Unable to create Cube, trying Ungridded data instead
        try:
            data = read_ungridded.read(filenames, variable)
        except CISError as e:
            raise e
    return data


def read_file_coordinates(filename):
    '''
    Read the coordinates from a file
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.
  
    args:
        filename:   The filename of the files to read
        
    returns:
        A list of HyperPoints  
    '''
    from jasmin_cis.exceptions import CISError
    
    try:
        coords = read_gridded.get_file_coordinates_points(filename)
    except:
        # Unable to read netcdf file, trying Ungridded data
        try:
            coords = read_ungridded.get_file_coordinates_points(filename)
        except CISError as ug_e:
            raise ug_e
       
    return coords

