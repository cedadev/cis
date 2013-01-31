"""
Module containing NetCDF file utility functions
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


def unpack_cube(cube): 
    '''
    To be commented
    ''' 
    from iris.cube import Cube
    import iris.plot as iplt
    import iris

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
        return { "data": cube.data, "x" : cube.x, "y" : cube.y }
