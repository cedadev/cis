"""
 Module to test the collocation routines
"""
import unittest
import datetime as dt

from nose.tools import eq_
import numpy as np

from cis.data_io.gridded_data import make_from_cube, GriddedDataList
from cis.collocation.col_implementations import GeneralUngriddedCollocator, DummyConstraint, moments, \
    SepConstraintKdtree
from cis.data_io.hyperpoint import HyperPoint
from cis.data_io.ungridded_data import UngriddedData, UngriddedDataList
from cis.test.util import mock


class TestGeneralUngriddedCollocator(unittest.TestCase):

    def test_averaging_basic_col_in_4d(self):
        ug_data = mock.make_regular_4d_ungridded_data()
        # Note - This isn't actually used for averaging
        sample_points = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34))])

        col = GeneralUngriddedCollocator()
        new_data = col.collocate(sample_points, ug_data, SepConstraintKdtree(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.name(), 'rainfall_flux')
        eq_(std_dev.name(), 'Corrected sample standard deviation of TOTAL RAINFALL RATE: LS+CONV KG/M2/S')
        eq_(no_points.name(), 'Number of points used to calculate the mean of TOTAL RAINFALL RATE: LS+CONV KG/M2/S')
        assert means.coords()
        assert std_dev.coords()
        assert no_points.coords()

    def test_ungridded_ungridded_box_moments(self):
        data = mock.make_regular_2d_ungridded_data()
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        col = GeneralUngriddedCollocator()
        output = col.collocate(sample, data, constraint, kernel)

        expected_result = np.array([28.0/3, 10.0, 20.0/3])
        expected_stddev = np.array([1.52752523, 1.82574186, 1.52752523])
        expected_n = np.array([3, 4, 3])
        assert len(output) == 3
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)
        assert np.allclose(output[1].data, expected_stddev)
        assert np.allclose(output[2].data, expected_n)

    def test_ungridded_ungridded_box_moments_missing_data_for_missing_sample(self):
        data = mock.make_regular_2d_ungridded_data()
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        sample_mask = [False, True, False]
        sample.data = np.ma.array([0, 0, 0], mask=sample_mask)

        col = GeneralUngriddedCollocator(missing_data_for_missing_sample=True)
        output = col.collocate(sample, data, constraint, kernel)

        assert len(output) == 3
        assert isinstance(output, UngriddedDataList)
        assert np.array_equal(output[0].data.mask, sample_mask)
        assert np.array_equal(output[1].data.mask, sample_mask)
        assert np.array_equal(output[2].data.mask, sample_mask)

    def test_ungridded_ungridded_box_moments_no_missing_data_for_missing_sample(self):
        data = mock.make_regular_2d_ungridded_data()
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        sample_mask = [False, True, False]
        sample.data = np.ma.array([0, 0, 0], mask=sample_mask)

        col = GeneralUngriddedCollocator(missing_data_for_missing_sample=False)
        output = col.collocate(sample, data, constraint, kernel)

        assert len(output) == 3
        assert isinstance(output, UngriddedDataList)
        assert not any(output[0].data.mask)
        assert not any(output[1].data.mask)
        assert not any(output[2].data.mask)

    def test_list_ungridded_ungridded_box_mean(self):
        ug_data_1 = mock.make_regular_2d_ungridded_data()
        ug_data_2 = mock.make_regular_2d_ungridded_data(data_offset=3)
        ug_data_2.long_name = 'TOTAL SNOWFALL RATE: LS+CONV KG/M2/S'
        ug_data_2.standard_name = 'snowfall_flux'
        ug_data_2.metadata._name = 'snow'

        data_list = UngriddedDataList([ug_data_1, ug_data_2])
        sample_points = mock.make_regular_2d_ungridded_data()
        constraint = SepConstraintKdtree('500km')
        kernel = moments()
        col = GeneralUngriddedCollocator()
        output = col.collocate(sample_points, data_list, constraint, kernel)

        expected_result = np.array(list(range(1, 16)))
        expected_n = np.array(15 * [1])
        assert len(output) == 6
        assert isinstance(output, UngriddedDataList)
        assert output[3].var_name == 'snow'
        assert output[4].var_name == 'snow_std_dev'
        assert output[5].var_name == 'snow_num_points'
        assert np.allclose(output[0].data, expected_result)
        assert all(output[1].data.mask)
        assert np.allclose(output[2].data, expected_n)
        assert np.allclose(output[3].data, expected_result + 3)
        assert all(output[4].data.mask)
        assert np.allclose(output[5].data, expected_n)

if __name__ == '__main__':
    import nose
    nose.runmodule()
