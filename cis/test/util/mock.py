"""
Module for creating mock, dummies and fakes
"""
from nose.tools import raises
import numpy as np
import numpy.ma as ma
from iris.cube import Cube
from iris.coords import DimCoord, AuxCoord
import datetime

from cis.time_util import convert_datetime_to_std_time

WKT_DIAMOND = "POLYGON ((-5.5 0, 0 5.5, 5.5 0, 0 -5.5, -5.5 0))"


def make_mock_cube(lat_dim_length=5, lon_dim_length=3, lon_range=None, alt_dim_length=0, pres_dim_length=0,
                   time_dim_length=0,
                   horizontal_offset=0, altitude_offset=0, pressure_offset=0, time_offset=0, data_offset=0,
                   surf_pres_offset=0,
                   hybrid_ht_len=0, hybrid_pr_len=0, geopotential_height=False, dim_order=None, mask=False):
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
    :param data_offset: Offset from the default data values
    :param surf_pres_offset: Offset for the optional surface pressure field
    :param hybrid_ht_len: Hybrid height grid length
    :param hybrid_pr_len: Hybrid pressure grid length
    :param geopotential_height: Include a geopotential height field when calcluting a hybrid pressure? (default False)
    :param dim_order: List of 'lat', 'lon', 'alt', 'pres', 'time' in the order in which the dimensions occur
    :param mask: A mask to apply to the data, this should be either a scalar or the same shape as the data
    :return: A cube with well defined data.
    """
    import iris
    from iris.aux_factory import HybridHeightFactory, HybridPressureFactory

    data_size = 1
    DIM_NAMES = ['lat', 'lon', 'alt', 'pres', 'time', 'hybrid_ht', 'hybrid_pr']
    dim_lengths = [lat_dim_length, lon_dim_length, alt_dim_length, pres_dim_length, time_dim_length, hybrid_ht_len,
                   hybrid_pr_len]
    lon_range = lon_range or (-5., 5.)

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
                                                 standard_name='latitude', units='degrees', var_name='lat'),
                                        coord_map['lat'])
        data_size *= lat_dim_length

    if lon_dim_length:
        coord_list[coord_map['lon']] = (
            DimCoord(np.linspace(lon_range[0], lon_range[1], lon_dim_length) + horizontal_offset,
                     standard_name='longitude', units='degrees', var_name='lon'), coord_map['lon'])
        data_size *= lon_dim_length

    if alt_dim_length:
        coord_list[coord_map['alt']] = (DimCoord(np.linspace(0., 7., alt_dim_length) + altitude_offset,
                                                 standard_name='altitude', units='metres', var_name='alt'),
                                        coord_map['alt'])
        data_size *= alt_dim_length

    if pres_dim_length:
        coord_list[coord_map['pres']] = (DimCoord(np.linspace(0., 7., pres_dim_length) + pressure_offset,
                                                  standard_name='air_pressure', units='hPa', var_name='pres'),
                                         coord_map['pres'])
        data_size *= pres_dim_length

    if time_dim_length:
        t0 = datetime.datetime(1984, 8, 27)
        times = np.array([t0 + datetime.timedelta(days=d + time_offset) for d in range(time_dim_length)])
        time_nums = convert_datetime_to_std_time(times)
        time_bounds = None
        if time_dim_length == 1:
            time_bounds = convert_datetime_to_std_time(np.array([times[0] - datetime.timedelta(days=0.5),
                                                                       times[0] + datetime.timedelta(days=0.5)]))
        coord_list[coord_map['time']] = (DimCoord(time_nums, standard_name='time',
                                                  units='days since 1600-01-01 00:00:00', var_name='time',
                                                  bounds=time_bounds),
                                         coord_map['time'])
        data_size *= time_dim_length

    if hybrid_ht_len:
        coord_list[coord_map['hybrid_ht']] = (DimCoord(np.arange(hybrid_ht_len, dtype='i8') + 10,
                                                       "model_level_number", units="1"), coord_map['hybrid_ht'])
        data_size *= hybrid_ht_len

    if hybrid_pr_len:
        coord_list[coord_map['hybrid_pr']] = (DimCoord(np.arange(hybrid_pr_len, dtype='i8'),
                                                       "atmosphere_hybrid_sigma_pressure_coordinate", units="1"),
                                              coord_map['hybrid_pr'])
        data_size *= hybrid_pr_len

    data = np.reshape(np.arange(data_size) + data_offset + 1., tuple(len(i[0].points) for i in coord_list))

    if mask:
        data = np.ma.asarray(data)
        data.mask = mask

    return_cube = Cube(data, dim_coords_and_dims=coord_list, var_name='rain', standard_name='rainfall_rate',
                       long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1")

    if hybrid_ht_len:
        return_cube.add_aux_coord(iris.coords.AuxCoord(np.arange(hybrid_ht_len, dtype='i8') + 40,
                                                       long_name="level_height",
                                                       units="m", var_name='hybrid_ht'), coord_map['hybrid_ht'])
        return_cube.add_aux_coord(iris.coords.AuxCoord(np.arange(hybrid_ht_len, dtype='i8') + 50,
                                                       long_name="sigma", units="1", var_name='sigma'),
                                  coord_map['hybrid_ht'])
        return_cube.add_aux_coord(iris.coords.AuxCoord(
            np.arange(lat_dim_length * lon_dim_length, dtype='i8').reshape(lat_dim_length, lon_dim_length) + 100,
            long_name="surface_altitude",
            units="m"), [coord_map['lat'], coord_map['lon']])

        return_cube.add_aux_factory(HybridHeightFactory(
            delta=return_cube.coord("level_height"),
            sigma=return_cube.coord("sigma"),
            orography=return_cube.coord("surface_altitude")))
    elif hybrid_pr_len:
        return_cube.add_aux_coord(iris.coords.AuxCoord(np.arange(hybrid_pr_len, dtype='i8') + 40,
                                                       long_name="hybrid A coefficient at layer midpoints",
                                                       units="Pa", var_name='a'), coord_map['hybrid_pr'])
        return_cube.add_aux_coord(iris.coords.AuxCoord(np.arange(hybrid_pr_len, dtype='f8') + 50,
                                                       long_name="hybrid B coefficient at layer midpoints", units="1",
                                                       var_name='b'),
                                  coord_map['hybrid_pr'])
        return_cube.add_aux_coord(
            iris.coords.AuxCoord(np.arange(lat_dim_length * lon_dim_length * time_dim_length, dtype='i8')
                                 .reshape(lat_dim_length, lon_dim_length, time_dim_length) * 100000 + surf_pres_offset,
                                 "surface_air_pressure", units="Pa"),
            [coord_map['lat'], coord_map['lon'], coord_map['time']])

        if geopotential_height:
            return_cube.add_aux_coord(iris.coords.AuxCoord(
                np.arange(lat_dim_length * lon_dim_length * time_dim_length * hybrid_pr_len, dtype='i8')
                .reshape(lat_dim_length, lon_dim_length, time_dim_length, hybrid_pr_len) + 10,
                "altitude", long_name="Geopotential height at layer midpoints", units="meter"),
                [coord_map['lat'], coord_map['lon'], coord_map['time'], coord_map['hybrid_pr']])

        return_cube.add_aux_factory(HybridPressureFactory(
            delta=return_cube.coord("hybrid A coefficient at layer midpoints"),
            sigma=return_cube.coord("hybrid B coefficient at layer midpoints"),
            surface_air_pressure=return_cube.coord("surface_air_pressure")))

    for coord in return_cube.coords(dim_coords=True):
        if coord.bounds is None:
            coord.guess_bounds()

    return return_cube


def make_dummy_2d_cube():
    """
        Makes a dummy cube filled with random datapoints of shape 19x36
    """

    latitude = DimCoord(np.arange(-85., 105., 10.), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(0., 360., 10.), standard_name='longitude', units='degrees')
    cube = Cube(np.reshape(np.arange(19 * 36) + 1.0, (19, 36)),
                dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_circular_lon():
    """
        Makes a dummy cube filled with random datapoints of shape 19x36
    """

    latitude = DimCoord(np.arange(-90., 100., 10.), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(0., 360., 10.), standard_name='longitude', units='degrees', circular=True)
    cube = Cube(np.reshape(np.arange(19 * 36) + 1.0, (19, 36)),
                dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_small_offset_in_lat():
    """
        Makes a dummy cube filled with random datapoints of shape 19x36
    """

    latitude = DimCoord(list(range(-84, 106, 10)), standard_name='latitude', units='degrees')
    longitude = DimCoord(list(range(0, 360, 10)), standard_name='longitude', units='degrees')
    cube = Cube(np.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_small_offset_in_lon():
    """
        Makes a dummy cube filled with random datapoints of shape 19x36
    """

    latitude = DimCoord(list(range(-85, 105, 10)), standard_name='latitude', units='degrees')
    longitude = DimCoord(list(range(1, 361, 10)), standard_name='longitude', units='degrees')
    cube = Cube(np.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_dummy_2d_cube_with_small_offset_in_lat_and_lon():
    """
        Makes a dummy cube filled with random datapoints of shape 19x36
    """

    latitude = DimCoord(list(range(-84, 106, 10)), standard_name='latitude', units='degrees')
    longitude = DimCoord(list(range(1, 361, 10)), standard_name='longitude', units='degrees')
    cube = Cube(np.random.rand(19, 36), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

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

    latitude = DimCoord(list(range(0, 10, 2)), standard_name='latitude', units='degrees')
    longitude = DimCoord(list(range(0, 10, 2)), standard_name='longitude', units='degrees')
    cube1 = Cube(np.random.rand(5, 5), dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    checkerboard = np.zeros((5, 5))

    for i in range(0, 5):
        for j in range(0, 5):
            if (i + j) % 2 == 1:
                checkerboard[i, j] = 1

    latitude = DimCoord(np.arange(1, 11, 2), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(1, 11, 2), standard_name='longitude', units='degrees')
    cube2 = Cube(checkerboard, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube1, cube2


def make_square_5x3_2d_cube():
    """
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
    """

    latitude = DimCoord(np.arange(-10., 11., 5), var_name='lat', standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5., 6., 5), var_name='lon', standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15) + 1.0, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)], var_name='dummy')

    return cube


def make_square_5x3_2d_cube_with_extra_dim():
    """
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
    """

    latitude = DimCoord(np.linspace(-10, 10, 5), var_name='lat', standard_name='latitude', units='degrees')
    longitude = DimCoord(np.linspace(-5, 5, 3), var_name='lon', standard_name='longitude', units='degrees')
    level = DimCoord(np.linspace(-10, 10, 7), var_name='lev', standard_name='air_pressure', units='Pa')
    data = np.reshape(np.arange(3 * 5 * 7) + 1.0, (5, 7, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 2), (level, 1)], var_name='dummy')

    return cube


def make_square_5x3_2d_cube_with_missing_data():
    """
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
    """

    latitude = DimCoord(np.arange(-10, 11, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), standard_name='longitude', units='degrees')
    values = np.ma.arange(15) + 1.0
    values[4] = np.ma.masked
    values[8] = np.ma.masked
    values[12] = np.ma.masked
    data = np.reshape(values, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

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

    latitude = DimCoord(np.arange(10, -11, -5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5, 6, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15) + 1.0, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    return cube


def make_square_5x3_2d_cube_with_time(offset=0, time_offset=0):
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
        time:
            array([1984-08-27, 1984-08-28, 1984-08-29, 1984-08-30, 1984-08-31, 1984-09-01, 1984-09-02])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    """
    import datetime

    t0 = datetime.datetime(1984, 8, 27)
    times = np.array([t0 + datetime.timedelta(days=d + time_offset) for d in range(7)])

    time_nums = convert_datetime_to_std_time(times)

    time = DimCoord(time_nums, standard_name='time')
    latitude = DimCoord(np.arange(-10 + offset, 11 + offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5 + offset, 6 + offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105) + 1.0, (5, 3, 7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (time, 2)], var_name='dummy')

    return cube


