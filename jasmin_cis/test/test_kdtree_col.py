import datetime as dt
from nose.tools import istest, eq_, assert_almost_equal, raises

import numpy as np

from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
from jasmin_cis.test.test_util import mock
from jasmin_cis.col_implementations import DefaultColocator, nn_horizontal_kdtree, DummyConstraint
from jasmin_cis.col_implementations import IndexedSepConstraint
from jasmin_cis.haversinedistancekdtreeindex import HaversineDistanceKDTreeIndex


def is_colocated(data1, data2):
    """
    Checks whether two datasets share all of the same points, this might be useful
    to determine if colocation is necessary or completed successfully
    """
    colocated = len(data1) == len(data2)
    if colocated:
        for i, point1 in enumerate(data1):
            colocated = point1.same_point_in_space_and_time(data2[i])
            if not colocated:
                return colocated
    return colocated


class Test_nn_horizontal_kdtree(object):

    @istest
    def test_basic_col_in_2d(self):
        # lat: -10 to 10 step 5; lon -5 to 5 step 5
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = mock.MockUngriddedData(
            [HyperPoint(lat=1.0, lon=1.0), HyperPoint(lat=4.0, lon=4.0), HyperPoint(lat=-4.0, lon=-4.0)])
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(fill_value=-999), nn_horizontal_kdtree())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    @istest
    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        ug_data = mock.make_regular_2d_ungridded_data()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = mock.MockUngriddedData([HyperPoint(0.0, 0.0)])
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(fill_value=-999), nn_horizontal_kdtree())[0]
        eq_(new_data.data[0], 8.0)

    @istest
    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        """
        This works out the edge case where the points are exactly in the middle or two or more datapoints.
        The nn_horizontal algorithm will start with the first point as the nearest and iterates through the
        points finding any points which are closer than the current closest. If two distances were exactly the same
        you would expect the first point to be chosen. This doesn't seem to always be the case but is probably
        down to floating points errors in the haversine calculation as these test points are pretty close
        together. This test is only really for documenting the behaviour for equidistant points.
        """
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = mock.MockUngriddedData([HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5),
                                                HyperPoint(-2.5, -2.5)])
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(fill_value=-999), nn_horizontal_kdtree())[0]
        eq_(new_data.data[0], 11.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    @istest
    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = mock.MockUngriddedData([HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5),
                                                HyperPoint(-5.5, -5.5)])
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(fill_value=-999), nn_horizontal_kdtree())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)


class TestSepConstraint(object):
    @istest
    def test_horizontal_constraint_in_2d(self):
        ug_data = mock.make_regular_2d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=7.5, lon=-2.5)
        sample_points = HyperPointList([sample_point])
        coord_map = None

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = IndexedSepConstraint(h_sep=400)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(sample_points, ug_data_points, coord_map, leafsize=2)
        constraint.haversine_distance_kd_tree_index = index

        # This should leave us with 4 points
        ref_vals = np.array([10, 11, 13, 14])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_horizontal_constraint_in_2d_with_missing_values(self):
        ug_data = mock.make_regular_2d_ungridded_data_with_missing_values()
        ug_data_points = ug_data.get_non_masked_points()
        coord_map = None

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = IndexedSepConstraint(h_sep=400)

        index = HaversineDistanceKDTreeIndex()
        sample_points = None  # Not used
        index.index_data(sample_points, ug_data_points, coord_map, leafsize=2)
        constraint.haversine_distance_kd_tree_index = index

        for sample_point in ug_data.get_all_points():
            new_points = constraint.constrain_points(sample_point, ug_data_points)
            new_vals = new_points.vals
            if sample_point.val[0] is np.ma.masked:
                ref_vals = np.array([])
            else:
                ref_vals = np.array([sample_point.val])

            eq_(ref_vals.size, new_vals.size)
            assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_horizontal_constraint_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, t=dt.datetime(1984, 8, 29))
        sample_points = HyperPointList([sample_point])
        coord_map = None

        # Constraint distance selects the central three points.
        constraint = IndexedSepConstraint(h_sep=1000)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(sample_points, ug_data_points, coord_map)
        constraint.haversine_distance_kd_tree_index = index

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50)+1.0, (10, 5))[:, 1:4].flatten()

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = np.sort(new_points.vals)

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_all_constraints_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, pres=50.0, t=dt.datetime(1984, 8, 29))

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        h_sep = 1000
        # 15m altitude separation
        a_sep = 15
        # 1 day (and a little bit) time separation
        t_sep = '1d1M'
        # Pressure constraint is 50/40 < p_sep < 60/50
        p_sep = 1.22

        constraint = IndexedSepConstraint(h_sep=h_sep, a_sep=a_sep, p_sep=p_sep, t_sep=t_sep)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(None, ug_data_points, None)
        constraint.haversine_distance_kd_tree_index = index

        # This should leave us with 9 points: [[ 22, 23, 24]
        #                                      [ 27, 28, 29]
        #                                      [ 32, 33, 34]]
        ref_vals = np.array([27., 28., 29., 32., 33., 34.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = np.sort(new_points.vals)

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())


if __name__ == '__main__':
    import nose
    nose.runmodule()
