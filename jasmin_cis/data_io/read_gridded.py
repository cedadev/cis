'''
Module for ungridded data utilities. Gridded data is generally
stored in cubes
'''

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
        raise InvalidVariableError("Variable not found: " + variable +
                                   "\nTo see a list of variables run: cis info " + filenames[0] + " -h")
    
    sub_cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    #  Ensure that there are no extra dimensions which can confuse the plotting.
    # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about 
    #  the dimension whose length is one. The above list comprehension would return a cube of 
    #  shape (145, 165)
    
    return sub_cube


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