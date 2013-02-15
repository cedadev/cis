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
    data = np.reshape(np.arange(15)+1.0,(5,3))
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
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    return HyperPoint(gen_random_lat())

def get_random_2d_point():
    '''
        Creates a random point on the surface of the globe
    '''
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    return HyperPoint(gen_random_lat(), gen_random_lon())

def get_random_3d_point():
    '''
        Creates a random point in 3d space upto 100km above the surface of the globe
    '''
    import random
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    return HyperPoint(gen_random_lat(), gen_random_lon(), random.randrange(0.0, 100.0))

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

class ScatterData(object):
    def __init__(self, x, y, data, shape, long_name):
        self.x = x
        self.y = y
        self.data = data
        self.shape = shape
        self.long_name = long_name
        
    def __getitem__(self, name):
        if name == "x":
            return self.x
        elif name == "y":
            return self.y
        elif name == "data":
            return self.data
        else:
            raise Exception("Unknown item")

def gen_random_lon():
    from random import randrange
    return randrange(-180, 180)

def gen_random_lat():
    from random import randrange
    return randrange(-90, 90)

def gen_random_data():
    from random import uniform
    return uniform(0, 0.000225)

class MockUngriddedData(object):
    def __init__(self, x, y, data, long_name, units, coords, v_type, standard_name):
        import numpy as np
        self.x = x # A numpy array
        self.y = y # A numpy array
        self.data = data # A numpy array
        self.data_list = [x, y, data]
        self.shape = np.shape(data) # A tuple
        self.long_name = long_name # A string
        self.units = units # A string
        self._coords = coords
        self.type = v_type
        self.standard_name = standard_name
        self.missing_value = np.nan

    def coords(self, optional_arg1 = None, optional_arg2 = None):
        return self._coords # list of object Coord
    
class MockCoord(object):
    def __init__(self, name):
        self._name = name
    def name(self):
        return self._name