'''
Module for creating mock, dummies and fakes
'''
def create_dummy_cube():

    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord
    
    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(0, 360, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return cube
