import datetime as dt
import pandas as pd

from hamcrest import *
from nose.tools import istest, eq_
import numpy as np
from cis.collocation.kdtree import KDTree
from cis.time_util import cis_standard_time_unit
import cis.data_io.gridded_data as gridded_data
from cis.data_io.hyperpoint import HyperPoint, HyperPointList
from cis.data_io.ungridded_data import UngriddedData
from cis.test.util import mock
from cis.collocation.col_implementations import (GeneralUngriddedCollocator, nn_horizontal_only, DummyConstraint,
                                                 SepConstraintKdtree, make_coord_map)
from cis.collocation.haversinedistancekdtreeindex import HaversineDistanceKDTreeIndex


def is_collocated(data1, data2):
    """
    Checks whether two datasets share all of the same points, this might be useful
    to determine if collocation is necessary or completed successfully
    """
    collocated = len(data1) == len(data2)
    if collocated:
        for i, point1 in enumerate(data1):
            collocated = point1.same_point_in_space_and_time(data2[i])
            if not collocated:
                return collocated
    return collocated


class Test_nn_horizontal_kdtree(object):
    @istest
    def test_basic_col_in_2d(self):
        # lat: -10 to 10 step 5; lon -5 to 5 step 5
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0), HyperPoint(lat=4.0, lon=4.0), HyperPoint(lat=-4.0, lon=-4.0)])
        col = GeneralUngriddedCollocator(fill_value=-999)
        new_data = col.collocate(sample_points, ug_data, SepConstraintKdtree(), nn_horizontal_only())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    @istest
    def test_already_collocated_in_col_ungridded_to_ungridded_in_2d(self):
        ug_data = mock.make_regular_2d_ungridded_data()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = UngriddedData.from_points_array([HyperPoint(0.0, 0.0)])
        col = GeneralUngriddedCollocator(fill_value=-999)
        new_data = col.collocate(sample_points, ug_data, SepConstraintKdtree(), nn_horizontal_only())[0]
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
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5),
             HyperPoint(-2.5, -2.5)])
        col = GeneralUngriddedCollocator(fill_value=-999)
        new_data = col.collocate(sample_points, ug_data, SepConstraintKdtree(), nn_horizontal_only())[0]
        eq_(new_data.data[0], 11.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    @istest
    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5),
             HyperPoint(-5.5, -5.5)])
        col = GeneralUngriddedCollocator(fill_value=-999)
        new_data = col.collocate(sample_points, ug_data, SepConstraintKdtree(), nn_horizontal_only())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)


