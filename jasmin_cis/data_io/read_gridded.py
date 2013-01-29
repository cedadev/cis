'''
Module for ungridded data utilities. Gridded data is generally
stored in cubes
'''
import iris.plot as iplt
import iris
from iris.cube import Cube
from collections import namedtuple

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

def unpack_cube(cube): 
    '''
    To be commented
    ''' 
    if type(cube) is Cube:
        no_of_dims = len(cube.shape)
        import numpy as np
        from mpl_toolkits.basemap import addcyclic
        
        plot_defn = iplt._get_plot_defn(cube, iris.coords.POINT_MODE, ndims = no_of_dims)
        data = cube.data #ndarray
        if plot_defn.transpose:
            data = data.T
        
        if no_of_dims == 1:
            u_coord, = plot_defn.coords
            if u_coord:
                x = u_coord.points
            else:
                x = np.arange(data.shape[0])
            y = None
        elif no_of_dims == 2:
            # Obtain U and V coordinates
            v_coord, u_coord = plot_defn.coords
            if u_coord:
                u = u_coord.points
            else:
                u = np.arange(data.shape[1])
            if v_coord:
                v = v_coord.points
            else:
                v = np.arange(data.shape[0])
            
        if plot_defn.transpose:
            u = u.T
            v = v.T
        
        if no_of_dims == 2:
            data, u = addcyclic(data, u)    
            x, y = np.meshgrid(u, v)
        
        return { "data": data, "x" : x, "y" : y }
    else:
        return cube

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

# Define a named tuple for storing vectors of coordinates from gridded data

GriddedCoordsT = namedtuple('GriddedCoords',['lat','lon','alt','t'])

def get_netcdf_file_coordinates(filename):
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

def get_netcdf_file_coordinates_points(filename):
    from jasmin_cis.col import HyperPoint
        
    dims = get_netcdf_file_coordinates(filename)
    
    # Pack the data into a list of x,y, val points to be passed to col
    points = []    
    
    for lat_p in dims.lat[:]:
        for lon_p in dims.lon[:]:
            for alt_p in dims.alt[:]:
                for time_p in dims.time[:]:
                    points.append(HyperPoint(lat_p,lon_p,alt_p,time_p))

    return points
