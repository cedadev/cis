from unittest import TestCase
from hamcrest import assert_that, is_, instance_of
from mock import MagicMock

from jasmin_cis.data_io.ungridded_data import UngriddedData, UngriddedDataList
from jasmin_cis.data_io.gridded_data import GriddedData, GriddedDataList, make_from_cube
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

    def test_GIVEN_wildcards_WHEN_read_data_THEN_matching_variables_identified(self):
        variables = ['*.nc', 'test?.hdf']
        file_vars = ['aeronet.lev20', 'var2.hdf', 'netcdf1.nc', 'netcdf3.nc', 'test.hdf', 'test1.hdf']
        should_match = ['netcdf1.nc', 'netcdf3.nc', 'test1.hdf']
        filenames = 'filename1'
        get_data_func = MagicMock(return_value=make_regular_2d_ungridded_data())
        get_var_func = MagicMock(return_value=file_vars)
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        reader.read_data(filenames, variables)
        assert_that(reader._get_data_func.call_count, is_(len(should_match)))
        for i in range(len(should_match)):
            assert_that(reader._get_data_func.call_args_list[i][0][1], is_(should_match[i]))

    def test_GIVEN_no_matching_variables_for_wildcards_WHEN_read_data_THEN_no_Error(self):
        variables = ['aeronet.lev20', '*.nc', 'test?.hdf']
        file_vars = ['aeronet.lev20', 'var2.hdf']
        filenames = 'filename1'
        get_data_func = MagicMock(return_value=make_regular_2d_ungridded_data())
        get_var_func = MagicMock(return_value=file_vars)
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        reader.read_data(filenames, variables)
        assert_that(reader._get_data_func.call_count, is_(1))
        assert_that(reader._get_data_func.call_args_list[0][0][1], is_('aeronet.lev20'))

    def test_GIVEN_no_matching_variables_found_overall_WHEN_read_data_THEN_raises_Error(self):
        variables = ['test?.hdf', '*.nc']
        file_vars = ['sample_file.hdf', 'aeronet.lev20']
        filenames = 'filename1'
        get_data_func = MagicMock()
        get_var_func = MagicMock(return_value=file_vars)
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        with self.assertRaises(ValueError):
            reader.read_data(filenames, variables)

    def test_GIVEN_multiple_datagroups_WHEN_read_datagroups_THEN_get_data_called_correctly(self):
        datagroup_1 = {'variables': ['var1', 'var2'],
                       'filenames': ['filename1.nc'],
                       'product': None}
        datagroup_2 = {'variables': ['var3', 'var4'],
                       'filenames': ['filename2.nc'],
                       'product': 'cis'}
        get_data_func = MagicMock(return_value=make_regular_2d_ungridded_data())
        get_var_func = MagicMock(side_effect=lambda f: {'filename1.nc': ['var1', 'var2'],
                                                        'filename2.nc': ['var3', 'var4']}[f])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup_1, datagroup_2])
        assert_that(get_data_func.call_count, is_(4))
        assert_that(get_data_func.call_args_list[0][0], is_((['filename1.nc'], 'var1', None)))
        assert_that(get_data_func.call_args_list[1][0], is_((['filename1.nc'], 'var2', None)))
        assert_that(get_data_func.call_args_list[2][0], is_((['filename2.nc'], 'var3', 'cis')))
        assert_that(get_data_func.call_args_list[3][0], is_((['filename2.nc'], 'var4', 'cis')))

    def test_GIVEN_ungridded_datagroups_with_different_num_vars_WHEN_read_datagroups_THEN_data_returned_in_list(self):
        datagroup_1 = {'variables': ['var1', 'var2'],
                       'filenames': ['filename1.nc'],
                       'product': None}
        datagroup_2 = {'variables': ['var3'],
                       'filenames': ['filename2.nc'],
                       'product': 'cis'}
        var1 = make_regular_2d_ungridded_data()
        var2 = make_regular_2d_ungridded_data()
        var3 = make_regular_2d_ungridded_data()
        get_data_func = MagicMock(side_effect=[var1, var2, var3])
        get_var_func = MagicMock(side_effect=lambda f: {'filename1.nc': ['var1', 'var2'],
                                                        'filename2.nc': ['var3']}[f])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup_1, datagroup_2])
        assert_that(isinstance(data, UngriddedDataList))
        assert_that(len(data), is_(3))
        assert_that(data[0], is_(var1))
        assert_that(data[1], is_(var2))
        assert_that(data[2], is_(var3))

    def test_GIVEN_gridded_datagroups_WHEN_read_datagroups_THEN_data_returned_in_list(self):
        datagroup_1 = {'variables': ['var1', 'var2'],
                       'filenames': ['filename1.nc'],
                       'product': None}
        datagroup_2 = {'variables': ['var3'],
                       'filenames': ['filename2.nc'],
                       'product': 'cis'}
        var1 = make_from_cube(make_square_5x3_2d_cube())
        var2 = make_from_cube(make_square_5x3_2d_cube())
        var3 = make_from_cube(make_square_5x3_2d_cube())
        get_data_func = MagicMock(side_effect=[var1, var2, var3])
        get_var_func = MagicMock(side_effect=lambda f: {'filename1.nc': ['var1', 'var2'],
                                                        'filename2.nc': ['var3']}[f])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup_1, datagroup_2])
        assert_that(isinstance(data, GriddedDataList))
        assert_that(len(data), is_(3))
        assert_that(data[0], is_(var1))
        assert_that(data[1], is_(var2))
        assert_that(data[2], is_(var3))

    def test_GIVEN_gridded_and_ungridded_datagroups_WHEN_read_datagroups_THEN_raises_TypeError(self):
        datagroup_1 = {'variables': ['var1'],
                       'filenames': ['filename1.nc'],
                       'product': None}
        datagroup_2 = {'variables': ['var3'],
                       'filenames': ['filename2.nc'],
                       'product': 'cis'}
        var1 = make_from_cube(make_square_5x3_2d_cube())
        var2 = make_regular_2d_ungridded_data()
        get_data_func = MagicMock(side_effect=[var1, var2])
        get_var_func = MagicMock(side_effect=lambda f: {'filename1.nc': ['var1'],
                                                        'filename2.nc': ['var3']}[f])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        with self.assertRaises(TypeError):
            reader.read_datagroups([datagroup_1, datagroup_2])

    def test_GIVEN_aliases_None_WHEN_read_datagroups_THEN_read_OK_aliases_default_to_var_names(self):
        datagroup = {'variables': ['var1'],
                     'filenames': ['filename1.nc'],
                     'product': None,
                     'aliases': None}
        var1 = make_from_cube(make_square_5x3_2d_cube())
        get_data_func = MagicMock(side_effect=[var1])
        get_var_func = MagicMock(side_effect=['var1'])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup])
        assert_that(data[0].var_name, is_('dummy'))

    def test_GIVEN_aliases_missing_WHEN_read_datagroups_THEN_read_OK_aliases_default_to_var_names(self):
        datagroup = {'variables': ['var1'],
                     'filenames': ['filename1.nc'],
                     'product': None}
        var1 = make_from_cube(make_square_5x3_2d_cube())
        get_data_func = MagicMock(side_effect=[var1])
        get_var_func = MagicMock(side_effect=['var1'])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup])
        assert_that(data[0].var_name, is_('dummy'))

    def test_GIVEN_not_enough_aliases_WHEN_read_datagroups_THEN_raises_ValueError(self):
        datagroup = {'variables': ['var1', 'var2'],
                     'filenames': ['filename1.nc'],
                     'product': None,
                     'aliases': ['alias1']}
        var1 = make_from_cube(make_square_5x3_2d_cube())
        var2 = make_from_cube(make_square_5x3_2d_cube())
        get_data_func = MagicMock(side_effect=[var1, var2])
        get_var_func = MagicMock(side_effect=['var1', 'var2'])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        with self.assertRaises(ValueError):
            data = reader.read_datagroups([datagroup])

    def test_GIVEN_aliases_WHEN_read_datagroups_THEN_output_data_has_aliases(self):
        datagroup = {'variables': ['var1'],
                     'filenames': ['filename1.nc'],
                     'product': None,
                     'aliases': ['alias1']}
        get_data_func = MagicMock(return_value=make_from_cube(make_square_5x3_2d_cube()))
        get_var_func = MagicMock(return_value=['var1'])
        reader = DataReader(get_data_func=get_data_func, get_variables_func=get_var_func)
        data = reader.read_datagroups([datagroup])
        assert_that(data[0].alias, is_('alias1'))