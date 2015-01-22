import unittest
import datetime
import numpy

from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.col_implementations import GeneralGriddedColocator, mean, CubeCellConstraint, \
    BinningCubeCellConstraint, moments
from jasmin_cis.test.util.mock import make_mock_cube, make_dummy_ungridded_data_single_point, \
    make_dummy_ungridded_data_two_points_with_different_values, make_dummy_1d_ungridded_data, \
    make_dummy_1d_ungridded_data_with_invalid_standard_name, make_square_5x3_2d_cube_with_time, \
    make_square_5x3_2d_cube_with_altitude, make_square_5x3_2d_cube_with_pressure, \
    make_square_5x3_2d_cube_with_decreasing_latitude, make_square_5x3_2d_cube, make_regular_2d_ungridded_data


class TestGeneralGriddedColocator(unittest.TestCase):
    
    def test_fill_value_for_cube_cell_constraint(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)

    def test_fill_value_for_cube_cell_constraint_default_fill_value(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 0.0)
    
        col = GeneralGriddedColocator()
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')],
                                       [float('Inf'), float('Inf'), float('Inf')]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
        
    def test_single_point_results_in_single_value_in_cell(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_two_points_in_a_cell_results_in_mean_value_in_cell(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_two_points_with_different_values(0.5, 0.5, 1.2, 1.4)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.3, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result)
    
    def test_two_points_in_a_cell_results_in_mean_value_in_cell_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_two_points_with_different_values(0.5, 0.5, 1.2, 1.4)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.3, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lat_boundary_appears_in_higher_cell(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(2.5, 0.0, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lat_boundary_appears_in_higher_cell_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(2.5, 0.0, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lon_boundary_appears_in_higher_cell(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(0.0, 2.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lon_boundary_appears_in_higher_cell_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(0.0, 2.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(2.5, 2.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_point_on_a_lat_lon_boundary_appears_in_highest_cell_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(2.5, 2.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.allclose(out_cube.data.filled(), expected_result, atol=1.0e-15)
    
    def test_single_point_outside_grid_is_excluded(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_outside_grid_is_excluded_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(99, 99, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_on_grid_corner_is_counted_once(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(10, 5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_on_grid_corner_is_counted_once_using_binning(self):
        sample_cube = make_mock_cube()
        data_point = make_dummy_ungridded_data_single_point(10, 5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, 1.2]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_no_time_with_cube_with_time(self):
        sample_cube = make_square_5x3_2d_cube_with_time()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_time_on_boundary_with_cube_with_time(self):
        sample_cube = make_square_5x3_2d_cube_with_time()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0))
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_no_altitude_with_cube_with_altitude(self):
        sample_cube = make_square_5x3_2d_cube_with_altitude()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    
        print sample_cube.data
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_altitude_with_cube_with_altitude(self):
        sample_cube = make_square_5x3_2d_cube_with_altitude()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, altitude=1.0)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_no_pressure_with_cube_with_pressure(self):
        sample_cube = make_square_5x3_2d_cube_with_pressure()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)
    
        print sample_cube.data
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_pressure_with_cube_with_pressure(self):
        sample_cube = make_square_5x3_2d_cube_with_pressure()
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, pressure=1.0)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, 1.2, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]],
    
                                       [[-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9],
                                        [-999.9, -999.9, -999.9, -999.9, -999.9, -999.9, -999.9]]])
    
        print out_cube.data.filled()
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_data_with_no_standard_name(self):
        sample_cube = make_mock_cube()
        data_points = make_dummy_1d_ungridded_data()
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=mean())[0]
    
    def test_data_with_invalid_standard_name(self):
        sample_cube = make_mock_cube()
        data_points = make_dummy_1d_ungridded_data_with_invalid_standard_name()
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_points, constraint=con, kernel=mean())[0]
    
    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude(self):
        sample_cube = make_square_5x3_2d_cube_with_decreasing_latitude()
        data_point = make_dummy_ungridded_data_single_point(3.0, 0.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = CubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)
    
    def test_single_point_results_in_single_value_in_cell_with_decreasing_latitude_using_binning(self):
        sample_cube = make_square_5x3_2d_cube_with_decreasing_latitude()
        data_point = make_dummy_ungridded_data_single_point(3.0, 0.5, 1.2)
    
        col = GeneralGriddedColocator(fill_value=-999.9)
        con = BinningCubeCellConstraint()
    
        out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]
    
        expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                       [-999.9, 1.2, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9],
                                       [-999.9, -999.9, -999.9]])
    
        assert numpy.array_equal(out_cube.data.filled(), expected_result)

    def test_can_colocate_list_of_data(self):
        col = GeneralGriddedColocator()
        sample = make_square_5x3_2d_cube()
        data1 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5, 0)
        data2 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5, 10)

        constraint = BinningCubeCellConstraint()
        kernel = mean()
        output = col.colocate(sample, UngriddedDataList([data1, data2]), constraint, kernel)

        assert len(output) == 2

        expected_data2 = numpy.array([[14.5, 16.5, 18.5],
                                      [26.5, 28.5, 30.5],
                                      [38.5, 40.5, 42.5],
                                      [50.5, 52.5, 54.5],
                                      [62.5, 64.5, 66.5]])
        expected_data1 = expected_data2 - 10
        assert numpy.array_equal(output[0].data, expected_data1)
        assert numpy.array_equal(output[1].data, expected_data2)

    def test_single_moments(self):
        col = GeneralGriddedColocator()
        sample = make_square_5x3_2d_cube()
        data = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5, 10)
        constraint = BinningCubeCellConstraint()
        kernel = moments()
        output = col.colocate(sample, data, constraint, kernel)

        expected_data = numpy.array([[14.5, 16.5, 18.5],
                                     [26.5, 28.5, 30.5],
                                     [38.5, 40.5, 42.5],
                                     [50.5, 52.5, 54.5],
                                     [62.5, 64.5, 66.5]])

        expected_stddev = numpy.ones((5, 3)) * 3.5118845842842465
        expected_num = numpy.ones((5, 3)) * 4

        assert len(output) == 3
        assert isinstance(output, GriddedDataList)
        assert output[0].var_name == 'rain'
        assert output[1].var_name == 'rain_std_dev'
        assert output[2].var_name == 'rain_num_points'
        assert numpy.array_equal(output[0].data, expected_data)
        assert numpy.allclose(output[1].data, expected_stddev)
        assert numpy.array_equal(output[2].data, expected_num)

    def test_list_moments(self):
        col = GeneralGriddedColocator()
        sample = make_square_5x3_2d_cube()
        data1 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5)
        data2 = make_regular_2d_ungridded_data(10, -10, 10, 6, -5, 5)
        data2.metadata._name = 'snow'
        data2.data *= 2

        constraint = BinningCubeCellConstraint()
        kernel = moments()
        output = col.colocate(sample, UngriddedDataList([data1, data2]), constraint, kernel)

        assert len(output) == 6
        assert output[0].var_name == 'rain'
        assert output[1].var_name == 'rain_std_dev'
        assert output[2].var_name == 'rain_num_points'
        assert output[3].var_name == 'snow'
        assert output[4].var_name == 'snow_std_dev'
        assert output[5].var_name == 'snow_num_points'

        expected_data1 = numpy.array([[4.5, 6.5, 8.5],
                                      [16.5, 18.5, 20.5],
                                      [28.5, 30.5, 32.5],
                                      [40.5, 42.5, 44.5],
                                      [52.5, 54.5, 56.5]])
        expected_data2 = 2 * expected_data1
        expected_stddev1 = numpy.ones((5, 3)) * 3.5118845842842465
        expected_stddev2 = expected_stddev1 * 2
        expected_num = numpy.ones((5, 3)) * 4

        assert numpy.array_equal(output[0].data, expected_data1)
        assert numpy.allclose(output[1].data, expected_stddev1)
        assert numpy.array_equal(output[2].data, expected_num)
        assert numpy.array_equal(output[3].data, expected_data2)
        assert numpy.allclose(output[4].data, expected_stddev2)
        assert numpy.array_equal(output[5].data, expected_num)