"""
Module to test the one-dimensional plotting of NetCDF files
More tests can be found in the manual_integration_tests package
"""
import unittest

import iris
from iris.coords import DimCoord
from iris.cube import Cube
import numpy as np

from cis.data_io.gridded_data import make_from_cube
from cis.plotting.plot import Plotter
from cis.plotting.generic_plot import Generic_Plot
from cis.test.utils_for_testing import assert_arrays_equal
from cis.plotting.heatmap import make_color_mesh_cells, Heatmap


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
            cube = iris.load_cube("/")
            Plotter([cube], "line", "/")


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
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

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
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

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
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

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

        # Test that a plot doesn't fail.
        map = Heatmap([data], self.plot_args)
        map.plot()
