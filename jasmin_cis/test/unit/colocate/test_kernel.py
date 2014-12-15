"""
Tests the various kernels
"""
import unittest
from nose.tools import eq_
from numpy.testing import assert_almost_equal
import numpy as np

from jasmin_cis.data_io import gridded_data
from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
from jasmin_cis.data_io.ungridded_data import UngriddedData
from jasmin_cis.test.util import mock


class TestFullAverage(unittest.TestCase):
    def test_basic_col_in_4d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, moments, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.data[0], 25.5)
        assert_almost_equal(std_dev.data[0], np.sqrt(212.5))
        eq_(no_points.data[0], 50)

    def test_basic_col_in_4d_with_pressure_not_altitude(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, moments, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, pres=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.data[0], 25.5)
        assert_almost_equal(std_dev.data[0], np.sqrt(212.5))
        eq_(no_points.data[0], 50)


class TestNNGridded(unittest.TestCase):
    def test_basic_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_gridded, DummyConstraint

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    def test_already_colocated_in_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_gridded, DummyConstraint

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = UngriddedData.from_points_array([HyperPoint(0.0, 0.0)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)

    def test_coordinates_exactly_between_points_in_col_gridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                Iris seems to count a point as 'belonging' to a datapoint if it is greater than a datapoint cell's lower
                bound and less than or equal to it's upper bound. Where a cell is an imaginary boundary around a
                datapoint which divides the grid.
        '''
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_gridded, DummyConstraint

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 7.0)
        eq_(new_data.data[3], 4.0)

    def test_coordinates_outside_grid_in_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_gridded, DummyConstraint

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    def test_basic_col_gridded_to_ungridded_in_2d_with_time(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_gridded, DummyConstraint
        import datetime as dt

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube_with_time())

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, t=dt.datetime(1984, 8, 28, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, t=dt.datetime(1984, 8, 31, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, t=dt.datetime(1984, 9, 2, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 51.0)
        eq_(new_data.data[1], 82.0)
        eq_(new_data.data[2], 28.0)


class TestNNHorizontal(unittest.TestCase):
    def test_basic_col_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0), HyperPoint(lat=4.0, lon=4.0), HyperPoint(lat=-4.0, lon=-4.0)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = UngriddedData.from_points_array([HyperPoint(0.0, 0.0)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_horizontal algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same  you would expect the first point to be chosen. This doesn't seem to always be the case but is
                probably down to floating points errors in the haversine calculation as these test points are pretty
                close together. This test is only really for documenting the behaviour for equidistant points.
        '''
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 11.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_horizontal, DummyConstraint

        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)


class TestNNTime(unittest.TestCase):
    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedColocator()
        with self.assertRaises(TypeError):
            new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]

    def test_basic_col_in_2d_with_time(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)
        eq_(new_data.data[1], 7.0)
        eq_(new_data.data[2], 10.0)

    def test_basic_col_with_time(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint
        import numpy as np

        ug_data = mock.make_MODIS_time_steps()

        ref = np.array([0.0, 1.0, 2.0, 3.0])

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149751.369618055))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149759.378055556, ))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149766.373969907))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=149776.375995371))
        sample_points = UngriddedData.from_points_array(sample_points)

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert (np.equal(new_data.data, ref).all())

    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()

        t0 = dt.datetime(1984, 8, 27)
        for d in xrange(15):
            sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=t0 + dt.timedelta(days=d)))
        sample_points = UngriddedData.from_points_array(sample_points)

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert (np.equal(new_data.data, np.arange(15) + 1.0).all())

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        '''
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_time, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1984, 8, 26)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1884, 8, 26)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, t=dt.datetime(1994, 8, 27)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 1.0)
        eq_(new_data.data[2], 15.0)


class TestNNAltitude(unittest.TestCase):

    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_altitude, DummyConstraint

        ug_data = mock.make_regular_4d_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedColocator()
        with self.assertRaises(TypeError):
            new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]

    def test_basic_col_in_4d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, alt=34.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, alt=89.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 6.0)
        eq_(new_data.data[1], 16.0)
        eq_(new_data.data[2], 46.0)

    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=80.0, t=dt.datetime(1984, 9, 4, 15, 54))])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 41.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        '''
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, alt=35.0, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 16.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_altitude, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=-12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=91.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, alt=890.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_altitude())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 46.0)
        eq_(new_data.data[2], 46.0)


class TestNNPressure(unittest.TestCase):

    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_pressure, DummyConstraint

        ug_data = mock.make_regular_4d_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedColocator()
        with self.assertRaises(TypeError):
            new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]

    def test_basic_col_in_4d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=1.0, lon=1.0, pres=12.0, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=4.0, lon=4.0, pres=34.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=-4.0, lon=-4.0, pres=89.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 6.0)
        eq_(new_data.data[1], 16.0)
        eq_(new_data.data[2], 46.0)

    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=80.0, t=dt.datetime(1984, 9, 4, 15, 54))])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 41.0)

    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_pressure algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        '''
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Choose a time at midday
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=0.0, lon=0.0, pres=8, t=dt.datetime(1984, 8, 29, 12))])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 1.0)

    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, nn_pressure, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=0.1, t=dt.datetime(1984, 8, 29, 8, 34)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=91.0, t=dt.datetime(1984, 9, 2, 1, 23)))
        sample_points.append(HyperPoint(lat=0.0, lon=0.0, pres=890.0, t=dt.datetime(1984, 9, 4, 15, 54)))
        sample_points = UngriddedData.from_points_array(sample_points)
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_pressure())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 46.0)
        eq_(new_data.data[2], 46.0)


class TestMean(unittest.TestCase):

    def test_basic_col_in_4d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, mean, DummyConstraint
        import datetime as dt

        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), mean())[0]
        eq_(new_data.data[0], 25.5)


class TestLi(unittest.TestCase):

    def test_basic_col_gridded_to_ungridded_using_li_in_2d(self):
        from jasmin_cis.col_implementations import GeneralUngriddedColocator, li, DummyConstraint

        cube = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(1.0, 1.0), HyperPoint(4.0, 4.0), HyperPoint(-4.0, -4.0)])
        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), li())[0]
        assert_almost_equal(new_data.data[0], 8.8)
        assert_almost_equal(new_data.data[1], 11.2)
        assert_almost_equal(new_data.data[2], 4.8)


if __name__ == '__main__':
    unittest.main()
