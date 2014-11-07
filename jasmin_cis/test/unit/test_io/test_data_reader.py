from unittest import TestCase
from hamcrest import assert_that, is_, instance_of
from mock import MagicMock

from jasmin_cis.data_io.ungridded_data import UngriddedData, UngriddedDataList
from jasmin_cis.data_io.gridded_data import GriddedData, GriddedDataList
from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.test.util.mock import make_square_5x3_2d_cube, make_regular_2d_ungridded_data


class TestDataReader(TestCase):

    def test_GIVEN_single_variable_gridded_WHEN_read_data_THEN_GriddedData_returned(self):
        variables = 'var1'
        filenames = 'filename1'
        product = None
        gridded_data = make_square_5x3_2d_cube()
        gridded_data.__class__ = GriddedData
        get_data_func = MagicMock(return_value=gridded_data)
        reader = DataReader(get_data_func=get_data_func)
        data = reader.read_data(filenames, variables, product)

        # Check the data read function is called correctly
        assert_that(get_data_func.call_count, is_(1))
        call_args = get_data_func.call_args_list[0][0]
        assert_that(call_args[0], is_([filenames]))
        assert_that(call_args[1], is_(variables))
        assert_that(call_args[2], is_(product))

        # Check the data we got back is as expected
        assert_that(data, instance_of(GriddedData))
        assert_that(data.data.tolist(), is_(make_square_5x3_2d_cube().data.tolist()))

    def test_GIVEN_single_variable_ungridded_WHEN_read_data_THEN_GriddedData_returned(self):
        variables = 'var1'
        filenames = 'filename1'
        product = None
        get_data_func = MagicMock(return_value=make_regular_2d_ungridded_data())
        reader = DataReader(get_data_func=get_data_func)
        data = reader.read_data(filenames, variables, product)

        # Check the data read function is called correctly
        assert_that(get_data_func.call_count, is_(1))
        call_args = get_data_func.call_args_list[0][0]
        assert_that(call_args[0], is_([filenames]))
        assert_that(call_args[1], is_(variables))
        assert_that(call_args[2], is_(product))

        # Check the data we got back is as expected
        assert_that(data, instance_of(UngriddedData))
        assert_that(data.data.tolist(), is_(make_regular_2d_ungridded_data().data.tolist()))

    def test_GIVEN_multiple_variable_gridded_WHEN_read_data_THEN_GriddedDataList_returned(self):
        variables = ['var1', 'var2']
        filenames = 'filename1'
        product = None
        gridded_data = make_square_5x3_2d_cube()
        gridded_data.__class__ = GriddedData
        get_data_func = MagicMock(return_value=gridded_data)
        reader = DataReader(get_data_func=get_data_func)
        data = reader.read_data(filenames, variables, product)

        # Check the data read function is called correctly
        assert_that(get_data_func.call_count, is_(2))
        first_call_args = get_data_func.call_args_list[0][0]
        second_call_args = get_data_func.call_args_list[1][0]
        assert_that(first_call_args[0], is_([filenames]))
        assert_that(first_call_args[1], is_(variables[0]))
        assert_that(second_call_args[1], is_(variables[1]))
        assert_that(first_call_args[2], is_(product))

        # Check the data we got back is as expected
        assert_that(data, instance_of(GriddedDataList))
        assert_that(data[0].data.tolist(), is_(make_square_5x3_2d_cube().data.tolist()))
        assert_that(data[1].data.tolist(), is_(data[0].data.tolist()))

    def test_GIVEN_multiple_variable_ungridded_WHEN_read_data_THEN_GriddedDataList_returned(self):
        variables = ['var1', 'var2']
        filenames = 'filename1'
        product = None
        get_data_func = MagicMock(return_value=make_regular_2d_ungridded_data())
        reader = DataReader(get_data_func=get_data_func)
        data = reader.read_data(filenames, variables, product)

        # Check the data read function is called correctly
        assert_that(get_data_func.call_count, is_(2))
        first_call_args = get_data_func.call_args_list[0][0]
        second_call_args = get_data_func.call_args_list[1][0]
        assert_that(first_call_args[0], is_([filenames]))
        assert_that(first_call_args[1], is_(variables[0]))
        assert_that(second_call_args[1], is_(variables[1]))
        assert_that(first_call_args[2], is_(product))

        # Check the data we got back is as expected
        assert_that(data, instance_of(UngriddedDataList))
        assert_that(data[0].data.tolist(), is_(make_regular_2d_ungridded_data().data.tolist()))
        assert_that(data[1].data.tolist(), is_(data[0].data.tolist()))

    def test_GIVEN_multiple_variable_mix_of_gridded_ungridded_WHEN_read_data_THEN_raises_TypeError(self):
        variables = ['var1', 'var2']
        filenames = 'filename1'
        product = None
        gridded_data = make_square_5x3_2d_cube()
        gridded_data.__class__ = GriddedData
        ungridded_data = make_regular_2d_ungridded_data()
        get_data_func = MagicMock(side_effect=[gridded_data, ungridded_data])
        reader = DataReader(get_data_func=get_data_func)
        with self.assertRaises(TypeError):
            data = reader.read_data(filenames, variables, product)