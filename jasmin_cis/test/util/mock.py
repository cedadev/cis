'''
Module for creating mock, dummies and fakes
'''
from nose.tools import raises
import numpy as np
import numpy.ma as ma
from iris.cube import Cube
from iris.coords import DimCoord
import datetime

from jasmin_cis.data_io.common_data import CommonData
from jasmin_cis.data_io.hyperpoint import HyperPointList
from jasmin_cis.time_util import convert_obj_to_standard_date_array

def make_mock_cube(lat_dim_length=5, lon_dim_length=3, alt_dim_length=0, pres_dim_length=0, time_dim_length=0,
                   horizontal_offset=0, altitude_offset=0, pressure_offset=0, time_offset=0, data_offset=0,
                   dim_order=None, mask=False):
    """
    Makes a cube of any shape required, with coordinate offsets from the default available. If no arguments are
    given get a 5x3 cube of the form:
        array([[1,2,3],
               [4,5,6],
               [7,8,9],
               [10,11,12],
               [13,14,15]])
        and coordinates in latitude:
            array([ -10, -5, 0, 5, 10 ])
        longitude:
            array([ -5, 0, 5 ])
    :param lat_dim_length: Latitude grid length
    :param lon_dim_length: Longitude grid length
    :param alt_dim_length: Altitude grid length
    :param pres_dim_length: Pressure grid length
    :param time_dim_length: Time grid length
    :param horizontal_offset: Offset from the default grid, in degrees, in lat and lon
    :param altitude_offset: Offset from the default grid in altitude
    :param pressure_offset: Offset from the default grid in pressure
    :param time_offset: Offset from the default grid in time
    :param dim_order: List of 'lat', 'lon', 'alt', 'pres', 'time' in the order in which the dimensions occur
    :return: A cube with well defined data.
    """

    data_size = 1
    DIM_NAMES = ['lat', 'lon', 'alt', 'pres', 'time']
    dim_lengths = [lat_dim_length, lon_dim_length, alt_dim_length, pres_dim_length, time_dim_length]

    if dim_order is None:
        dim_order = list(DIM_NAMES)

    if any([True for d in dim_order if d not in DIM_NAMES]):
        raise ValueError("dim_order contains unrecognised name")

    for idx, dim in enumerate(DIM_NAMES):
        if dim_lengths[idx] == 0 and dim in dim_order:
            del dim_order[dim_order.index(dim)]

    coord_map = {}
    for idx, dim in enumerate(dim_order):
        coord_map[dim] = dim_order.index(dim)
    coord_list = [None] * len(coord_map)

    if lat_dim_length:
        coord_list[coord_map['lat']] = (DimCoord(np.linspace(-10., 10., lat_dim_length) + horizontal_offset,
                                        standard_name='latitude', units='degrees'), coord_map['lat'])
        data_size *= lat_dim_length

    if lon_dim_length:
        coord_list[coord_map['lon']] = (DimCoord(np.linspace(-5., 5., lon_dim_length) + horizontal_offset,
                                        standard_name='longitude', units='degrees'), coord_map['lon'])
        data_size *= lon_dim_length

    if alt_dim_length:
        coord_list[coord_map['alt']] = (DimCoord(np.linspace(0., 7., alt_dim_length) + altitude_offset,
                                        standard_name='altitude', units='metres'), coord_map['alt'])
        data_size *= alt_dim_length

    if pres_dim_length:
        coord_list[coord_map['pres']] = (DimCoord(np.linspace(0., 7., pres_dim_length) + pressure_offset,
                                         standard_name='air_pressure', units='hPa'), coord_map['pres'])
        data_size *= pres_dim_length

    if time_dim_length:
        t0 = datetime.datetime(1984, 8, 27)
        times = np.array([t0 + datetime.timedelta(days=d+time_offset) for d in xrange(time_dim_length)])
        time_nums = convert_obj_to_standard_date_array(times)
        coord_list[coord_map['time']] = (DimCoord(time_nums, standard_name='time', units='days since 1600-01-01 00:00:00'),
                                         coord_map['time'])
        data_size *= time_dim_length

    data = np.reshape(np.arange(data_size) + data_offset + 1., tuple(len(i[0].points) for i in coord_list))
    if mask:
        data = np.ma.asarray(data)
        data.mask = mask

    return_cube = Cube(data, dim_coords_and_dims=coord_list)

    for coord in return_cube.coords():
        coord.guess_bounds()

    return return_cube

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