def make_square_5x3_2d_cube_with_scalar_time(time_offset=0):
    """
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
        time:
            1984-08-27
        time_bounds:
            [1984-08-22, 1984-09-01]
    """
    from cis.time_util import cis_standard_time_unit

    t0 = datetime.datetime(1984, 8, 27)

    time_nums = convert_datetime_to_std_time(t0 + datetime.timedelta(days=time_offset))

    time = DimCoord(time_nums, standard_name='time',
                    bounds=[convert_datetime_to_std_time(t0 - datetime.timedelta(days=5)),
                            convert_datetime_to_std_time(t0 + datetime.timedelta(days=5))],
                    units=cis_standard_time_unit)

    latitude = DimCoord(np.arange(-10., 11., 5), var_name='lat', standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5., 6., 5), var_name='lon', standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(15) + 1.0, (5, 3))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)], var_name='dummy')

    cube.add_aux_coord(time)

    return cube


def make_square_NxM_2d_cube_with_time(start_lat=-10, end_lat=10, lat_point_count=5,
                                      start_lon=-5, end_lon=5, lon_point_count=3,
                                      time_offset=0):
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
        time:
            array([1984-08-27, 1984-08-28, 1984-08-29, 1984-08-30, 1984-08-31, 1984-09-01, 1984-09-02])

        They are different lengths to make it easier to distinguish. Note the latitude increases
        as you step through the array in order - so downwards as it's written above
    """
    import datetime

    t0 = datetime.datetime(1984, 8, 27)
    times = np.array([t0 + datetime.timedelta(days=d + time_offset) for d in range(7)])

    time_nums = convert_datetime_to_std_time(times)

    time = DimCoord(time_nums, standard_name='time')
    latitude = DimCoord(np.linspace(start_lat, end_lat, lat_point_count), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.linspace(start_lon, end_lon, lon_point_count), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(lat_point_count * lon_point_count * 7) + 1.0, (lat_point_count, lon_point_count, 7))
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

    altitude = DimCoord(np.arange(0, 7, 1) + altitude_offset, standard_name='altitude', units='metres')
    latitude = DimCoord(np.arange(-10 + offset, 11 + offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5 + offset, 6 + offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105) + 1.0, (5, 3, 7))
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

    pressure = DimCoord(np.arange(0, 7, 1), standard_name='air_pressure', units='hPa')
    latitude = DimCoord(np.arange(-10 + offset, 11 + offset, 5), standard_name='latitude', units='degrees')
    longitude = DimCoord(np.arange(-5 + offset, 6 + offset, 5), standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(105) + 1.0, (5, 3, 7))
    cube = Cube(data, dim_coords_and_dims=[(latitude, 0), (longitude, 1), (pressure, 2)])

    return cube


def make_dummy_1d_cube():
    latitude = DimCoord(list(range(-85, 105, 10)), standard_name='latitude', units='degrees')
    cube = Cube(np.random.rand(19), dim_coords_and_dims=[(latitude, 0)])

    return cube


def make_dummy_ungridded_data_time_series(len=10):
    """
    Create a time series of ungridded data of length len, with a single lat/lon coordinate (65.2, -12.1)
    :param len: length of teh time series and associated data
    :return:
    """
    from datetime import datetime, timedelta
    from cis.time_util import cis_standard_time_unit

    t0 = datetime(1984, 8, 27)
    times = np.array([t0 + timedelta(days=d) for d in range(len)])

    x = AuxCoord(np.zeros(len) + 65.2, standard_name='latitude', units='degrees')
    y = AuxCoord(np.zeros(len) - 12.1, standard_name='longitude', units='degrees')
    t = AuxCoord(cis_standard_time_unit.date2num(times), standard_name='time', units=cis_standard_time_unit)
    data = np.arange(len) + 1.0
    index = DimCoord(range(len), var_name="Obs")

    return Cube(data, standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(index, 0)], aux_coords_and_dims=[(x, 0), (y, 0), (t, 0)])


def make_dummy_ungridded_data_single_point(lat=0.0, lon=0.0, value=1.0, time=None, altitude=None, pressure=None,
                                           mask=None):

    x = AuxCoord(np.array(lat), standard_name='latitude')
    y = AuxCoord(np.array(lon), standard_name='longitude')

    if (time is not None) + (altitude is not None) + (pressure is not None) > 1:
        raises(NotImplementedError)
    elif time is None and altitude is None and pressure is None:
        coords = [(x, 0), (y, 0)]
    elif altitude is not None:
        z = AuxCoord(np.array(altitude), standard_name='altitude')
        coords = [(x, 0), (y, 0), (z, 0)]
    elif time is not None:
        t = AuxCoord(np.array(time), standard_name='time')
        coords = [(x, 0), (y, 0), (t, 0)]
    elif pressure is not None:
        p = AuxCoord(np.array(pressure), standard_name='air_pressure')
        coords = [(x, 0), (y, 0), (p, 0)]

    data = np.array(value)
    if mask:
        data = ma.masked_array(data, mask=mask)
    return Cube(data, var_name='Rain', standard_name='rainfall_rate', long_name="Total Rainfall",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord([0], var_name="Obs"), 0)],
                aux_coords_and_dims=coords)


def make_dummy_sample_points(lat=None, lon=None, time=None, alt=None, pres=None):
    # Find the length of the first non-None array
    n_values = len(lat or lon or time or alt or pres)
    sample = Cube(np.empty((n_values,)))
    if lat is not None:
        sample.add_aux_coord(AuxCoord(lat, standard_name='latitude'), 0)
    if lon is not None:
        sample.add_aux_coord(AuxCoord(lon, standard_name='longitude'), 0)
    if time is not None:
        sample.add_aux_coord(AuxCoord(time, standard_name='time'), 0)
    if alt is not None:
        sample.add_aux_coord(AuxCoord(alt, standard_name='altitude'), 0)
    if pres is not None:
        sample.add_aux_coord(AuxCoord(pres, standard_name='air_pressure'), 0)
    return sample


def make_dummy_ungridded_data_two_points_with_different_values(lat=0.0, lon=0.0, value1=1.0, value2=2.0):
    x = AuxCoord(np.array([lat, lat]), standard_name='latitude')
    y = AuxCoord(np.array([lon, lon]), standard_name='longitude')
    data = np.array([value1, value2])
    return Cube(data, var_name='Rain', standard_name='rainfall_rate', long_name="Total Rainfall",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord([0, 1], var_name="Obs"), 0)],
                aux_coords_and_dims=[(x,0), (y,0)])


def make_dummy_1d_ungridded_data():
    x = AuxCoord(gen_random_lat_array((5,)), standard_name='latitude')
    data = gen_random_data_array((5,), 4.0, 1.0)
    return Cube(data, var_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(5), var_name="Obs"), 0)],
                aux_coords_and_dims=[(x,0)])


def make_dummy_1d_ungridded_data_with_invalid_standard_name():
    x = AuxCoord(gen_random_lat_array((5,)), standard_name='latitude')
    data = gen_random_data_array((5,), 4.0, 1.0)
    return Cube(data, var_name='rain', standard_name='notavalidname',
                                        long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(5), var_name="Obs"), 0)],
                aux_coords_and_dims=[(x, 0)])


def make_dummy_2d_ungridded_data():
    x = AuxCoord(gen_random_lat_array((5, 5)), standard_name='latitude')
    y = AuxCoord(gen_random_lat_array((5, 5)), standard_name='longitude')
    data = gen_random_data_array((5, 5), 4.0, 1.0)
    return Cube(data, standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                        units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(5), var_name="x"), 0),
                                                                                 (DimCoord(range(5), var_name="y"), 1)],
                aux_coords_and_dims=[(x, (0, 1)), (y, (0, 1))])


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

    x_points = np.linspace(lat_min, lat_max, lat_dim_length)
    y_points = np.linspace(lon_min, lon_max, lon_dim_length)
    y, x = np.meshgrid(y_points, x_points)

    x = AuxCoord(x, var_name='lat', standard_name='latitude', units='degrees')
    y = AuxCoord(y, var_name='lon', standard_name='longitude', units='degrees')
    data = np.reshape(np.arange(lat_dim_length * lon_dim_length) + data_offset + 1.0, (lat_dim_length, lon_dim_length))
    if mask:
        data = np.ma.asarray(data)
        data.mask = mask

    return Cube(data, var_name='rain', standard_name='rainfall_rate', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(lat_dim_length), var_name="x"), 0),
                                                         (DimCoord(range(lon_dim_length), var_name="y"), 1)],
                aux_coords_and_dims=[(x, (0, 1)), (y, (0, 1))])


def make_regular_2d_ungridded_data_with_missing_values():
    """
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
    """

    x_points = np.arange(-10, 11, 5)
    y_points = np.arange(-5, 6, 5)
    y, x = np.meshgrid(y_points, x_points)

    x = AuxCoord(x, standard_name='latitude', units='degrees')
    y = AuxCoord(y, standard_name='longitude', units='degrees')
    values = np.ma.arange(15) + 1.0
    values[4] = np.ma.masked
    values[8] = np.ma.masked
    values[12] = np.ma.masked
    data = np.reshape(values, (5, 3))

    return Cube(data, var_name='rain', standard_name='rainfall_rate', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(5), var_name="x"), 0),
                                                         (DimCoord(range(3), var_name="y"), 1)],
                aux_coords_and_dims=[(x, (0, 1)), (y, (0, 1))])


def make_regular_2d_with_time_ungridded_data():
    """
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
    """
    import datetime
    from cis.time_util import cis_standard_time_unit

    x_points = np.arange(-10, 11, 5)
    y_points = np.arange(-5, 6, 5)
    y, x = np.meshgrid(y_points, x_points)

    t0 = datetime.datetime(1984, 8, 27)
    times = np.reshape(np.array([t0 + datetime.timedelta(days=d) for d in range(15)]), (5, 3))

    x = AuxCoord(x, standard_name='latitude', units='degrees')
    y = AuxCoord(y, standard_name='longitude', units='degrees')
    t = AuxCoord(cis_standard_time_unit.date2num(times), standard_name='time', units=cis_standard_time_unit)

    data = np.reshape(np.arange(15) + 1.0, (5, 3))

    return Cube(data, var_name='rain', standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(5), var_name="x"), 0),
                                                         (DimCoord(range(3), var_name="y"), 1)],
                aux_coords_and_dims=[(x, (0, 1)), (y, (0, 1)), (t, (0, 1))])


def make_MODIS_time_steps():
    """
        Useful for debugging MODIS collocation
    :return:
    """
    x = np.zeros(4)
    times = np.array([149754, 149762, 149770, 149778])

    x = AuxCoord(x, standard_name='latitude', units='degrees')
    t = AuxCoord(times, standard_name='time')

    data = np.arange(4.0)

    return Cube(data, standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(4), var_name="Obs"), 0)],
                aux_coords_and_dims=[(x,0), (t,0)])


def make_regular_4d_ungridded_data():
    """
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
    """
    from cis.time_util import cis_standard_time_unit
    import datetime

    x_points = np.linspace(-10, 10, 5)
    y_points = np.linspace(-5, 5, 5)
    t0 = datetime.datetime(1984, 8, 27)
    times = convert_datetime_to_std_time(np.array([t0 + datetime.timedelta(days=d) for d in range(5)]))

    alt = np.linspace(0, 90, 10)

    data = np.reshape(np.arange(50) + 1.0, (10, 5))

    y, a = np.meshgrid(y_points, alt)
    x, a = np.meshgrid(x_points, alt)
    t, a = np.meshgrid(times, alt)
    p = a
    p[0, :] = 4
    p[1, :] = 16

    a = AuxCoord(a, standard_name='altitude', units='meters')
    x = AuxCoord(x, standard_name='latitude', units='degrees')
    y = AuxCoord(y, standard_name='longitude', units='degrees')
    p = AuxCoord(p, standard_name='air_pressure', units='Pa')
    t = AuxCoord(t, standard_name='time', units=cis_standard_time_unit)

    return Cube(data, standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                units="kg m-2 s-1", dim_coords_and_dims=[(DimCoord(range(10), var_name="z"), 0),
                                                         (DimCoord(range(5), var_name="t"), 1)],
                aux_coords_and_dims=[(x, (0, 1)), (y, (0, 1)), (t, (0, 1)), (a, (0, 1)), (p, (0, 1))])


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
    return var * randn(*shape) + mean

