'''
Module for creating mock, dummies and fakes
'''
def make_dummy_2d_cube():

    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(0, 360, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return cube

def make_dummy_1d_cube():
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    cube = Cube(numpy.random.rand(19), dim_coords_and_dims=[(latitude, 0)])
    
    return cube

def get_random_1d_point():
    import random
    from jasmin_cis.col import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0))

def get_random_2d_point():
    import random
    from jasmin_cis.col import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0), random.randrange(0.0, 360.0))

def get_random_3d_point():
    import random
    from jasmin_cis.col import HyperPoint
    return HyperPoint(random.randrange(-90.0, 90.0), random.randrange(0.0, 360.0), random.randrange(0.0, 100.0))

def make_dummy_1d_points_list(num):
    return [ get_random_1d_point() for i in xrange(0,num) ]

def make_dummy_2d_points_list(num):
    return [ get_random_2d_point() for i in xrange(0,num) ]
        
def make_dummy_1d_ungridded_data():
    pass

def make_dummy_2d_ungridded_data():
    pass