def make_dummy_2d_cube_with_small_offset_in_lat():
    '''
        Makes a dummy cube filled with random datapoints of shape 19x36
    '''
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(range(-84, 106, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(0, 360, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_small_offset_in_lon():
    '''
        Makes a dummy cube filled with random datapoints of shape 19x36
    '''
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(range(-85, 105, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(1, 361, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_small_offset_in_lat_and_lon():
    '''
        Makes a dummy cube filled with random datapoints of shape 19x36
    '''
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(range(-84, 106, 10), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(1, 361, 10), standard_name='longitude', units='degrees')
    cube = Cube(numpy.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_list_with_2_dummy_2d_cubes_where_verticies_are_in_cell_centres():
    """
    Makes two dummy cubes where the cells intersect like:

        |--------|
        |        |
        |   |----|----|
        |   |    |    |
        |--------|    |
            |         |
            |---------|

    For the second cube the values contained are a checkerboard of 0s and 1s, starting with 0 for the first cell
    """
    import numpy
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(range(0, 10, 2), standard_name='latitude', units='degrees')
    longitude = DimCoord(range(0, 10, 2), standard_name='longitude', units='degrees')
    cube1 = Cube(numpy.random.rand(5, 5), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    checkerboard = numpy.zeros((5, 5))

    for i in range(0, 5):
        for j in range(0, 5):
            if (i+j)%2 == 1:
                checkerboard[i, j] = 1

    latitude = DimCoord(numpy.arange(1, 11, 2), standard_name='latitude', units='degrees')
    longitude = DimCoord(numpy.arange(1, 11, 2), standard_name='longitude', units='degrees')
    cube2 = Cube(checkerboard, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube1, cube2


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
    
    latitude = DimCoord(np.arange(-10, 11, 5), var_name='lat', standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), var_name='lon', standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15)+1.0,(5,3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)], var_name='dummy')
    
    return cube

def make_square_5x3_2d_cube_with_extra_dim():
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
        level non coord:
            array([-10,0,10])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    '''
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(np.linspace(-10, 10, 5), var_name='lat', standard_name='latitude', units='degrees')
    longitude = DimCoord(np.linspace(-5, 5, 3), var_name='lon', standard_name='longitude', units='degrees')
    level = DimCoord(np.linspace(-10, 10, 7), var_name='lev', standard_name='air_pressure', units='Pa')
    data = np.reshape(np.arange(3 * 5 * 7) + 1.0, (5, 7, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 2), (level, 1)], var_name='dummy')

    return cube

def make_square_5x3_2d_cube_with_missing_data():
    '''
        Makes a well defined cube of shape 5x3 with data as follows
        array([[1,2,3],
               [4,M,6],
               [7,8,M],
               [10,11,12],
               [M,14,15]])
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
    values = np.ma.arange(15) + 1.0
    values[4] = np.ma.masked
    values[8] = np.ma.masked
    values[12] = np.ma.masked
    data = np.reshape(values, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    print cube.data

    return cube


def make_5x3_lon_lat_2d_cube_with_missing_data():
    """
    Makes a well defined cube of shape 5x3 with data as follows
    array([[1,2,3],
           [4,M,6],
           [7,8,M],
           [10,11,12],
           [M,14,15]])
    and coordinates in longitude:
        array([ -10, -5, 0, 5, 10 ])
    latitude:
        array([ -5, 0, 5 ])

    They are different lengths to make it easier to distinguish. Note the longitude increases
    as you step through the array in order - so downwards as it's written above
    """
    import numpy as np
    from iris.coords import DimCoord
    from iris.cube import Cube

    longitude = DimCoord(np.arange(-10, 11, 5), standard_name='longitude', units='degrees')
    latitude = DimCoord(np.arange(-5, 6, 5), standard_name='latitude', units='degrees')
    values = np.ma.arange(15) + 1.0
    values[4] = np.ma.masked
    values[8] = np.ma.masked
    values[12] = np.ma.masked
    data = np.reshape(values, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(longitude, 0), (latitude, 1)])

    return cube


def make_square_5x3_2d_cube_with_decreasing_latitude():
    """
    Makes a well defined cube of shape 5x3 with data as follows
    array([[1,2,3],
           [4,5,6],
           [7,8,9],
           [10,11,12],
           [13,14,15]])
    and coordinates in latitude:
        array([ 10, 5, 0, -5, -10 ])
    longitude:
        array([ -5, 0, 5 ])

    They are different lengths to make it easier to distinguish. Note the latitude increases
    as you step through the array in order - so downwards as it's written above
    """
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord

    latitude = DimCoord(np.arange(10, -11, -5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15) + 1.0, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_square_5x3_2d_cube_with_time(offset=0, time_offset=0):
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
    times = np.array([t0 + datetime.timedelta(days=d+time_offset) for d in xrange(7)])

    time_nums = convert_obj_to_standard_date_array(times)

    time = DimCoord(time_nums, standard_name='time')
    latitude = DimCoord(np.arange(-10+offset, 11+offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5+offset, 6+offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105)+1.0,(5,3,7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (time, 2)], var_name='dummy')

    return cube

def make_square_NxM_2d_cube_with_time(start_lat=-10, end_lat=10, lat_point_count=5,
                                      start_lon=-5, end_lon=5, lon_point_count=3,
                                      time_offset=0):
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

    t0 = datetime.datetime(1984, 8, 27)
    times = np.array([t0 + datetime.timedelta(days=d+time_offset) for d in xrange(7)])

    time_nums = convert_obj_to_standard_date_array(times)

    time = DimCoord(time_nums, standard_name='time')
    latitude = DimCoord(np.linspace(start_lat, end_lat, lat_point_count), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.linspace(start_lon, end_lon, lon_point_count), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(lat_point_count * lon_point_count * 7)+1.0, (lat_point_count, lon_point_count, 7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (time, 2)], var_name='dummy')

    return cube

def make_square_5x3_2d_cube_with_altitude(offset=0, altitude_offset=0):
    """
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
    altitude:
        array([0, 1, 2, 3, 4, 5, 6])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    """
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord

    altitude = DimCoord(np.arange(0, 7, 1)+altitude_offset, standard_name='altitude', units='metres')
    latitude = DimCoord(np.arange(-10+offset, 11+offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5+offset, 6+offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105)+1.0,(5,3,7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (altitude, 2)])

    return cube


def make_square_5x3_2d_cube_with_pressure(offset=0):
    """
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
    pressure:
        array([0, 1, 2, 3, 4, 5, 6])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    """
    import numpy as np
    from iris.cube import Cube
    from iris.coords import DimCoord

    pressure = DimCoord(np.arange(0, 7, 1), standard_name='air_pressure', units='hPa')
    latitude = DimCoord(np.arange(-10+offset, 11+offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5+offset, 6+offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105)+1.0,(5,3,7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (pressure, 2)])

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


def make_dummy_ungridded_data_single_point(lat=0.0, lon=0.0, value=1.0, time=None, altitude=None, pressure=None, mask=None):
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
    import datetime
    import numpy

    x = Coord(numpy.array(lat), Metadata('latitude'), 'x')
    y = Coord(numpy.array(lon), Metadata('longitude'), 'y')

    if (time is not None) + (altitude is not None) + (pressure is not None) > 1:
        raises(NotImplementedError)
    elif time is None and altitude is None and pressure is None:
        coords = CoordList([x, y])
    elif altitude is not None:
        z = Coord(numpy.array(altitude), Metadata('altitude'), 'z')
        coords = CoordList([x, y, z])
    elif time is not None:
        t = Coord(numpy.array(time), Metadata('time'), 't')
        coords = CoordList([x, y, t])
    elif pressure is not None:
        p = Coord(numpy.array(pressure), Metadata('air_pressure'), 'p')
        coords = CoordList([x, y, p])

    data = numpy.array(value)
    if mask:
        data = ma.masked_array(data, mask=mask)
    return UngriddedData(data, Metadata(name='Rain', standard_name='rainfall_rate', long_name="Total Rainfall",
                                        units="kg m-2 s-1", missing_value=-999), coords)


def make_dummy_ungridded_data_two_points_with_different_values(lat=0.0, lon=0.0, value1=1.0, value2=2.0):
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
    import numpy

    x = Coord(numpy.array([lat, lat]), Metadata('latitude'), 'x')
    y = Coord(numpy.array([lon, lon]), Metadata('longitude'), 'y')
    coords = CoordList([x, y])
    data = numpy.array([value1, value2])
    return UngriddedData(data, Metadata(name='Rain', standard_name='rainfall_rate', long_name="Total Rainfall",
                                        units="kg m-2 s-1", missing_value=-999), coords)


def make_dummy_1d_ungridded_data():
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x = Coord(gen_random_lat_array((5,)), Metadata('latitude'), 'x')
    coords = CoordList([x])
    data = gen_random_data_array((5,),4.0,1.0)
    return UngriddedData(data, Metadata(name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", missing_value=-999), coords)


def make_dummy_1d_ungridded_data_with_invalid_standard_name():
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x = Coord(gen_random_lat_array((5,)), Metadata('latitude'), 'x')
    coords = CoordList([x])
    data = gen_random_data_array((5,),4.0,1.0)
    return UngriddedData(data, Metadata(name='rain', standard_name='notavalidname',
                                        long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", missing_value=-999), coords)


def make_dummy_2d_ungridded_data():
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x = Coord(gen_random_lat_array((5,5)), Metadata('latitude'),'x')
    y = Coord(gen_random_lon_array((5,5)), Metadata('longitude'),'y')
    coords = CoordList([x, y])
    data = gen_random_data_array((5,5),4.0,1.0)
    return UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)


def make_regular_2d_ungridded_data(lat_dim_length=5, lat_min=-10, lat_max=10, lon_dim_length=3, lon_min=-5, lon_max=5,
                                   data_offset=0, mask=False):
    """
    Makes a well defined ungridded data object. If no arguments are supplied, it is of shape 5x3 with data as follows
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

    :param lat_dim_length: number of latitude coordinate values
    :param lat_min: minimum latitude coordinate value
    :param lat_max: maximum latitude coordinate value
    :param lon_dim_length: number of longitude coordinate values
    :param lon_min: minimum longitude coordinate value
    :param lon_max: maximum longitude coordinate value
    :param data_offset: value by which to increase data values
    :param mask: missing value mask
    :return: UngriddedData object as specified
    """
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata

    x_points = np.linspace(lat_min, lat_max, lat_dim_length)
    y_points = np.linspace(lon_min, lon_max, lon_dim_length)
    y, x = np.meshgrid(y_points, x_points)

    x = Coord(x, Metadata(name='lat', standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(name='lon', standard_name='longitude', units='degrees'))
    data = np.reshape(np.arange(lat_dim_length * lon_dim_length) + data_offset + 1.0, (lat_dim_length, lon_dim_length))
    if mask:
        data = np.ma.asarray(data)
        data.mask = mask

    coords = CoordList([x, y])
    return UngriddedData(data, Metadata(name='rain', standard_name='rainfall_rate',
                                        long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", missing_value=-999), coords)


def make_2d_ungridded_data_list_on_multiple_coordinate_sets(lat_dim_length=5, lat_min=-10, lat_max=10, lon_dim_length=3,
                                                            lon_min=-5, lon_max=5, data_offset=0, mask=False):
    import numpy as np
    from jasmin_cis.data_io.Coord import CoordList, Coord
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedDataList

    x_points = np.linspace(lat_min, lat_max, lat_dim_length)
    y_points = np.linspace(lon_min, lon_max, lon_dim_length)
    y_1, x_1 = np.meshgrid(y_points, x_points)
    x_points = np.linspace(lat_min, lat_max - 1, lat_dim_length + 1)
    y_points = np.linspace(lon_min, lon_max - 1, lon_dim_length + 1)
    y_2, x_2 = np.meshgrid(y_points, x_points)
    x_1 = Coord(x_1, Metadata(name='lat', standard_name='latitude', units='degrees north'))
    y_1 = Coord(y_1, Metadata(name='lon', standard_name='longitude', units='degrees east'))
    x_2 = Coord(x_2, Metadata(name='lat_1', standard_name='latitude', units='degrees north'))
    y_2 = Coord(y_2, Metadata(name='lon_1', standard_name='longitude', units='degrees east'))
    data = np.reshape(np.arange(lat_dim_length * lon_dim_length) + data_offset + 1.0, (lat_dim_length, lon_dim_length))
    if mask:
        data = np.ma.asarray(data)
        data.mask = mask
    coords_1 = CoordList([x_1, y_1])
    coords_2 = CoordList([x_2, y_2])
    ungridded1 = UngriddedData(data, Metadata(name='rain', standard_name='rainfall_rate',
                                              long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                              units="kg m-2 s-1", missing_value=-999), coords_1)
    ungridded2 = UngriddedData(data, Metadata(name='snow', standard_name='snowfall_rate',
                                              long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S",
                                              units="kg m-2 s-1", missing_value=-999), coords_2)
    return UngriddedDataList([ungridded1, ungridded2])

def make_regular_2d_ungridded_data_with_missing_values():
    '''
        Makes a well defined ungridded data object of shape 5x3 with data as follows, in which M denotes a missing
        value:
        array([[1,2,3],
               [4,M,6],
               [7,8,M],
               [10,11,12],
               [M,14,15]])
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
    y, x = np.meshgrid(y_points, x_points)

    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
    values = np.ma.arange(15) + 1.0
    values[4] = np.ma.masked
    values[8] = np.ma.masked
    values[12] = np.ma.masked
    data = np.reshape(values, (5, 3))

    coords = CoordList([x, y])
    return UngriddedData(data,
                         Metadata(name='rain', standard_name='rainfall_rate',
                                  long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                  units="kg m-2 s-1", missing_value=-999),
                         coords)


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
    :return:
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

        pressure:
        [[  4.   4.   4.   4.   4.]
         [ 16.  16.  16.  16.  16.]
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
    p = a
    p[0,:] = 4
    p[1,:] = 16

    a = Coord(a, Metadata(standard_name='altitude', units='meters'))
    x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
    y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
    p = Coord(p, Metadata(standard_name='air_pressure', units='Pa'))
    t = Coord(t, Metadata(standard_name='time', units='DateTime Object'))

    coords = CoordList([x, y, a, p, t])
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


class MockUngriddedData(CommonData):
    """
    Fake UngriddedData that uses data in a HyperPointList.
    """
    def __init__(self, hyperpointlist):
        if isinstance(hyperpointlist, HyperPointList):
            self.hyperpointlist = hyperpointlist
        elif isinstance(hyperpointlist, list):
            self.hyperpointlist = HyperPointList(hyperpointlist)
        else:
            raise ValueError("Expected HyperPointList or list of HyperPoints")

    def get_coordinates_points(self):
        return self.hyperpointlist

    def get_all_points(self):
        return self.hyperpointlist

    def get_non_masked_points(self):
        return self.hyperpointlist

    def is_gridded(self):
        return False
