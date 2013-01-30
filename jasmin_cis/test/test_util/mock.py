'''
Module for creating mock, dummies and fakes
'''
def make_dummy_2d_cube():
    '''
        Makes a dummy cube filled with random datapoints of shape 19x36
    '''
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(0, 360, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return cube

def make_square_3x3_2d_cube():
    '''
        Makes a well defined cube of shape 3x3 with data as follows
        array([[1,2,3],
               [4,5,6],
               [7,8,9],
               [10,11,12],
               [13,14,15]])
        and coordinates in latitude:
            array([ -10, -5, 0, 5, 10 ])
        longitude:
            array([ -5, 0, 5 ])
            
        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    '''
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(np.arange(-10, 11, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15)+1,(5,3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return cube

def make_dummy_1d_cube():
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    cube = Cube(numpy.random.rand(19), dim_coords_and_dims=[(latitude, 0)])
    
    return cube

def get_random_1d_point():
    '''
        Creates a hyper point at some random point along the Grenwich meridian (lon = 0.0)
    '''
    import random
    from jasmin_cis.hyperpoint import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0))

def get_random_2d_point():
    '''
        Creates a random point on the surface of the globe
    '''
    import random
    from jasmin_cis.hyperpoint import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0), random.randrange(0.0, 360.0))

def get_random_3d_point():
    '''
        Creates a random point in 3d space upto 100km above the surface of the globe
    '''
    import random
    from jasmin_cis.hyperpoint import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0), random.randrange(0.0, 360.0), random.randrange(0.0, 100.0))

def make_dummy_1d_points_list(num):
    '''
        Create a list of 1d points 'num' long
    '''
    return [ get_random_1d_point() for i in xrange(0,num) ]

def make_dummy_2d_points_list(num):
    '''
        Create a list of 2d points 'num' long
    '''
    return [ get_random_2d_point() for i in xrange(0,num) ]
        
def make_dummy_1d_ungridded_data():
    pass

def make_dummy_2d_ungridded_data():
    pass

