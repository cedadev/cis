'''
Module to test the one-dimensional plotting of NetCDF files
More tests can be found in the manual_integration_tests package
'''
import unittest

import iris
import numpy as np

from jasmin_cis.test.test_files.data import *
from jasmin_cis.plotting.plot import Plotter
from jasmin_cis.plotting.generic_plot import Generic_Plot
from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.test.utils_for_testing import assert_arrays_equal


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