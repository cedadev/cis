'''
 Module to test the colocation routines
'''
from nose.tools import istest, eq_, assert_almost_equal, raises
from jasmin_cis.exceptions import ClassNotFoundError
from test_util import mock


def is_colocated(data1, data2):
    '''
        Checks wether two datasets share all of the same points, this might be useful
        to determine if colocation is necesary or completed succesfully
    '''
    colocated = len(data1) == len(data2)
    if colocated:
        for i, point1 in enumerate(data1):
            colocated = point1.same_point_in_space_and_time(data2[i])
            if not colocated:
                return colocated
    return colocated


class ColocatorTests(object):
    pass


class TestDefaultColocator(ColocatorTests):
    pass


class TestAverageColocator(ColocatorTests):

    @istest
    @raises(ClassNotFoundError)
    def should_throw_error_if_full_average_kernel_is_not_used(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import AverageColocator, mean, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34)))

        col = AverageColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), mean())


    @istest
    def test_basic_col_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import AverageColocator, full_average, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34)))

        col = AverageColocator(stddev_name='my_std_dev',nopoints_name='my_no_points')
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), full_average())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.name(), 'rain_mean')
        eq_(std_dev.name(), 'my_std_dev')
        eq_(no_points.name(), 'my_no_points')


class TestDifferenceColocator(ColocatorTests):

    @istest
    def test_basic_col_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DifferenceColocator, mean, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34),25.0))

        col = DifferenceColocator(diff_name='my_diff')
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), mean())
        values = new_data[0]
        differences = new_data[1]

        eq_(values.name(), 'rain')
        eq_(differences.name(), 'my_diff')
        eq_(values.data[0],25.5)
        eq_(differences.data[0],0.5)



class KernelTests(object):
    pass


class Test_full_average(KernelTests):

    @istest
    def test_basic_col_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import AverageColocator, full_average, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34)))

        col = AverageColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), full_average())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.data[0], 25.5)
        assert_almost_equal(std_dev.data[0], 14.4308696897)
        eq_(no_points.data[0], 50)


