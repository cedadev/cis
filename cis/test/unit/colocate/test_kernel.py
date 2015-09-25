"""
Tests the various kernels
"""
import unittest

from nose.tools import eq_
from numpy.testing import assert_almost_equal, assert_equal
import numpy as np

from cis.data_io import gridded_data
from cis.data_io.hyperpoint import HyperPoint, HyperPointList
from cis.data_io.ungridded_data import UngriddedData
from cis.test.util import mock


class TestFullAverage(unittest.TestCase):
    def test_basic_col_in_4d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, moments, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.data[0], 25.5)
        assert_almost_equal(std_dev.data[0], np.sqrt(212.5))
        eq_(no_points.data[0], 50)

    def test_basic_col_in_4d_with_pressure_not_altitude(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, moments, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, pres=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.data[0], 25.5)
        assert_almost_equal(std_dev.data[0], np.sqrt(212.5))
        eq_(no_points.data[0], 50)


class TestNNGridded(unittest.TestCase):
    def test_basic_col_gridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0),
             HyperPoint(lat=4.0, lon=4.0),
             HyperPoint(lat=-4.0, lon=-4.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 8.0)  # float(cube[2,1].data))
        eq_(new_data.data[1], 12.0)  # float(cube[3,2].data))
        eq_(new_data.data[2], 4.0)  # float(cube[1,0].data))

    def test_negative_lon_points_dont_matter_with_0_360_grid_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        # This cube is defined over a 0-360 longitude grid
        cube = gridded_data.make_from_cube(mock.make_dummy_2d_cube())

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0),
             HyperPoint(lat=19.0, lon=44.0),
             HyperPoint(lat=-4.0, lon=-14.0),
             HyperPoint(lat=-4.0, lon=-44.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 325.0)  # float(cube[9,0].data)
        eq_(new_data.data[1], 365.0)  # float(cube[10,4].data))
        eq_(new_data.data[2], 324.0)  # float(cube[8,35].data))
        eq_(new_data.data[3], 321.0)  # float(cube[8,32].data))

    def test_guessing_the_bounds_on_a_cube_doesnt_matter_for_negative_lon_points_on_a_0_360_grid_in_2d(self):
        """This should be identical to above but there was an issue in iris where this caused a problem"""
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        # This cube is defined over a 0-360 longitude grid
        cube = gridded_data.make_from_cube(mock.make_dummy_2d_cube())
        cube.coord(standard_name='longitude').guess_bounds()

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0),
             HyperPoint(lat=19.0, lon=44.0),
             HyperPoint(lat=-4.0, lon=-14.0),
             HyperPoint(lat=-4.0, lon=-44.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 325.0)  # float(cube[9,0].data)
        eq_(new_data.data[1], 365.0)  # float(cube[10,4].data))
        eq_(new_data.data[2], 324.0)  # float(cube[8,35].data))
        eq_(new_data.data[3], 321.0)  # float(cube[8,32].data))

    def test_lon_points_over_360_dont_matter_with_0_360_grid_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        # This cube is defined over a 0-360 longitude grid
        cube = gridded_data.make_from_cube(mock.make_dummy_2d_cube())

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=0.0),
             HyperPoint(lat=1.0, lon=20.0),
             HyperPoint(lat=1.0, lon=361.0),
             HyperPoint(lat=1.0, lon=381.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 325.0)  # float(cube[9,0].data))
        eq_(new_data.data[1], 327.0)  # float(cube[9,0].data))
        eq_(new_data.data[2], 325.0)  # float(cube[9,0].data))
        eq_(new_data.data[3], 327.0)  # float(cube[9,2].data))

    def test_already_collocated_in_col_gridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = UngriddedData.from_points_array([HyperPoint(0.0, 0.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 8.0)

    def test_collocation_of_alt_points_on_hybrid_altitude_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=5000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 221.0)  # float(cube[2,1,1,0].data))
        eq_(new_data.data[1], 345.0)  # float(cube[3,2,1,4].data))
        eq_(new_data.data[2], 100.0)  # float(cube[1,0,0,9].data))

    def test_negative_lon_points_on_hybrid_altitude_coordinates_dont_matter(self):
        """This should give the same results as above"""
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=5000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, t=dt.datetime(1984, 8, 28, 8, 34))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 221.0)  # float(cube[2,1,1,0].data))
        eq_(new_data.data[1], 345.0)  # float(cube[3,2,1,4].data))

    def test_collocation_of_alt_points_on_hybrid_altitude_coordinates_on_0_360_grid(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10, lon_dim_length=36,
                                                               lon_range=(0.,350.)))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=111.0, alt=5000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             HyperPoint(lat=4.0, lon=141.0, alt=12000.0, t=dt.datetime(1984, 8, 28, 8, 34))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 2501.0)  # float(cube[2,11,1,0].data))
        eq_(new_data.data[1], 3675.0)  # float(cube[3,14,1,4].data))

    def test_negative_lon_points_on_hybrid_altitude_coordinates_with_0_360_grid(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10, lon_dim_length=36,
                                                               lon_range=(0.,350.)))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=111.0, alt=5000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             HyperPoint(lat=4.0, lon=141.0, alt=12000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             HyperPoint(lat=-4.0, lon=-14.0, alt=10000.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 2501.0)  # float(cube[2,11,1,0].data))
        eq_(new_data.data[1], 3675.0)  # float(cube[3,14,1,4].data))
        eq_(new_data.data[2], 2139.0)  # float(cube[1,35,0,8].data))

    def test_collocation_of_pres_points_on_hybrid_altitude_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, pres=5000.0, t=dt.datetime(1984, 8, 28, 8, 34))])

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        # There is no pressure coordinate on the cube so no single value could be returned by the kernel
        eq_(new_data.data[0], np.inf)

    def test_collocation_of_alt_pres_points_on_hybrid_altitude_coordinates(self):
        """
        Redundant pressure coordinates should be ignored by the kernel
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=5000.0, pres=10000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, pres=10000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, pres=10000.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], float(cube[2,1,1,0].data))
        eq_(new_data.data[1], float(cube[3,2,1,4].data))
        eq_(new_data.data[2], float(cube[1,0,0,9].data))

    def test_collocation_of_pres_points_on_hybrid_pressure_coordinates_and_altitude_coordinates(self):
        """
            When only pressure coordinate is present this should be used for the collocation
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, pres=1100000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, pres=184600000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, pres=63100049.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], float(cube[2,1,1,0].data))
        eq_(new_data.data[1], float(cube[3,2,1,4].data))
        eq_(new_data.data[2], float(cube[1,0,0,9].data))

    def test_collocation_of_alt_pres_points_on_hybrid_pressure_and_altitude_coordinates(self):
        """
            When altitude and pressure coordinates are present only the altitude coordinates should be used for the
            collocation
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=10, pres=110000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=354, pres=11000000.0, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, alt=1000, pres=63100049.0, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], float(cube[2,1,1,0].data))
        eq_(new_data.data[1], float(cube[3,2,1,4].data))
        eq_(new_data.data[2], float(cube[1,0,0,9].data))

    def test_collocation_of_alt_points_on_hybrid_pressure_and_altitude_coordinates(self):
        """
            Kernel should use the auxilliary altitude dimension when altitude is present in the coordinates
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # This point actually lies outside the lower bounds for altitude at this point in space
            [HyperPoint(lat=1.0, lon=1.0, alt=10, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies in the middle of the altitude bounds at this point
             HyperPoint(lat=4.0, lon=4.0, alt=354, t=dt.datetime(1984, 8, 28, 8, 34)),
             # This point lies outside the upper bounds for altitude at this point
             HyperPoint(lat=-4.0, lon=-4.0, alt=1000, t=dt.datetime(1984, 8, 27, 2, 18, 52))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], float(cube[2,1,1,0].data))
        eq_(new_data.data[1], float(cube[3,2,1,4].data))
        eq_(new_data.data[2], float(cube[1,0,0,9].data))

    def test_coordinates_exactly_between_points_in_col_gridded_to_ungridded_in_2d(self):
        """
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                Iris seems to count a point as 'belonging' to a datapoint if it is greater than a datapoint cell's lower
                bound and less than or equal to it's upper bound. Where a cell is an imaginary boundary around a
                datapoint which divides the grid.
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 7.0)
        eq_(new_data.data[3], 4.0)

    def test_coordinates_outside_grid_in_col_gridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    def test_basic_col_gridded_to_ungridded_in_2d_with_time(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_gridded
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube_with_time())

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, t=dt.datetime(1984, 8, 28, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, t=dt.datetime(1984, 8, 31, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, t=dt.datetime(1984, 9, 2, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, nn_gridded())[0]
        eq_(new_data.data[0], 51.0)
        eq_(new_data.data[1], 82.0)
        eq_(new_data.data[2], 28.0)


class TestNNHorizontal(unittest.TestCase):
    def test_basic_col_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0), HyperPoint(lat=4.0, lon=4.0), HyperPoint(lat=-4.0, lon=-4.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    def test_already_collocated_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = UngriddedData.from_points_array([HyperPoint(0.0, 0.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        """
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_horizontal algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same  you would expect the first point to be chosen. This doesn't seem to always be the case but is
                probably down to floating points errors in the haversine calculation as these test points are pretty
                close together. This test is only really for documenting the behaviour for equidistant points.
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 11.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)


