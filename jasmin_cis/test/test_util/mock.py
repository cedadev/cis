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

def make_square_5x3_2d_cube():
    '''
        Makes a well defined cube of shape 5x3 with data as follows
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


def make_square_5x3_2d_cube_with_time():
    '''
        Makes a well defined cube of shape 5x3 with data as follows
        arr([[[   1.    2.    3.    4.    5.    6.    7.]
              [   8.    9.   10.   11.   12.   13.   14.]
              [  15.   16.   17.   18.   19.   20.   21.]]

             [[  22.   23.   24.   25.   26.   27.   28.]
              [  29.   30.   31.   32.   33.   34.   35.]
              [  36.   37.   38.   39.   40.   41.   42.]]

             [[  43.   44.   45.   46.   47.   48.   49.]
              [  50.   51.   52.   53.   54.   55.   56.]
              [  57.   58.   59.   60.   61.   62.   63.]]

             [[  64.   65.   66.   67.   68.   69.   70.]
              [  71.   72.   73.   74.   75.   76.   77.]
              [  78.   79.   80.   81.   82.   83.   84.]]

             [[  85.   86.   87.   88.   89.   90.   91.]
              [  92.   93.   94.   95.   96.   97.   98.]
              [  99.  100.  101.  102.  103.  104.  105.]]])
        and coordinates in latitude:
            array([ -10, -5, 0, 5, 10 ])
        longitude:
            array([ -5, 0, 5 ])
        time:
            array([1984-08-27, 1984-08-28, 1984-08-29, 1984-08-30, 1984-08-31, 1984-09-01, 1984-09-02])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    '''
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord
    import datetime
    from jasmin_cis.time_util import convert_obj_to_standard_date_array

    t0 = datetime.datetime(1984,8,27)
    times = np.array([t0+datetime.timedelta(days=d) for d in xrange(7)])

    time_nums = convert_obj_to_standard_date_array(times)

    time = DimCoord(time_nums, standard_name='time')
    latitude = DimCoord(np.arange(-10, 11, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105)+1.0,(5,3,7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (time, 2)])

    print data

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
    from data_io.Coord import CoordList, Coord
    from data_io.ungridded_data import UngriddedData, Metadata

    x = Coord(gen_random_lat_array((5,)), Metadata('latitude'),'x')
    coords = CoordList([x])
    data = gen_random_data_array((5,),4.0,1.0)
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)

def make_dummy_2d_ungridded_data():
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x = Coord(gen_random_lat_array((5,5)), Metadata('latitude'),'x')
    y = Coord(gen_random_lon_array((5,5)), Metadata('longitude'),'y')
    coords = CoordList([x, y])
    data = gen_random_data_array((5,5),4.0,1.0)
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)

def make_regular_2d_ungridded_data():
    '''
        Makes a well defined ungridded data object of shape 5x3 with data as follows
        array([[1,2,3],
               [4,5,6],
               [7,8,9],
               [10,11,12],
               [13,14,15]])
        and coordinates in latitude:
        array([[-10,-10,-10],
               [-5,-5,-5],
               [0,0,0],
               [5,5,5],
               [10,10,10]])
        longitude:
        array([[-5,0,5],
               [-5,0,5],
               [-5,0,5],
               [-5,0,5],
               [-5,0,5]])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    '''
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x_points = np.arange(-10, 11, 5)
    y_points = np.arange(-5, 6, 5)
    y, x = np.meshgrid(y_points,x_points)

    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
    data = np.reshape(np.arange(15)+1.0,(5,3))

    coords = CoordList([x, y])
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)


def make_regular_2d_with_time_ungridded_data():
    '''
        Makes a well defined ungridded data object of shape 5x3 with data as follows
        array([[1,2,3],
               [4,5,6],
               [7,8,9],
               [10,11,12],
               [13,14,15]])
        and coordinates in latitude:
        array([[-10,-10,-10],
               [-5,-5,-5],
               [0,0,0],
               [5,5,5],
               [10,10,10]])
        longitude:
        array([[-5,0,5],
               [-5,0,5],
               [-5,0,5],
               [-5,0,5],
               [-5,0,5]])
        time: np.array( [ 15 day increments from 27th August 1984 ] )
        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    '''
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
    import datetime

    x_points = np.arange(-10, 11, 5)
    y_points = np.arange(-5, 6, 5)
    y, x = np.meshgrid(y_points,x_points)

    t0 = datetime.datetime(1984,8,27)
    times = np.reshape(np.array([t0+datetime.timedelta(days=d) for d in xrange(15)]),(5,3))

    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
    t = Coord(times, Metadata(standard_name='time', units='DateTime Object'))

    data = np.reshape(np.arange(15)+1.0,(5,3))

    coords = CoordList([x, y, t])
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)


def make_MODIS_time_steps():
    '''
        Useful for debugging MODIS colocation
    @return:
    '''
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x = np.zeros(4)
    times = np.array([149754,149762,149770,149778])

    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    t = Coord(times, Metadata(standard_name='time', units='DateTime Object'))

    data = np.arange(4.0)

    coords = CoordList([x, t])
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)


def make_regular_4d_ungridded_data():
    '''
        Makes a well defined ungridded data object of shape 10x5 with data as follows

        data:
        [[  1.   2.   3.   4.   5.]
         [  6.   7.   8.   9.  10.]
         [ 11.  12.  13.  14.  15.]
         [ 16.  17.  18.  19.  20.]
         [ 21.  22.  23.  24.  25.]
         [ 26.  27.  28.  29.  30.]
         [ 31.  32.  33.  34.  35.]
         [ 36.  37.  38.  39.  40.]
         [ 41.  42.  43.  44.  45.]
         [ 46.  47.  48.  49.  50.]]

        latitude:
        [[-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]
         [-10.  -5.   0.   5.  10.]]

        longitude:
        [[-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]
         [-5.  -2.5  0.   2.5  5. ]]

        altitude:
        [[  0.   0.   0.   0.   0.]
         [ 10.  10.  10.  10.  10.]
         [ 20.  20.  20.  20.  20.]
         [ 30.  30.  30.  30.  30.]
         [ 40.  40.  40.  40.  40.]
         [ 50.  50.  50.  50.  50.]
         [ 60.  60.  60.  60.  60.]
         [ 70.  70.  70.  70.  70.]
         [ 80.  80.  80.  80.  80.]
         [ 90.  90.  90.  90.  90.]]

        time:
        [[1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]
         [1984-08-27 1984-08-28 1984-08-29 1984-08-30 1984-08-31]]

        They are shaped to represent a typical lidar type satelite data set.
    '''
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
    import datetime
    from jasmin_cis.time_util import convert_obj_to_standard_date_array

    x_points = np.linspace(-10,10,5)
    y_points = np.linspace(-5, 5, 5)
    t0 = datetime.datetime(1984,8,27)
    times = convert_obj_to_standard_date_array(np.array([t0+datetime.timedelta(days=d) for d in xrange(5)]))

    alt = np.linspace(0,90,10)

    data = np.reshape(np.arange(50)+1.0,(10,5))
    print np.mean(data[:,1:3])
    print np.mean(data[4:6,:])
    print np.mean(data[:,2])
    print np.std(data)
    print np.mean(data)
    print len(data.flat)

    y, a = np.meshgrid(y_points,alt)
    x, a = np.meshgrid(x_points,alt)
    t, a = np.meshgrid(times,alt)

    a = Coord(a, Metadata(standard_name='altitude', units='meters'))
    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
    t = Coord(t, Metadata(standard_name='time', units='DateTime Object'))

    coords = CoordList([x, y, a, t])
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)


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
    return gen_random_lon_array((1,))

def gen_random_lat():
    return gen_random_lat_array((1,))

def gen_random_data():
    return gen_random_data_array((1,), 0.000225, 0.0001)

def gen_random_lon_array(shape):
    from numpy.random import rand
    return 360.0 * rand(*shape) - 180.0

def gen_random_lat_array(shape):
    from numpy.random import rand
    return 180.0 * rand(*shape) - 90.0

def gen_random_data_array(shape, mean=0.0, var=1.0):
    from numpy.random import randn
    return var*randn(*shape) + mean
