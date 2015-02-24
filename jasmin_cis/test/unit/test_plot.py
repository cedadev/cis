'''
Module to test the one-dimensional plotting of NetCDF files
More tests can be found in the manual_integration_tests package
'''
import unittest

import iris
from iris.coords import DimCoord
from iris.cube import Cube
import numpy as np
from data_io.gridded_data import make_from_cube

from jasmin_cis.test.test_files.data import *
from jasmin_cis.plotting.plot import Plotter
from jasmin_cis.plotting.generic_plot import Generic_Plot
from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.test.utils_for_testing import assert_arrays_equal
from jasmin_cis.plotting.heatmap import make_color_mesh_cells, Heatmap


def delete_file_if_exists():
    '''
    Used to delete the file that will be created before tests are run
    in order to be able to check after the test if the file was created by the test
    '''
    if os.path.isfile(out_filename):
        os.remove(out_filename)


def make_cube(filename, variable = None):
    if variable is None:
        variable = valid_variable_in_valid_filename
    variable = iris.AttributeConstraint(name = variable)
    cube = iris.load_cube(filename, variable)
    cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
    return cube


class TestPlotting(unittest.TestCase):

    plot_args = {'x_variable': 'longitude',
                 'y_variable': 'latitude',
                 'valrange': {'vmin': 0, 'vmax': 2},
                 'xrange': {'xmin': 0, 'xmax': 360}
                 }

    class TestGenericPlot(Generic_Plot):
        def plot(self):
                pass

    def test_should_raise_io_error_with_invalid_filename(self):
        with self.assertRaises(IOError):
            cube = make_cube("/")
            Plotter([cube], "line", "/")

    def test_GIVEN_flat_UngriddedData_WHEN_create_GenericPlot_THEN_latlons_sorted_correctly(self):
        x = np.array([[0, 90, 180, 270, 360, 0],
                      [0, 90, 180, 270, 360, 0],
                      [0, 90, 180, 270, 360, 0],
                      [0, 90, 180, 270, 360, 0]])
        y = np.array([6 * [-90], 6 * [45], 6 * [-45], 6 * [90]])
        data = np.arange(1, 25).reshape(x.shape)
        x_coord = Coord(x, Metadata('longitude'), 'x')
        y_coord = Coord(y, Metadata('latitude'), 'y')
        coords = CoordList([x_coord, y_coord])
        data = UngriddedData(data, Metadata('data'), coords)

        plot = self.TestGenericPlot([data], self.plot_args)
        expected_x = np.array([[0, 0, 0, 90, 180, 270],
                               [0, 0, 0, 90, 180, 270],
                               [0, 0, 0, 90, 180, 270],
                               [0, 0, 0, 90, 180, 270]])
        expected_y = np.array([6 * [90], 6 * [45], 6 * [-45], 6 * [-90]])
        expected_data = np.array([[19, 23, 24, 20, 21, 22],
                                  [7, 11, 12, 8, 9, 10],
                                  [13, 17, 18, 14, 15, 16],
                                  [1, 5, 6, 2, 3, 4]])
        assert_arrays_equal(plot.unpacked_data_items[0]['x'], expected_x)
        assert_arrays_equal(plot.unpacked_data_items[0]['y'], expected_y)
        assert_arrays_equal(plot.unpacked_data_items[0]['data'], expected_data)


class TestHeatMap(unittest.TestCase):

    plot_args = {'x_variable': 'longitude',
                 'y_variable': 'latitude',
                 'valrange': {},
                 'xrange': {'xmin': None, 'xmax': None},
                 'datagroups': {0: {'cmap': None,
                                    'cmin': None,
                                    'cmax': None}},
                 'nasabluemarble': False,
                 'coastlinescolour': None
                }
    kwargs = {}

    def test_lat_lon_increasing_no_bounds_over_greenwich(self):
        x = np.array([-0.5, 0.5])
        y = np.array([50.5, 51.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_x, out_y, out_values = make_color_mesh_cells(data, self.plot_args)
        expected_x = np.array([[-1, 0, 1],
                               [-1, 0, 1],
                               [-1, 0, 1]])
        expected_y = np.array([[50, 50, 50],
                               [51, 51, 51],
                               [52, 52, 52]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, values)

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()

    def test_lat_lon_increasing_no_bounds(self):
        x = np.array([0.5, 1.5])
        y = np.array([50.5, 51.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_x, out_y, out_values = make_color_mesh_cells(data, self.plot_args)
        expected_x = np.array([[0, 1, 2],
                               [0, 1, 2],
                               [0, 1, 2]])
        expected_y = np.array([[50, 50, 50],
                               [51, 51, 51],
                               [52, 52, 52]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, values)

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()

    def test_lat_lon_decreasing_no_bounds(self):
        x = np.array([0.5, -0.5])
        y = np.array([51.5, 50.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_x, out_y, out_values = make_color_mesh_cells(data, self.plot_args)
        expected_x = np.array([[1, 0, -1],
                               [1, 0, -1],
                               [1, 0, -1]])
        expected_y = np.array([[52, 52, 52],
                               [51, 51, 51],
                               [50, 50, 50]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, values)

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()

    def test_wide_longitude(self):
        x = np.arange(-174, 186, 10)
        y = np.array([50.5, 51.5])
        values = np.arange(len(y) * len(x)).reshape((len(y), len(x)))
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_x, out_y, out_values = make_color_mesh_cells(data, self.plot_args)
        x_bounds = np.arange(-179, 190, 10)
        y_bounds = np.array([50, 51, 52])
        expected_x, expected_y = np.meshgrid(x_bounds, y_bounds)
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, values)

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()

    def test_longitude_0_360(self):
        x = np.arange(10, 370, 20)
        y = np.array([50.5, 51.5])
        values = np.arange(len(y) * len(x)).reshape((len(y), len(x)))
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_x, out_y, out_values = make_color_mesh_cells(data, self.plot_args)
        x_bounds = np.arange(0, 380, 20)
        y_bounds = np.array([50, 51, 52])
        expected_x, expected_y = np.meshgrid(x_bounds, y_bounds)
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, values)

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()