'''
 Module to test the colocation routines
'''
import unittest
from nose.tools import eq_
import datetime as dt
import numpy as np

from jasmin_cis.data_io.gridded_data import make_from_cube, GriddedDataList
from jasmin_cis.col_implementations import GeneralUngriddedColocator, DummyConstraint, moments, li, nn_h, \
    SepConstraintKdtree, mean, nn_gridded
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
        new_data = col.colocate(sample_points, ug_data, DummyConstraint(), moments())
        means = new_data[0]
        std_dev = new_data[1]
        no_points = new_data[2]

        eq_(means.name(), 'rain')
        eq_(std_dev.name(), 'rain_std_dev')
        eq_(no_points.name(), 'rain_num_points')
        assert means.coords()
        assert std_dev.coords()
        assert no_points.coords()

    def test_gridded_ungridded_nn(self):
        data = make_from_cube(mock.make_mock_cube())
        data.name = lambda: 'Name'
        data.var_name = 'var_name'
        data._standard_name = 'y_wind'
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = None
        kernel = nn_gridded()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data, constraint, kernel)

        expected_result = np.array([8, 12, 8])
        assert len(output) == 1
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)

    def test_gridded_ungridded_lin(self):
        data = make_from_cube(mock.make_mock_cube())
        data.name = lambda: 'Name'
        data.var_name = 'var_name'
        data._standard_name = 'y_wind'
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = None
        kernel = li()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data, constraint, kernel)

        expected_result = np.array([8.8, 10.4, 7.2])
        assert len(output) == 1
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)

    def test_gridded_ungridded_box_mean(self):
        data = make_from_cube(mock.make_mock_cube())
        data.name = lambda: 'Name'
        data.var_name = 'var_name'
        data._standard_name = 'y_wind'
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = mean()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data, constraint, kernel)

        expected_result = np.array([28.0/3, 10.0, 20.0/3])
        assert len(output) == 1
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)

    def test_gridded_ungridded_box_moments(self):
        data = make_from_cube(mock.make_mock_cube())
        data.name = lambda: 'Name'
        data.var_name = 'var_name'
        data._standard_name = 'y_wind'
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data, constraint, kernel)

        expected_result = np.array([28.0/3, 10.0, 20.0/3])
        expected_stddev = np.array([1.52752523, 1.82574186, 1.52752523])
        expected_n = np.array([3, 4, 3])
        assert len(output) == 3
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)
        assert np.allclose(output[1].data, expected_stddev)
        assert np.allclose(output[2].data, expected_n)

    def test_ungridded_ungridded_box_moments(self):
        data = mock.make_regular_2d_ungridded_data()
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data, constraint, kernel)

        expected_result = np.array([28.0/3, 10.0, 20.0/3])
        expected_stddev = np.array([1.52752523, 1.82574186, 1.52752523])
        expected_n = np.array([3, 4, 3])
        assert len(output) == 3
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)
        assert np.allclose(output[1].data, expected_stddev)
        assert np.allclose(output[2].data, expected_n)

    def test_list_ungridded_ungridded_box_mean(self):
        ug_data_1 = mock.make_regular_2d_ungridded_data()
        ug_data_2 = mock.make_regular_2d_ungridded_data(data_offset=3)
        ug_data_2.long_name = 'TOTAL SNOWFALL RATE: LS+CONV KG/M2/S'
        ug_data_2.standard_name = 'snowfall_rate'
        ug_data_2.metadata._name = 'snow'

        data_list = UngriddedDataList([ug_data_1, ug_data_2])
        sample_points = mock.make_regular_2d_ungridded_data()
        constraint = SepConstraintKdtree('500km')
        kernel = moments()
        col = GeneralUngriddedColocator()
        output = col.colocate(sample_points, data_list, constraint, kernel)

        expected_result = np.array(range(1, 16))
        expected_stddev = np.array(15 * [float('inf')])
        expected_n = np.array(15 * [1])
        assert len(output) == 6
        assert isinstance(output, UngriddedDataList)
        assert output[3].var_name == 'snow'
        assert output[4].var_name == 'snow_std_dev'
        assert output[5].var_name == 'snow_num_points'
        assert np.allclose(output[0].data, expected_result)
        assert np.allclose(output[1].data, expected_stddev)
        assert np.allclose(output[2].data, expected_n)
        assert np.allclose(output[3].data, expected_result + 3)
        assert np.allclose(output[4].data, expected_stddev)
        assert np.allclose(output[5].data, expected_n)

    def test_list_gridded_ungridded_box_moments(self):
        data1 = make_from_cube(mock.make_mock_cube())
        data1.name = lambda: 'Name1'
        data1.var_name = 'var_name1'
        data1._standard_name = 'y_wind'
        data2 = make_from_cube(mock.make_mock_cube(data_offset=3))
        data2.name = lambda: 'Name1'
        data2.var_name = 'var_name2'
        data2._standard_name = 'x_wind'
        data_list = GriddedDataList([data1, data2])
        sample = UngriddedData.from_points_array(
            [HyperPoint(lat=1.0, lon=1.0, alt=12.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=3.0, lon=3.0, alt=7.0, t=dt.datetime(1984, 8, 29, 8, 34)),
             HyperPoint(lat=-1.0, lon=-1.0, alt=5.0, t=dt.datetime(1984, 8, 29, 8, 34))])
        constraint = SepConstraintKdtree('500km')
        kernel = moments()

        col = GeneralUngriddedColocator()
        output = col.colocate(sample, data_list, constraint, kernel)

        expected_result = np.array([28.0/3, 10.0, 20.0/3])
        expected_stddev = np.array([1.52752523, 1.82574186, 1.52752523])
        expected_n = np.array([3, 4, 3])
        assert len(output) == 6
        assert isinstance(output, UngriddedDataList)
        assert np.allclose(output[0].data, expected_result)
        assert np.allclose(output[1].data, expected_stddev)
        assert np.allclose(output[2].data, expected_n)
        assert np.allclose(output[3].data, expected_result + 3)
        assert np.allclose(output[4].data, expected_stddev)
        assert np.allclose(output[5].data, expected_n)

if __name__ == '__main__':
    import nose
    nose.runmodule()