class TestNNTime(unittest.TestCase):
    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedCollocator()
        with self.assertRaises(TypeError):
            new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]

    def test_basic_col_in_2d_with_time(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)
        eq_(new_data.data[1], 7.0)
        eq_(new_data.data[2], 10.0)

    def test_basic_col_with_time(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint
        import numpy as np

        ug_data = mock.make_MODIS_time_steps()

        ref = np.array([0.0, 1.0, 2.0, 3.0])

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149751.369618055))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149759.378055556, ))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149766.373969907))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149776.375995371))
        sample_points = UngriddedData.from_points_array(sample_points)

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert (np.equal(new_data.data, ref).all())

    def test_already_collocated_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()

        t0 = dt.datetime(1984, 8, 27)
        for d in xrange(15):
            sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=t0 + dt.timedelta(days=d)))
        sample_points = UngriddedData.from_points_array(sample_points)

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert (np.equal(new_data.data, np.arange(15) + 1.0).all())

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        """
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 26)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1884, 8, 26)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1994, 8, 27)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 1.0)
        eq_(new_data.data[2], 15.0)


class TestNNAltitude(unittest.TestCase):

    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_altitude, DummyConstraint

        ug_data = mock.make_regular_4d_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedCollocator()
        with self.assertRaises(TypeError):
            new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]

    def test_basic_col_in_4d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, alt=34.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, alt=89.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 6.0)
        eq_(new_data.data[1], 16.0)
        eq_(new_data.data[2], 46.0)

    def test_already_collocated_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=80.0, t=dt.datetime(1984, 9, 4, 15, 54))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 41.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        """
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=35.0, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 16.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=-12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=91.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=890.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 46.0)
        eq_(new_data.data[2], 46.0)


