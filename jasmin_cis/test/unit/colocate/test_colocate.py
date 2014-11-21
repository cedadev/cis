"""
Tests the jasmin_cis.col.Colocate class
"""
import unittest
from hamcrest import assert_that, is_
from mock import MagicMock
from jasmin_cis.data_io import gridded_data
from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList

from jasmin_cis.col import Colocate, ColocatorFactory
from jasmin_cis.test.util import mock


class TestColocate(unittest.TestCase):

    def test_GIVEN_UngriddedData_WHEN_colocate_THEN_colocator_called_correctly(self):
        sample = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        out_name = 'output-name'
        col_name = 'box'
        col_options = {'h_sep': '1km', 'fill_value': '-999'}
        mock_colocator = MagicMock()
        mock_colocator.colocate = MagicMock(return_value=GriddedDataList([sample]))
        mock_constraint = MagicMock()
        mock_kernel = MagicMock()
        mock_colocator_factory = ColocatorFactory()
        mock_colocator_factory.get_colocator_instances_for_method = MagicMock(return_value=(mock_colocator,
                                                                                            mock_constraint,
                                                                                            mock_kernel))
        col = Colocate(sample, out_name, colocator_factory=mock_colocator_factory)
        data = mock.make_regular_2d_ungridded_data()
        output = col.colocate(data, col_name, col_options)

        assert_that(mock_colocator_factory.get_colocator_instances_for_method.call_count, is_(1))
        factory_call_args = mock_colocator_factory.get_colocator_instances_for_method.call_args_list[0][0]
        assert_that(factory_call_args[0], is_(col_name))
        assert_that(factory_call_args[1], is_(None))
        col_options['missing_data_for_missing_sample'] = False
        assert_that(factory_call_args[2], is_(col_options))
        assert_that(factory_call_args[3], is_(None))
        assert_that(factory_call_args[4], is_(True))
        assert_that(factory_call_args[5], is_(False))

        assert_that(mock_colocator.colocate.call_count, is_(1))
        colocator_args = mock_colocator.colocate.call_args_list[0][0]
        assert_that(colocator_args[0], is_(sample))
        assert_that(colocator_args[1], is_(data))
        assert_that(colocator_args[2], is_(mock_constraint))
        assert_that(colocator_args[3], is_(mock_kernel))

        assert_that(isinstance(output, GriddedDataList))
        assert_that(len(output), is_(1))
        assert_that(output[0].data.flatten().tolist(), is_(sample.data.flatten().tolist()))

    def test_GIVEN_UngriddedDataList_WHEN_colocate_THEN_colocator_called_correctly(self):
        sample = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        out_name = 'output-name'
        col_name = 'box'
        col_options = {'h_sep': '1km', 'fill_value': '-999'}
        mock_colocator = MagicMock()
        mock_colocator.colocate = MagicMock(return_value=GriddedDataList(2*[sample]))
        mock_constraint = MagicMock()
        mock_kernel = MagicMock()
        mock_colocator_factory = ColocatorFactory()
        mock_colocator_factory.get_colocator_instances_for_method = MagicMock(return_value=(mock_colocator,
                                                                                            mock_constraint,
                                                                                            mock_kernel))
        col = Colocate(sample, out_name, colocator_factory=mock_colocator_factory)
        data = UngriddedDataList(2*[mock.make_regular_2d_ungridded_data()])
        output = col.colocate(data, col_name, col_options)

        assert_that(mock_colocator_factory.get_colocator_instances_for_method.call_count, is_(1))
        factory_call_args = mock_colocator_factory.get_colocator_instances_for_method.call_args_list[0][0]
        assert_that(factory_call_args[0], is_(col_name))
        assert_that(factory_call_args[1], is_(None))
        col_options['missing_data_for_missing_sample'] = False
        assert_that(factory_call_args[2], is_(col_options))
        assert_that(factory_call_args[3], is_(None))
        assert_that(factory_call_args[4], is_(True))
        assert_that(factory_call_args[5], is_(False))

        assert_that(mock_colocator.colocate.call_count, is_(1))
        colocator_args = mock_colocator.colocate.call_args_list[0][0]
        assert_that(colocator_args[0], is_(sample))
        assert_that(colocator_args[1], is_(data))
        assert_that(colocator_args[2], is_(mock_constraint))
        assert_that(colocator_args[3], is_(mock_kernel))

        assert_that(isinstance(output, GriddedDataList))
        assert_that(len(output), is_(2))
        assert_that(output[0].data.flatten().tolist(), is_(sample.data.flatten().tolist()))

    def test_GIVEN_GriddedData_WHEN_colocate_THEN_colocator_called_correctly(self):
        sample = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        out_name = 'output-name'
        col_name = 'dummy'
        col_options = {}
        mock_colocator = MagicMock()
        mock_colocator.colocate = MagicMock(return_value=GriddedDataList([sample]))
        mock_constraint = MagicMock()
        mock_kernel = MagicMock()
        mock_colocator_factory = ColocatorFactory()
        mock_colocator_factory.get_colocator_instances_for_method = MagicMock(return_value=(mock_colocator,
                                                                                            mock_constraint,
                                                                                            mock_kernel))
        col = Colocate(sample, out_name, colocator_factory=mock_colocator_factory)
        data = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        output = col.colocate(data, col_name, col_options)

        assert_that(mock_colocator_factory.get_colocator_instances_for_method.call_count, is_(1))
        factory_call_args = mock_colocator_factory.get_colocator_instances_for_method.call_args_list[0][0]
        assert_that(factory_call_args[0], is_(col_name))
        assert_that(factory_call_args[1], is_(None))
        col_options['missing_data_for_missing_sample'] = False
        assert_that(factory_call_args[2], is_(col_options))
        assert_that(factory_call_args[3], is_(None))
        assert_that(factory_call_args[4], is_(True))
        assert_that(factory_call_args[5], is_(True))

        assert_that(mock_colocator.colocate.call_count, is_(1))
        colocator_args = mock_colocator.colocate.call_args_list[0][0]
        assert_that(colocator_args[0], is_(sample))
        assert_that(colocator_args[1], is_(data))
        assert_that(colocator_args[2], is_(mock_constraint))
        assert_that(colocator_args[3], is_(mock_kernel))

        assert_that(isinstance(output, GriddedDataList))
        assert_that(len(output), is_(1))
        assert_that(output[0].data.flatten().tolist(), is_(sample.data.flatten().tolist()))

    def test_GIVEN_GriddedDataList_WHEN_colocate_THEN_colocator_called_correctly(self):
        sample = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        out_name = 'output-name'
        col_name = 'dummy'
        col_options = {}
        mock_colocator = MagicMock()
        mock_colocator.colocate = MagicMock(return_value=GriddedDataList(2*[sample]))
        mock_constraint = MagicMock()
        mock_kernel = MagicMock()
        mock_colocator_factory = ColocatorFactory()
        mock_colocator_factory.get_colocator_instances_for_method = MagicMock(return_value=(mock_colocator,
                                                                                            mock_constraint,
                                                                                            mock_kernel))
        col = Colocate(sample, out_name, colocator_factory=mock_colocator_factory)
        data = GriddedDataList(2*[gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())])
        output = col.colocate(data, col_name, col_options)

        assert_that(mock_colocator_factory.get_colocator_instances_for_method.call_count, is_(1))
        factory_call_args = mock_colocator_factory.get_colocator_instances_for_method.call_args_list[0][0]
        assert_that(factory_call_args[0], is_(col_name))
        assert_that(factory_call_args[1], is_(None))
        col_options['missing_data_for_missing_sample'] = False
        assert_that(factory_call_args[2], is_(col_options))
        assert_that(factory_call_args[3], is_(None))
        assert_that(factory_call_args[4], is_(True))
        assert_that(factory_call_args[5], is_(True))

        assert_that(mock_colocator.colocate.call_count, is_(1))
        colocator_args = mock_colocator.colocate.call_args_list[0][0]
        assert_that(colocator_args[0], is_(sample))
        assert_that(colocator_args[1], is_(data))
        assert_that(colocator_args[2], is_(mock_constraint))
        assert_that(colocator_args[3], is_(mock_kernel))

        assert_that(isinstance(output, GriddedDataList))
        assert_that(len(output), is_(2))
        assert_that(output[0].data.flatten().tolist(), is_(sample.data.flatten().tolist()))