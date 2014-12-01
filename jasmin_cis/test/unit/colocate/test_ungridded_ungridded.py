'''
 Module to test the colocation routines
'''
import unittest
from nose.tools import eq_
import datetime as dt

from jasmin_cis.col_implementations import GeneralUngriddedColocator, DummyConstraint, moments
from jasmin_cis.data_io.hyperpoint import HyperPoint
from jasmin_cis.data_io.ungridded_data import UngriddedData, UngriddedDataList
from jasmin_cis.test.util import mock


class TestGeneralUngriddedColocator(unittest.TestCase):

    def test_averaging_basic_col_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedColocator()
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(),
                                moments(stddev_name='my_std_dev', nopoints_name='my_no_points'))
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.name(), 'rain_mean')
        eq_(std_dev.name(), 'my_std_dev')
        eq_(no_points.name(), 'my_no_points')

    def test_colocate_with_list_of_data_raises_NotImplementedError(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        data_list = UngriddedDataList(2*[ug_data])
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedColocator()
        with self.assertRaises(NotImplementedError):
            new_data = col.colocate(sample_points, data_list, DummyConstraint(),
                                    moments(stddev_name='my_std_dev', nopoints_name='my_no_points'))


if __name__ == '__main__':
    import nose
    nose.runmodule()