class TestNNPressure(unittest.TestCase):

    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_pressure, DummyConstraint

        ug_data = mock.make_regular_4d_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedCollocator()
        with self.assertRaises(TypeError):
            new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]

    def test_basic_col_in_4d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, pres=12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, pres=34.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, pres=89.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 6.0)
        eq_(new_data.data[1], 16.0)
        eq_(new_data.data[2], 46.0)

    def test_already_collocated_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=80.0, t=dt.datetime(1984, 9, 4, 15, 54))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 41.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        """
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_pressure algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=8, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 1.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=0.1, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=91.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=890.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 46.0)
        eq_(new_data.data[2], 46.0)


class TestMean(unittest.TestCase):

    def test_basic_col_in_4d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, mean, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, DummyConstraint(), mean())[0]
        eq_(new_data.data[0], 25.5)


class TestLi(unittest.TestCase):

    def test_basic_col_gridded_to_ungridded_using_li_in_2d(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 8.8)
        assert_almost_equal(new_data.data[1], 11.2)
        assert_almost_equal(new_data.data[2], 4.8)

    def test_negative_lon_points_in_2d_dont_matter(self):
        """
            This is exactly the same test as above, except we ommit the point with negative longitude, this makes the
            collocator wrap the longitude coordinate and gives a slightly different interpolation result...
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0)])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 8.8)
        assert_almost_equal(new_data.data[1], 11.2)

    def test_collocation_of_points_on_hybrid_altitude_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=5550.0, t=dt.datetime(1984, 8, 28)),
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, t=dt.datetime(1984, 8, 28)),
             HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, t=dt.datetime(1984, 8, 27))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 222.4814815, decimal=7)
        assert_almost_equal(new_data.data[1], 321.0467626, decimal=7)
        # Test that points outside the cell are returned as masked, rather than extrapolated by default
        assert_equal(new_data.data[2], np.NAN)

    def test_negative_lon_points_on_hybrid_altitude_coordinates_dont_matter(self):
        """
            This is exactly the same test as above, except we ommit the point with negative longitude, this makes the
            collocator wrap the longitude coordinate and gives a slightly different interpolation result...
        """
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
             [HyperPoint(lat=4.0, lon=4.0, alt=6000.0, t=dt.datetime(1984, 8, 28)),
             HyperPoint(lat=0.0, lon=0.0, alt=5550.0, t=dt.datetime(1984, 8, 28))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 321.0467626, decimal=7)
        assert_almost_equal(new_data.data[1], 222.4814815, decimal=7)

    def test_collocation_of_alt_pres_points_on_hybrid_altitude_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=5550.0, pres=10000.0, t=dt.datetime(1984, 8, 28)),
             HyperPoint(lat=4.0, lon=4.0, alt=6000.0, pres=1000.0, t=dt.datetime(1984, 8, 28)),
             HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, pres=100.0, t=dt.datetime(1984, 8, 27))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 222.4814815, decimal=7)
        assert_almost_equal(new_data.data[1], 321.0467626, decimal=7)
        # Test that points outside the cell are returned as masked, rather than extrapolated by default
        assert_equal(new_data.data[2], np.NAN)

    def test_collocation_of_pres_points_on_hybrid_altitude_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
             [HyperPoint(lat=-4.0, lon=-4.0, pres=100.0, t=dt.datetime(1984, 8, 27))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        # The kernel can't return a unique point and so should raise a ValueError - leaving the data point blank
        assert_equal(new_data.data[0], np.NAN)

    def test_alt_extrapolation(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=-4.0, lon=-4.0, alt=6382.8, t=dt.datetime(1984, 8, 27))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li(extrapolate=True))[0]
        assert_almost_equal(new_data.data[0], 126.0, decimal=7)

    def test_nearest_neighbour_vertical_interpolation_on_hybrid_altitude(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_ht_len=10))

        sample_points = UngriddedData.from_points_array(
            # This is just past the top of the vertical coordinate slice
            [HyperPoint(lat=-4.0, lon=-4.0, alt=6500.0, t=dt.datetime(1984, 8, 27)),
             # This is well past the bottom of the vertical coordinate slice
             HyperPoint(lat=-4.0, lon=-4.0, alt=0.0, t=dt.datetime(1984, 8, 27))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li(nn_vertical=True))[0]
        assert_almost_equal(new_data.data[0], 124.0, decimal=7)
        assert_almost_equal(new_data.data[1], 115.0, decimal=7)

    def test_collocation_of_pres_points_on_hybrid_pressure_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
             [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=0.0, lon=0.0, pres=113625040.5, t=dt.datetime(1984, 8, 28, 12, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, t=dt.datetime(1984, 8, 28, 0, 0 ,0)),
             HyperPoint(lat=-4.0, lon=-4.0, pres=166600039.0, t=dt.datetime(1984, 8, 27))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li())[0]
        # Exactly on the lat, lon, time points, interpolated over pressure
        assert_almost_equal(new_data.data[0], 221.5, decimal=5)
        # Exactly on the lat, lon, points, interpolated over time and pressure
        assert_almost_equal(new_data.data[1], 226.5, decimal=7)
        # Exactly on the lat, time points, interpolated over longitude and pressure
        assert_almost_equal(new_data.data[2], 330.5, decimal=7)
        # Outside of the pressure bounds - extrapolation off
        assert_equal(new_data.data[3], np.inf)

    def test_negative_lon_points_on_hybrid_pressure_coordinates_dont_matter(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
             [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, t=dt.datetime(1984, 8, 28, 0, 0 ,0))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li())[0]
        # Exactly on the lat, lon, time points, interpolated over pressure
        assert_almost_equal(new_data.data[0], 221.5, decimal=5)
        # Exactly on the lat, time points, interpolated over latitude and pressure
        assert_almost_equal(new_data.data[1], 330.5, decimal=7)

    def test_nearest_neighbour_vertical_interpolation_on_hybrid_pressure(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
             [HyperPoint(lat=0.0, lon=0.0, pres=111100040.5, t=dt.datetime(1984, 8, 28, 0, 0, 0)),
             HyperPoint(lat=5.0, lon=2.5, pres=177125044.5, t=dt.datetime(1984, 8, 28, 0, 0 ,0)),
             HyperPoint(lat=-4.0, lon=-4.0, pres=68400050.0, t=dt.datetime(1984, 8, 27))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li(nn_vertical=True))[0]
        assert_almost_equal(new_data.data[0], 221)
        assert_almost_equal(new_data.data[1], 330)
        assert_almost_equal(new_data.data[2], 124.0)

    def test_extrapolation_of_pres_points_on_hybrid_pressure_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # Point interpolated in the horizontal and then extrapolated past the top vertical layer (by one layer)
            [HyperPoint(lat=-4.0, lon=-4.0, pres=68400050.0, t=dt.datetime(1984, 8, 27))])
        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, cube, None, li(extrapolate=True))[0]
        assert_almost_equal(new_data.data[0], 125.0, decimal=7)

    def test_collocation_of_alt_points_on_hybrid_altitude_and_pressure_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li, DummyConstraint
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # Test point with both pressure and altitude should interpolate over the altitude only (since that is also
            #  present in the data cube)
            [HyperPoint(lat=0.0, lon=0.0, alt=234.5, t=dt.datetime(1984, 8, 28,0,0,0)),
             HyperPoint(lat=5.0, lon=5.0, alt=355.5, t=dt.datetime(1984, 8, 28, 0, 0))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 225.5, decimal=7)
        assert_almost_equal(new_data.data[1], 346.5, decimal=7)

    def test_collocation_of_alt_pres_points_on_hybrid_altitude_and_pressure_coordinates(self):
        from cis.collocation.col_implementations import GeneralUngriddedCollocator, li, DummyConstraint
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_mock_cube(time_dim_length=3, hybrid_pr_len=10))

        sample_points = UngriddedData.from_points_array(
            # Test point with both pressure and altitude should interpolate over the altitude only (since that is also
            #  present in the data cube)
            [HyperPoint(lat=0.0, lon=0.0, alt=234.5, pres=1000, t=dt.datetime(1984, 8, 28,0,0,0))])

        col = GeneralUngriddedCollocator(fill_value=np.NAN)
        new_data = col.collocate(sample_points, cube, None, li())[0]
        assert_almost_equal(new_data.data[0], 225.5, decimal=7)

if __name__ == '__main__':
    unittest.main()
