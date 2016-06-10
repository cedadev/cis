"""
Unit tests for the top-level subsetting routines.
Note that the set_limit mocks are setup for each test using the start/stop methods in setup
 and teardown respectively, but that the constrain methods are patched out on a per-test basis, this is just
 because some tests rely on the constrain call having different side effects.
"""
from unittest import TestCase
from hamcrest import assert_that, is_
from mock import MagicMock, Mock, patch

from cis.data_io.data_reader import DataReader
from cis.data_io.data_writer import DataWriter
from cis.data_io.ungridded_data import UngriddedDataList
from cis.data_io.gridded_data import GriddedDataList, make_from_cube
from cis.subsetting.subset import Subset
from cis.subsetting.subset_limits import SubsetLimits
from cis.test.util.mock import make_regular_2d_ungridded_data, make_square_5x3_2d_cube

# TODO: These will all need updating...

class TestSubsetOnUngriddedData(TestCase):

    def setUp(self):
        """
        Setup the test harnesses, the various mocks and variables are set here, but some may be overriden by the
        individual tests.
        :return:
        """
        self.variable = 'var_name'
        self.filename = 'filename'
        self.output_file = 'output.hdf'
        self.xmin, self.xmax = -10, 10
        self.ymin, self.ymax = 40, 60
        self.limits = {'x': SubsetLimits(self.xmin, self.xmax, False),
                       'y': SubsetLimits(self.ymin, self.ymax, False)}

        self.mock_data_reader = DataReader()
        self.mock_data_reader.read_data_list = MagicMock(return_value=make_regular_2d_ungridded_data())
        self.mock_data_writer = DataWriter()
        self.mock_data_writer.write_data = Mock()

        # Patch out the set_limit methods so that we can check they've been called correctly
        self.limit_patch = patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.set_limit')
        self.set_limit = self.limit_patch.start()

    def tearDown(self):
        """
        Make sure we clean-up the patch
        """
        self.limit_patch.stop()

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataReader_called_correctly(self):

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        subset.subset(self.variable, self.filename, product=None)
        assert_that(self.mock_data_reader.read_data_list.call_count, is_(1))
        assert_that(self.mock_data_reader.read_data_list.call_args[0][0], self.filename)
        assert_that(self.mock_data_reader.read_data_list.call_args[0][1], self.variable)

    def test_GIVEN_single_variable_WHEN_subset_THEN_Subsetter_called_correctly(self):

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        # Patch out the constrain method, in this case it just sends all the data back
        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                             side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list
            assert_that(called_data.data_flattened.tolist(),
                        is_([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
            assert_that(called_limits[0][0][0].name(), is_('lat'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('lon'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataWriter_called_correctly(self):

        def _mock_subset(data):
            data.data += 1  # Modify the data slightly so we can be sure it's passed in correctly
            return data

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        # Patch out the constrain method, in this case it modifies the data slightly so we can test the writing
        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                             side_effect=_mock_subset) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(self.mock_data_writer.write_data.call_count, is_(1))
            written_data = self.mock_data_writer.write_data.call_args[0][0]
            written_filename = self.mock_data_writer.write_data.call_args[0][1]
            assert_that(written_data.data_flattened.tolist(), is_([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))
            assert_that(written_filename, is_(self.output_file))

    def test_GIVEN_multiple_variables_and_filenames_WHEN_subset_THEN_DataReader_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']
        self.filenames = ['filename1', 'filename2']

        self.mock_data_reader.read_data_list = MagicMock(
            return_value=UngriddedDataList(2 * [make_regular_2d_ungridded_data()]))

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                             side_effect=lambda *args: args[0]) as constrain:

            subset.subset(self.variables, self.filenames, product=None)

            assert_that(self.mock_data_reader.read_data_list.call_count, is_(1))
            assert_that(self.mock_data_reader.read_data_list.call_args[0][0], self.filenames)
            assert_that(self.mock_data_reader.read_data_list.call_args[0][1], self.variables)

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_Subsetter_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']

        self.mock_data_reader.read_data_list = MagicMock(
            return_value=UngriddedDataList(2 * [make_regular_2d_ungridded_data()]))

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                             side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variables, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list

            assert_that(called_data[0].data_flattened.tolist(), is_([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
            assert_that(called_data[1].data_flattened.tolist(), is_(called_data[0].data_flattened.tolist()))
            assert_that(called_limits[0][0][0].name(), is_('lat'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('lon'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_DataWriter_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']

        def _mock_subset(data):
            # Modify the data slightly so we can be sure it's passed in correctly
            for var in data:
                var.data += 1
            return data

        self.mock_data_reader.read_data_list = MagicMock(return_value=UngriddedDataList([make_regular_2d_ungridded_data(),
                                                                                    make_regular_2d_ungridded_data()]))

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                                side_effect=_mock_subset) as constrain:
            subset.subset(self.variables, self.filename, product=None)

            assert_that(self.mock_data_writer.write_data.call_count, is_(1))
            written_data = self.mock_data_writer.write_data.call_args[0][0]
            written_filename = self.mock_data_writer.write_data.call_args[0][1]
            assert_that(written_data[0].data_flattened.tolist(), is_([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))
            assert_that(written_data[0].data_flattened.tolist(), written_data[1].data_flattened.tolist())
            assert_that(written_filename, is_(self.output_file))

    def test_GIVEN_named_variables_WHEN_subset_THEN_coordinates_found_correctly(self):
        self.limits = {'lon': SubsetLimits(self.xmin, self.xmax, False),
                       'lat': SubsetLimits(self.ymin, self.ymax, False)}

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.UngriddedSubsetConstraint.constrain',
                             side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variable, self.filename, product=None)
            called_limits = self.set_limit.call_args_list
            assert_that(called_limits[0][0][0].name(), is_('lat'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('lon'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))


class TestSubsetOnGriddedData(TestCase):

    def _mock_data(self, data):
        return data

    def setUp(self):
        self.variable = 'var_name'
        self.filename = 'filename'
        self.output_file = 'output.hdf'
        self.xmin, self.xmax = 0, 5
        self.ymin, self.ymax = -5, 5
        self.limits = {'x': SubsetLimits(self.xmin, self.xmax, False),
                       'y': SubsetLimits(self.ymin, self.ymax, False)}

        self.mock_data_reader = DataReader()
        self.mock_data_reader.read_data_list = MagicMock(return_value=make_from_cube(make_square_5x3_2d_cube()))
        self.mock_data_writer = DataWriter()
        self.mock_data_writer.write_data = Mock()

        self.limit_patch = patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.set_limit')
        self.set_limit = self.limit_patch.start()

    def tearDown(self):
        self.limit_patch.stop()

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataReader_called_correctly(self):

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        subset.subset(self.variable, self.filename, product=None)
        assert_that(self.mock_data_reader.read_data_list.call_count, is_(1))
        assert_that(self.mock_data_reader.read_data_list.call_args[0][0], self.filename)
        assert_that(self.mock_data_reader.read_data_list.call_args[0][1], self.variable)

    def test_GIVEN_single_variable_WHEN_subset_THEN_Subsetter_called_correctly(self):

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                                     side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list
            assert_that(called_data.data.tolist(),
                        is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
            assert_that(called_limits[0][0][0].name(), is_('latitude'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('longitude'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataWriter_called_correctly(self):

        def _mock_subset(data):
            data.data += 1  # Modify the data slightly so we can be sure it's passed in correctly
            return data

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                                     side_effect=_mock_subset) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(self.mock_data_writer.write_data.call_count, is_(1))
            written_data = self.mock_data_writer.write_data.call_args[0][0]
            written_filename = self.mock_data_writer.write_data.call_args[0][1]
            assert_that(written_data.data.tolist(), is_([[2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16]]))
            assert_that(written_filename, is_(self.output_file))

    def test_GIVEN_multiple_variables_and_filenames_WHEN_subset_THEN_DataReader_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']
        self.filenames = ['filename1', 'filename2']

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)
        subset.subset(self.variables, self.filenames, product=None)
        assert_that(self.mock_data_reader.read_data_list.call_count, is_(1))
        assert_that(self.mock_data_reader.read_data_list.call_args[0][0], self.filenames)
        assert_that(self.mock_data_reader.read_data_list.call_args[0][1], self.variables)

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_Subsetter_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']

        self.mock_data_reader.read_data_list = MagicMock(return_value=GriddedDataList([make_square_5x3_2d_cube(),
                                                                                  make_square_5x3_2d_cube()]))

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                             side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variables, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list
            assert_that(called_data[0].data.tolist(), is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
            assert_that(called_data[1].data.tolist(), is_(called_data[0].data.tolist()))
            assert_that(called_limits[0][0][0].name(), is_('latitude'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('longitude'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))

    def test_GIVEN_multiple_variables_WHEN_subset_THEN_DataWriter_called_correctly(self):
        self.variables = ['var_name1', 'var_name2']

        def _mock_subset(data):
            # Modify the data slightly so we can be sure it's passed in correctly
            for var in data:
                var.data += 1
            return data

        self.mock_data_reader.read_data_list = MagicMock(return_value=GriddedDataList([make_square_5x3_2d_cube(),
                                                                                  make_square_5x3_2d_cube()]))

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                                     side_effect=_mock_subset) as constrain:
            subset.subset(self.variables, self.filename, product=None)

            assert_that(self.mock_data_writer.write_data.call_count, is_(1))
            written_data = self.mock_data_writer.write_data.call_args[0][0]
            written_filename = self.mock_data_writer.write_data.call_args[0][1]
            assert_that(written_data[0].data.tolist(), is_([[2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16]]))
            assert_that(written_data[0].data.tolist(), written_data[1].data.tolist())
            assert_that(written_filename, is_(self.output_file))

    def test_GIVEN_standard_named_variables_WHEN_subset_THEN_coordinates_found_correctly(self):
        self.limits = {'longitude': SubsetLimits(self.xmin, self.xmax, False),
                       'latitude': SubsetLimits(self.ymin, self.ymax, False)}

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                                     side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list
            assert_that(called_data.data.tolist(), is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
            assert_that(called_limits[0][0][0].name(), is_('latitude'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('longitude'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))

    def test_GIVEN_var_named_variables_WHEN_subset_THEN_coordinates_found_correctly(self):
        self.limits = {'lon': SubsetLimits(self.xmin, self.xmax, False),
                       'lat': SubsetLimits(self.ymin, self.ymax, False)}

        subset = Subset(self.limits, self.output_file,
                        data_reader=self.mock_data_reader, data_writer=self.mock_data_writer)

        with patch('cis.subsetting.subset_constraint.GriddedSubsetConstraint.constrain',
                                     side_effect=lambda *args: args[0]) as constrain:
            subset.subset(self.variable, self.filename, product=None)

            assert_that(constrain.call_count, is_(1))
            called_data = constrain.call_args[0][0]
            called_limits = self.set_limit.call_args_list
            assert_that(called_data.data.tolist(), is_([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]))
            assert_that(called_limits[0][0][0].name(), is_('latitude'))
            assert_that(called_limits[0][0][1:], is_((self.ymin, self.ymax)))
            assert_that(called_limits[1][0][0].name(), is_('longitude'))
            assert_that(called_limits[1][0][1:], is_((self.xmin, self.xmax)))
