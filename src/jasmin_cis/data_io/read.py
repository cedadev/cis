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
        
def read_gridded_data_file_variable(filenames, variable):
    '''
    Read gridded data from a NetCDF file
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        A cube containing the specified data with unnecessary dimensions removed    
    '''
    from jasmin_cis.exceptions import InvalidVariableError
    import iris
    
    var_constraint = iris.AttributeConstraint(name=variable)
    # Create an Attribute constraint on the name Attribute for the variable given
    
    try:
        cube = iris.load_cube(filenames, var_constraint)
    except iris.exceptions.ConstraintMismatchError:
        print "Variable not found: "+variable
        print "Try one of these instead: "
        for variable in get_netcdf_file_variables(filenames[0]):
            print variable
        raise InvalidVariableError
    
    sub_cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    #  Ensure that there are no extra dimensions which can confuse the plotting.
    # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about 
    #  the dimension whose length is one. The above list comprehension would return a cube of 
    #  shape (145, 165)
    
    return sub_cube
        
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
    from read_ungridded import UngriddedData, read_ungridded_data
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
        