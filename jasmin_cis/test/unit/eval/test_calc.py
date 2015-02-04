import unittest

from hamcrest import assert_that, is_, ends_with
import numpy

from jasmin_cis.data_io.gridded_data import make_from_cube, GriddedDataList, GriddedData
from jasmin_cis.evaluate import Calculator, EvaluationError
from jasmin_cis.test.util import mock
from jasmin_cis.test.utils_for_testing import compare_masked_arrays
from jasmin_cis.cis import __version__


class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = Calculator()
        self.data = GriddedDataList([make_from_cube(mock.make_mock_cube())])
        self.data[0].var_name = 'var_name'

    def _make_two_gridded(self):
        data1 = make_from_cube(mock.make_mock_cube())
        data2 = make_from_cube(mock.make_mock_cube(data_offset=10))
        data1.var_name = 'var1'
        data2._var_name = 'var2'
        data1.filenames = ['filename1']
        data2.filenames = ['filename2']
        self.data = [data1, data2]
        self.data = GriddedDataList([data1, data2])

    def _make_two_ungridded_data(self):
        data1 = mock.make_regular_2d_ungridded_data_with_missing_values()
        data2 = mock.make_regular_2d_ungridded_data_with_missing_values()
        data1.metadata._name = 'var1'
        data2.metadata._name = 'var2'
        data1.filenames = ['filename1']
        data2.filenames = ['filename2']
        self.data = [data1, data2]

    def test_GIVEN_expr_with_double_underscores_WHEN_calculate_THEN_raises_EvaluationError(self):
        expr = "[c for c in ().__class__.__base__.__subclasses__() if c.__name__ " \
               "== 'catch_warnings'][0]()._module.__builtins__['__import__']('os')"
        with self.assertRaises(EvaluationError):
            self.calc.evaluate(self.data, expr)

    def test_GIVEN_expr_using_disallowed_builtins_WHEN_calculate_THEN_raises_EvaluationError(self):
        expr = 'open("path")'
        with self.assertRaises(EvaluationError):
            self.calc.evaluate(self.data, expr)

    def test_GIVEN_expr_using_numpy_WHEN_calculate_THEN_allowed(self):
        expr = 'numpy.log(var_name)'
        self.calc.evaluate(self.data, expr)

    def test_GIVEN_expr_using_allowed_builtins_WHEN_calculate_THEN_allowed(self):
        expr = 'var_name + sum(sum(var_name))'
        self.calc.evaluate(self.data, expr)

    def test_GIVEN_two_cubes_and_basic_addition_WHEN_calculate_THEN_addition_successful(self):
        self._make_two_gridded()
        expr = 'var1 + var2'

        res = self.calc.evaluate(self.data, expr)
        expected = numpy.array([[12, 14, 16], [18, 20, 22], [24, 26, 28], [30, 32, 34], [36, 38, 40]])

        assert_that(numpy.array_equal(res.data, expected))

    def test_GIVEN_two_cubes_interpolated_WHEN_calculate_THEN_interpolation_successful(self):
        self._make_two_gridded()
        # Simulate the use case of interpolating between two wavelengths
        #550 -> [600] -> 670
        expr = 'var1 + (var2 - var1) * (600 - 550) / (670 - 550)'

        res = self.calc.evaluate(self.data, expr)
        expected = numpy.array([[5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16], [17, 18, 19]]) + 1.0/6

        assert_that(numpy.allclose(res.data, expected))

    def test_GIVEN_ungridded_data_basic_addition_WHEN_calculate_THEN_addition_successful(self):
        data1 = mock.make_regular_2d_ungridded_data()
        data2 = mock.make_regular_2d_ungridded_data()
        data1.metadata._name = 'var1'
        data2.metadata._name = 'var2'
        self.data = [data1, data2]
        expr = 'var1 + var2'

        res = self.calc.evaluate(self.data, expr)
        expected = 2 * self.data[1].data

        assert_that(numpy.array_equal(res.data, expected))

    def test_GIVEN_ungridded_missing_values_WHEN_calculate_THEN_missing_values_preserved(self):
        data = mock.make_regular_2d_ungridded_data_with_missing_values()
        data.metadata._name = 'var1'
        self.data = [data]
        expr = 'var1 + 10'

        res = self.calc.evaluate(self.data, expr)
        expected = numpy.ma.masked_invalid([[11, 12, 13], [14, float('Nan'), 16], [17, 18, float('Nan')],
                                            [20, 21, 22], [float('Nan'), 24, 25]])
        compare_masked_arrays(res.data, expected)

    def test_GIVEN_two_variables_WHEN_calculate_THEN_variable_values_not_changed(self):
        # This is to fix an issue where the calculator was taking a reference to the input list and therefore changing
        # its value when output.
        data1 = mock.make_regular_2d_ungridded_data()
        data2 = mock.make_regular_2d_ungridded_data()
        data1.metadata._name = 'var1'
        data2.metadata._name = 'var2'
        self.data = [data1, data2]
        expr = 'var1 + var2'

        res = self.calc.evaluate(self.data, expr)
        assert_that(numpy.array_equal(data1.data, data2.data))

    def test_GIVEN_two_cubes_basic_addition_WHEN_calculate_THEN_metadata_correct(self):
        self._make_two_gridded()
        expr = 'var1 + alias2'
        self.data[1].alias = 'alias2'

        res = self.calc.evaluate(self.data, expr)
        expected_var_name = 'calculated_variable'
        expected_standard_name = None
        expected_long_name = 'Calculated value for expression "%s"' % expr

        assert_that(isinstance(res, GriddedData))
        assert_that(res.var_name, is_(expected_var_name))
        assert_that(res.standard_name, is_(expected_standard_name))
        assert_that(res.long_name, is_(expected_long_name))
        assert_that(res.alias, is_(res.var_name))

    def test_GIVEN_variables_from_same_file_WHEN_calculate_THEN_history_added(self):
        self._make_two_ungridded_data()
        self.data[1].alias = 'alias2'
        self.data[1].filenames = self.data[0].filenames
        expr = 'var1 + alias2'
        res = self.calc.evaluate(self.data, expr)
        expected_history = "Evaluated using CIS version " + __version__ + \
                           "\nExpression evaluated: 'var1 + alias2'" + \
                           "\nwith variables: 'var1' from files ['filename1']," + \
                           "\n'var2' (as 'alias2') from files ['filename1']."
        # Do an ends_with comparison because history starts with timestamp
        assert_that(res.history, ends_with(expected_history))

    def test_GIVEN_variables_from_different_files_WHEN_calculate_THEN_history_added(self):
        self._make_two_gridded()
        expr = 'var1 + var2'
        res = self.calc.evaluate(self.data, expr)
        expected_history = "Evaluated using CIS version " + __version__ + \
                           "\nExpression evaluated: 'var1 + var2'" + \
                           "\nwith variables: 'var1' from files ['filename1']," + \
                           "\n'var2' from files ['filename2']."
       # Do an ends_with comparison because history starts with timestamp
        assert_that(res.history, ends_with(expected_history))

    def test_GIVEN_output_var_name_WHEN_calculate_THEN_output_uses_var_name(self):
        self._make_two_gridded()
        expr = 'var1 + var2'
        res = self.calc.evaluate(self.data, expr, output_var='var_out_name')
        assert_that(res.var_name, is_('var_out_name'))

    def test_GIVEN_operation_results_in_wrong_shape_THEN_raises_EvaluationError(self):
        data1 = mock.make_regular_2d_ungridded_data()
        data1.metadata._name = 'var1'
        self.data = [data1]
        expr = 'numpy.mean(var1)'
        with self.assertRaises(EvaluationError):
            res = self.calc.evaluate(self.data, expr)

    def test_GIVEN_variables_not_compatible_shape_THEN_raises_EvaluationError(self):
        data1 = mock.make_regular_2d_ungridded_data()
        data2 = mock.make_regular_2d_ungridded_data(lat_dim_length=6)
        data1.metadata._name = 'var1'
        data2.metadata._name = 'var2'
        self.data = [data1, data2]
        expr = 'var1 + var2'
        with self.assertRaises(EvaluationError):
            res = self.calc.evaluate(self.data, expr)
