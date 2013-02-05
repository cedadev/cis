'''
Module for reading gridded data
Assumes gridded data are in NetCDF format
'''
import iris
from collections import namedtuple

GriddedCoordsT = namedtuple('GriddedCoords',['lat','lon','alt','t'])

def get_file_variables(filename):
    '''
    Get all variables from a file containing gridded data
    
    args:
        filename: The filename of the file to get the variables from
    
    '''
    from netcdf import get_netcdf_file_variables
    return get_netcdf_file_variables(filename)

# Define a named tuple for storing vectors of coordinates from gridded data

def get_file_coordinates(filename):
    '''
    Get all of the coordinate variables from a NetCDF file
    
    args:
        filename: The filename of the file to get the variables from
    
    returns:
        A GriddedCoordsT named tuple.
    '''
    from netCDF4 import Dataset    
    f = Dataset(filename)
    try:
        lat = f.variables['latitude']
    except KeyError:
        lat=[]
    try:
        lon = f.variables['longitude']
    except KeyError:
        lon=[]
    try:
        alt = f.variables['altitude']
    except KeyError:
        alt=[]
    try:
        time = f.variables['t']
    except KeyError:
        time=[]
        
    return GriddedCoordsT(lat,lon,alt,time)

def get_file_coordinates_points(filename):

    from jasmin_cis.data_io.hyperpoint import HyperPoint
        
    dims = get_file_coordinates(filename)
    
    # Pack the data into a list of x,y, val points to be passed to col
    points = []    
    
    for lat_p in dims.lat[:]:
        for lon_p in dims.lon[:]:
            for alt_p in dims.alt[:]:
                for time_p in dims.time[:]:
                    points.append(HyperPoint(lat_p,lon_p,alt_p,time_p))

    return points

def read(filenames, variable):
    '''
    Read gridded data for a given variable over multiple files.
    
    args:
        filenames:   The filenames of the files to read
        variable:    The variable to read from the files
        
    returns:
        A cube containing the specified data with unnecessary dimensions removed    
    '''
    from jasmin_cis.exceptions import InvalidVariableError
    
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
