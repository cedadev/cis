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
from cis.plotting.formatted_plot import Plotter
from cis.plotting.genericplot import Generic2DPlot
from cis.test.utils_for_testing import assert_arrays_equal


class TestPlotting(unittest.TestCase):

    def test_should_raise_io_error_with_invalid_filename(self):
        with self.assertRaises(IOError):
            cube = iris.load_cube("/")
            Plotter([cube], "line", "/")

    def test_units_formatting(self):
        from cis.plotting.plot import format_units
        from cf_units import Unit
        assert format_units("kg s-1") == "(kg s-1)"
        assert format_units("seconds since 1600") == ""  # We don't want any units as they will be converted to DateTime
        assert format_units(Unit("kg s-1")) == "(kg s-1)"

    def test_get_label(self):
        from cis.plotting.plot import get_label
        from cis.test.util.mock import make_dummy_1d_ungridded_data
        d = make_dummy_1d_ungridded_data()
        assert get_label(d) == "TOTAL RAINFALL RATE: LS+CONV KG/M2/S (kg m-2 s-1)"
        assert get_label(d, False) == "TOTAL RAINFALL RATE: LS+CONV KG/M2/S"
        d.var_name = ""
        d.long_name = ""
        assert get_label(d) == "unknown (kg m-2 s-1)"
        assert get_label(d, False) == "unknown"

    def test_get_axis_ungridded(self):
        from cis.plotting.plot import get_axis
        from cis.test.util.mock import make_dummy_2d_ungridded_data
        d = make_dummy_2d_ungridded_data()
        assert get_axis(d, "x").name() == 'latitude'
        assert get_axis(d, "x", 'latitude').name() == 'latitude'
        assert get_axis(d, "x", 'bad_name').name() == 'latitude'  # Falls back on axis name
        assert get_axis(d, "y").name() == 'longitude'
        assert get_axis(d, "y", 'longitude').name() == 'longitude'
        assert get_axis(d, "y", 'bad_name').name() == 'longitude'  # Falls back on axis name

    def test_get_axis_gridded(self):
        from cis.plotting.plot import get_axis
        from cis.test.util.mock import make_mock_cube
        from cis.data_io.gridded_data import make_from_cube
        d = make_from_cube(make_mock_cube())
        assert get_axis(d, "x").name() == 'longitude'
        assert get_axis(d, "y").name() == 'latitude'


class TestHeatMap(unittest.TestCase):
    kwargs = {}

    def test_lat_lon_increasing_no_bounds_over_greenwich(self):
        x = np.array([-0.5, 0.5])
        y = np.array([50.5, 51.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        expected_x = np.array([-1, 0, 1])
        expected_y = np.array([50, 51, 52])
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

    def test_lat_lon_increasing_no_bounds(self):
        x = np.array([0.5, 1.5])
        y = np.array([50.5, 51.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        expected_x = np.array([0, 1, 2])
        expected_y = np.array([50, 51, 52])
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

    def test_lat_lon_decreasing_no_bounds(self):
        x = np.array([0.5, -0.5])
        y = np.array([51.5, 50.5])
        values = np.array([[1, 2], [3, 4]])
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        expected_x = np.array([1, 0, -1])
        expected_y = np.array([52, 51, 50])
        expected_v = np.array([[1, 2],
                               [3, 4]])
        assert_arrays_equal(out_x, expected_x)
        assert_arrays_equal(out_y, expected_y)
        assert_arrays_equal(out_values, expected_v)

    def test_wide_longitude(self):
        x = np.arange(-174, 186, 10)
        y = np.array([50.5, 51.5])
        values = np.arange(len(y) * len(x)).reshape((len(y), len(x)))
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        x_bounds = np.arange(-179, 190, 10)
        y_bounds = np.array([50, 51, 52])
        assert_arrays_equal(out_x, x_bounds)
        assert_arrays_equal(out_y, y_bounds)

    def test_longitude_0_360(self):
        x = np.arange(10, 370, 20)
        y = np.array([50.5, 51.5])
        values = np.arange(len(y) * len(x)).reshape((len(y), len(x)))
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        x_bounds = np.arange(0, 380, 20)
        y_bounds = np.array([50, 51, 52])
        assert_arrays_equal(out_x, x_bounds)
        assert_arrays_equal(out_y, y_bounds)

    def test_longitude_0_360_one_degree(self):
        x = np.arange(0.5, 360.5, 1)
        y = np.array([50.5, 51.5])
        values = np.arange(len(y) * len(x)).reshape((len(y), len(x)))
        latitude = DimCoord(y, standard_name='latitude', units='degrees')
        longitude = DimCoord(x, standard_name='longitude', units='degrees')
        data = make_from_cube(Cube(values, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]))
        out_values, out_x, out_y= Generic2DPlot._cube_manipulation(data, longitude.contiguous_bounds(),
                                                                   latitude.contiguous_bounds())
        x_bounds = np.arange(0, 361, 1)
        y_bounds = np.array([50, 51, 52])
        assert_arrays_equal(out_x, x_bounds)
        assert_arrays_equal(out_y, y_bounds)