class Test_nn_gridded(KernelTests):

    @istest
    def test_basic_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_gridded, DummyConstraint
        cube = mock.make_square_5x3_2d_cube()
        sample_points = [ HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    @istest
    def test_already_colocated_in_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_gridded, DummyConstraint
        cube = mock.make_square_5x3_2d_cube()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = [ HyperPoint(0.0, 0.0) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)

    @istest
    def test_coordinates_exactly_between_points_in_col_gridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                Iris seems to count a point as 'belonging' to a datapoint if it is greater than a datapoint cell's lower
                bound and less than or equal to it's upper bound. Where a cell is an imaginary boundary around a datapoint
                which divides the grid.
        '''
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_gridded, DummyConstraint
        cube = mock.make_square_5x3_2d_cube()
        sample_points = [ HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 7.0)
        eq_(new_data.data[3], 4.0)

    @istest
    def test_coordinates_outside_grid_in_col_gridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_gridded, DummyConstraint
        cube = mock.make_square_5x3_2d_cube()
        sample_points = [ HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    @istest
    def test_basic_col_gridded_to_ungridded_in_2d_with_time(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_gridded, DummyConstraint
        import datetime as dt
        cube = mock.make_square_5x3_2d_cube_with_time()

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,t=dt.datetime(1984,8,28,8,34)))
        sample_points.append(HyperPoint(4.0,4.0,t=dt.datetime(1984,8,31,1,23)))
        sample_points.append(HyperPoint(-4.0,-4.0,t=dt.datetime(1984,9,2,15,54)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), nn_gridded())[0]
        eq_(new_data.data[0], 51.0)
        eq_(new_data.data[1], 82.0)
        eq_(new_data.data[2], 28.0)


class Test_nn_horizontal(KernelTests):

    @istest
    def test_basic_col_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_horizontal, DummyConstraint
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = [HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0)]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)
        eq_(new_data.data[1], 12.0)
        eq_(new_data.data[2], 4.0)

    @istest
    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_horizontal, DummyConstraint
        ug_data = mock.make_regular_2d_ungridded_data()
        # This point already exists on the cube with value 5 - which shouldn't be a problem
        sample_points = [ HyperPoint(0.0, 0.0) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 8.0)

    @istest
    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_horizontal algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly the same
                you would expect the first point to be chosen. This doesn't seem to always be the case but is probably
                down to floating points errors in the haversine calculation as these test points are pretty close
                together. This test is only really for documenting the behaviour for equidistant points.
        '''
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_horizontal, DummyConstraint
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = [ HyperPoint(2.5, 2.5), HyperPoint(-2.5, 2.5), HyperPoint(2.5, -2.5), HyperPoint(-2.5, -2.5) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 11.0)
        eq_(new_data.data[1], 5.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

    @istest
    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_horizontal, DummyConstraint
        ug_data = mock.make_regular_2d_ungridded_data()
        sample_points = [ HyperPoint(5.5, 5.5), HyperPoint(-5.5, 5.5), HyperPoint(5.5, -5.5), HyperPoint(-5.5, -5.5) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_horizontal())[0]
        eq_(new_data.data[0], 12.0)
        eq_(new_data.data[1], 6.0)
        eq_(new_data.data[2], 10.0)
        eq_(new_data.data[3], 4.0)

class Test_nn_time(KernelTests):

    @istest
    @raises(TypeError)
    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = [HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0)]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]

    @istest
    def test_basic_col_in_2d_with_time(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,t=dt.datetime(1984,8,29,8,34)))
        sample_points.append(HyperPoint(4.0,4.0,t=dt.datetime(1984,9,2,1,23)))
        sample_points.append(HyperPoint(-4.0,-4.0,t=dt.datetime(1984,9,4,15,54)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)
        eq_(new_data.data[1], 7.0)
        eq_(new_data.data[2], 10.0)

    @istest
    def test_basic_col_with_time(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        import numpy as np

        ug_data = mock.make_MODIS_time_steps()

        ref = np.array([0.0,1.0,2.0,3.0])

        sample_points = HyperPointList()
        sample_points.append(HyperPoint(0.0, 0.0,t=149751.369618055))
        sample_points.append(HyperPoint(0.0,0.0,t=149759.378055556,))
        sample_points.append(HyperPoint(0.0,0.0,t=149766.373969907))
        sample_points.append(HyperPoint(0.0,0.0,t=149776.375995371))

        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert(np.equal(new_data.data,ref).all())

    @istest
    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        import datetime as dt
        import numpy as np
        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()

        t0 = dt.datetime(1984,8,27)
        for d in xrange(15):
            sample_points.append(HyperPoint(0.0, 0.0,t=t0+dt.timedelta(days=d)))

        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        assert(np.equal(new_data.data,np.arange(15)+1.0).all())

    @istest
    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        '''
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        # Choose a time at midday
        sample_points.append(HyperPoint(0.0,0.0,t=dt.datetime(1984,8,29,12)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 3.0)

    @istest
    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_time, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_2d_with_time_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(0.0,0.0,t=dt.datetime(1984,8,26)))
        sample_points.append(HyperPoint(0.0,0.0,t=dt.datetime(1884,8,26)))
        sample_points.append(HyperPoint(0.0,0.0,t=dt.datetime(1994,8,27)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_time())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 1.0)
        eq_(new_data.data[2], 15.0)


class Test_nn_altitude(KernelTests):

    @istest
    @raises(TypeError)
    def test_basic_col_with_incompatible_points_throws_a_TypeError(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import DefaultColocator, nn_vertical, DummyConstraint
        ug_data = mock.make_regular_4d_ungridded_data()
        # Make sample points with no time dimension specified
        sample_points = [HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0)]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_vertical())[0]

    @istest
    def test_basic_col_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_vertical, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34)))
        sample_points.append(HyperPoint(4.0,4.0,34.0,dt.datetime(1984,9,2,1,23)))
        sample_points.append(HyperPoint(-4.0,-4.0,89.0,dt.datetime(1984,9,4,15,54)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_vertical())[0]
        eq_(new_data.data[0], 6.0)
        eq_(new_data.data[1], 16.0)
        eq_(new_data.data[2], 46.0)

    @istest
    def test_already_colocated_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_vertical, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(0.0,0.0,80.0,dt.datetime(1984,9,4,15,54)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_vertical())[0]
        eq_(new_data.data[0], 41.0)

    @istest
    def test_coordinates_exactly_between_points_in_col_ungridded_to_ungridded_in_2d(self):
        '''
            This works out the edge case where the points are exactly in the middle or two or more datapoints.
                The nn_time algorithm will start with the first point as the nearest and iterates through the
                points finding any points which are closer than the current closest. If two distances were exactly
                the same the first point to be chosen.
        '''
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_vertical, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        # Choose a time at midday
        sample_points.append(HyperPoint(0.0,0.0,35.0,dt.datetime(1984,8,29,12)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_vertical())[0]
        eq_(new_data.data[0], 16.0)

    @istest
    def test_coordinates_outside_grid_in_col_ungridded_to_ungridded_in_2d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, nn_vertical, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(0.0, 0.0,-12.0,dt.datetime(1984,8,29,8,34)))
        sample_points.append(HyperPoint(0.0,0.0,91.0,dt.datetime(1984,9,2,1,23)))
        sample_points.append(HyperPoint(0.0,0.0,890.0,dt.datetime(1984,9,4,15,54)))
        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), nn_vertical())[0]
        eq_(new_data.data[0], 1.0)
        eq_(new_data.data[1], 46.0)
        eq_(new_data.data[2], 46.0)


class Test_mean(KernelTests):

    @istest
    def test_basic_col_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
        from jasmin_cis.col_implementations import DefaultColocator, mean, DummyConstraint
        import datetime as dt
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = HyperPointList()
        sample_points.append(HyperPoint(1.0, 1.0,12.0,dt.datetime(1984,8,29,8,34)))

        col = DefaultColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), mean())[0]
        eq_(new_data.data[0], 25.5)


class Test_li(KernelTests):

    @istest
    def test_basic_col_gridded_to_ungridded_using_li_in_2d(self):
        from jasmin_cis.col_implementations import DefaultColocator, li, DummyConstraint
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        cube = mock.make_square_5x3_2d_cube()
        sample_points = [ HyperPoint(1.0, 1.0), HyperPoint(4.0,4.0), HyperPoint(-4.0,-4.0) ]
        col = DefaultColocator()
        new_data = col.colocate(sample_points, cube, DummyConstraint(), li())[0]
        assert_almost_equal(new_data.data[0], 8.8)
        assert_almost_equal(new_data.data[1], 11.2)
        assert_almost_equal(new_data.data[2], 4.8)

class ConstraintTests(object):
    pass

class TestSepConstraint(ConstraintTests):

    @istest
    def test_all_constraint_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(0.0, 0.0, 50.0,dt.datetime(1984,8,29))

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        h_sep = 1000
        # 15m altitude seperation
        a_sep = 15
        # 1 day (and a little bit) time seperation
        t_sep = '1d1M'

        constraint = SepConstraint(h_sep = h_sep, a_sep = a_sep, t_sep = t_sep)

        # This should leave us with 9 points: [[ 22, 23, 24]
        #                                      [ 27, 28, 29]
        #                                      [ 32, 33, 34]]
        ref_vals = np.array([22,23,24,27,28,29,32,33,34])

        new_points = constraint.constrain_points(sample_point,ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_alt_constraint_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(0.0, 0.0, 50.0,dt.datetime(1984,8,29))

        # 15m altitude seperation
        a_sep = 15

        constraint = SepConstraint(a_sep=a_sep)

        # This should leave us with 15 points:   [ 21.  22.  23.  24.  25.]
        #                                       [ 26.  27.  28.  29.  30.]
        #                                       [ 31.  32.  33.  34.  35.]
        ref_vals = np.array([21.,22.,23.,24.,25.,26.,27.,28.,29.,30.,31.,32.,33.,34.,35.])

        new_points = constraint.constrain_points(sample_point,ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_horizontal_constraint_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(0.0, 0.0, 50.0,dt.datetime(1984,8,29))

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        #  in each direction
        constraint = SepConstraint(h_sep=1000)

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50)+1.0,(10,5))[:,1:4].flatten()

        new_points = constraint.constrain_points(sample_point,ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())

    @istest
    def test_time_constraint_in_4d(self):
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(0.0, 0.0, 50.0,dt.datetime(1984,8,29))

        # 1 day (and a little bit) time seperation
        constraint = SepConstraint(t_sep='1d1M')

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50)+1.0,(10,5))[:,1:4].flatten()

        new_points = constraint.constrain_points(sample_point,ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert(np.equal(ref_vals, new_vals).all())
