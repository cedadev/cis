# DataReader.py
# Created by PARD on 14th Jan 2013
# Copyright TODO
#
# Class for reading data

def read_gridded_data_file_variable(filename, variable):
    """
    
    
    """
    from cis.exceptions import InvalidVariableError
    import iris
    from netCDF4 import Dataset
    
    var_constraint = iris.AttributeConstraint(name=variable)
    # Create an Attribute constraint on the name Attribute for the variable given
    
    try:
        cube = iris.load_cube(filename, var_constraint)
    except iris.exceptions.ConstraintMismatchError:
        print "Variable not found: "+variable
        print "Try one of these instead:"
        f = Dataset(filename)
        for variable in f.variables:
            print "  "+variable
        raise InvalidVariableError
    
    sub_cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    #  Ensure that there are no extra dimensions which can confuse the plotting.
    # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about 
    #  the dimension whose length is one. The above list comprehension would return a cube of 
    #  shape (145, 165)
    
    return sub_cube
        
def read_variable(filenames, variable):
    """
    
    
    
    """
    from cis.data_io.read_ungridded import UngriddedData, read_ungridded_data
    from iris.exceptions import IrisError
    try:
        data = read_gridded_data_file_variable(file, variable)
    except IrisError:
        print "Unable to create Cube, trying Ungridded data"
        data = read_ungridded_data(file, variable)
    return data
        