class TestSepConstraint(object):
    @istest
    def test_horizontal_constraint_in_2d(self):
        from cis.data_io.Coord import Coord, CoordList
        from cis.data_io.ungridded_data import Metadata
        ug_data = mock.make_regular_2d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_points = UngriddedData(np.array([0.0]), Metadata(),
                                      CoordList([Coord(np.array([7.5]), Metadata(standard_name='latitude')),
                                                 Coord(np.array([-2.5]), Metadata(standard_name='longitude'))]))
        sample_points_view = sample_points.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        # sample_point = HyperPoint(lat=7.5, lon=-2.5)
        # sample_points = HyperPointList([sample_point])
        coord_map = None

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = SepConstraintKdtree(h_sep=400)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(sample_points, ug_data_points, coord_map, leafsize=2)
        constraint.haversine_distance_kd_tree_index = index

        # This should leave us with 4 points
        ref_vals = np.array([10, 11, 13, 14])

        indices = constraint.haversine_distance_kd_tree_index.find_points_within_distance_sample(sample_points_view, 400)

        new_vals = ug_data.data.flat[indices]

        eq_(ref_vals.size, len(new_vals[0]))
        assert (np.equal(ref_vals, new_vals).all())

    @istest
    def test_horizontal_constraint_in_2d_with_missing_values(self):
        ug_data = mock.make_regular_2d_ungridded_data_with_missing_values()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=0)
        coord_map = None

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = SepConstraintKdtree(h_sep=400)

        index = HaversineDistanceKDTreeIndex()
        sample_points = None  # Not used
        index.index_data(sample_points, ug_data_points, coord_map, leafsize=2)
        constraint.haversine_distance_kd_tree_index = index

        for i, sample_point in ug_data.as_data_frame(time_index=False, name='vals').iterrows():
            new_points = constraint.constrain_points(sample_point, ug_data_points)
            new_vals = new_points.vals
            if np.isnan(sample_point.vals):
                ref_vals = np.array([])
            else:
                ref_vals = np.array([sample_point.vals])

            eq_(ref_vals.size, new_vals.size)
            assert (np.equal(ref_vals, new_vals).all())

    @istest
    def test_horizontal_constraint_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_points = pd.DataFrame(data={'longitude': [0.0], 'latitude': [0.0], 'altitude': [50.0],
                                              'time': [dt.datetime(1984, 8, 29)]})
        coord_map = None

        # Constraint distance selects the central three points.
        constraint = SepConstraintKdtree(h_sep=1000)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(sample_points, ug_data_points, coord_map)
        constraint.haversine_distance_kd_tree_index = index

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50) + 1.0, (10, 5))[:, 1:4].flatten()

        new_points = constraint.constrain_points(sample_points.iloc[0], ug_data_points)
        new_vals = np.sort(new_points.vals)

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    @istest
    def test_all_constraints_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_point = pd.DataFrame(data={'longitude': [0.0], 'latitude': [0.0], 'altitude': [50.0],
                                          'air_pressure': [50.0],
                                          'time': [cis_standard_time_unit.date2num(dt.datetime(1984, 8, 29))]}).iloc[0]
        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        h_sep = 1000
        # 15m altitude separation
        a_sep = 15
        # 1 day (and a little bit) time separation
        t_sep = 'P1dT1M'
        # Pressure constraint is 50/40 < p_sep < 60/50
        p_sep = 1.22

        constraint = SepConstraintKdtree(h_sep=h_sep, a_sep=a_sep, p_sep=p_sep, t_sep=t_sep)

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
        assert (np.equal(ref_vals, new_vals).all())

    def get_max_depth(self, node, depth):
        if isinstance(node, KDTree.leafnode):
            return depth
        return max(self.get_max_depth(node.less, depth + 1), self.get_max_depth(node.greater, depth + 1))

    @istest
    def test_horizontal_constraint_in_2d_when_lats_are_the_same_produces_a_balanced_tree(self):
        ug_data = mock.make_regular_2d_ungridded_data(lat_dim_length=1001, lat_max=10, lat_min=10)
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_points = pd.DataFrame(data={'longitude': [-2.5], 'latitude': [7.5]})
        coord_map = None

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = SepConstraintKdtree(h_sep=400)

        index = HaversineDistanceKDTreeIndex()
        index.index_data(sample_points, ug_data_points, coord_map, leafsize=2)

        depth = self.get_max_depth(index.index.tree, 0)

        assert_that(depth, is_(2), "Depth is 2, there are three unique values -10, 0, 10")


class TestSepConstraintWithoutHorizontalSeparation(object):
    """Tests that SepConstraintKdtree behaves as an unoptimized constraint for non-spatial separations
    if the spatial separation parameter is not specified.
    """

    @istest
    def test_alt_constraint_in_4d(self):
        from cis.collocation.col_implementations import SepConstraintKdtree
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_point = pd.Series({'longitude': [0.0], 'latitude': [0.0], 'altitude':[50.0],
                                  'time': [cis_standard_time_unit.date2num(dt.datetime(1984, 8, 29))]})
        # 15m altitude separation
        a_sep = 15

        constraint = SepConstraintKdtree(a_sep=a_sep)

        # This should leave us with 15 points:  [ 21.  22.  23.  24.  25.]
        #                                       [ 26.  27.  28.  29.  30.]
        #                                       [ 31.  32.  33.  34.  35.]
        ref_vals = np.array([21., 22., 23., 24., 25., 26., 27., 28., 29., 30., 31., 32., 33., 34., 35.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    @istest
    def test_time_constraint_in_4d(self):
        from cis.collocation.col_implementations import SepConstraintKdtree
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_point = pd.Series({'longitude': [0.0], 'latitude': [0.0], 'altitude':[50.0],
                                  'time': [cis_standard_time_unit.date2num(dt.datetime(1984, 8, 29))]})

        # 1 day (and a little bit) time seperation
        constraint = SepConstraintKdtree(t_sep='P1dT1M')

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50) + 1.0, (10, 5))[:, 1:4].flatten()

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    @istest
    def test_pressure_constraint_in_4d(self):
        from cis.collocation.col_implementations import SepConstraintKdtree
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.as_data_frame(time_index=False, name='vals').dropna(axis=1)
        sample_point = pd.Series({'longitude': [0.0], 'latitude': [0.0], 'altitude':[50.0], 'air_pressure': [24.0],
                                  'time': [cis_standard_time_unit.date2num(dt.datetime(1984, 8, 29))]})
        constraint = SepConstraintKdtree(p_sep=2)

        # This should leave us with 20 points:  [  6.   7.   8.   9.  10.]
        #                                       [ 11.  12.  13.  14.  15.]
        #                                       [ 16.  17.  18.  19.  20.]
        #                                       [ 21.  22.  23.  24.  25.]
        ref_vals = np.array([6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23.,
                             24., 25.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())


if __name__ == '__main__':
    import nose

    nose.runmodule()
