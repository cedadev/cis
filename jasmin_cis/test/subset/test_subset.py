from unittest import TestCase
from hamcrest import assert_that, is_
from mock import MagicMock, Mock

from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.subsetting.subset import Subset
from jasmin_cis.subsetting.subset_limits import SubsetLimits
from jasmin_cis.subsetting.subsetter import Subsetter
from jasmin_cis.test.test_util.mock import make_regular_2d_ungridded_data


class TestSubset(TestCase):

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataReader_called_correctly(self):
        variable = 'var_name'
        filename = 'filename'
        output_file = 'output.hdf'
        xmin, xmax = -10, 10
        ymin, ymax = 40, 60
        limits = {'x': SubsetLimits(xmin, xmax, False),
                  'y': SubsetLimits(ymin, ymax, False)}

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=make_regular_2d_ungridded_data())
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_subsetter = Subsetter()
        mock_subsetter.subset = lambda *args: args[0]  # Return the data array unmodified

        subset = Subset(limits, output_file, subsetter=mock_subsetter,
                        data_reader=mock_data_reader, data_writer=mock_data_writer)
        subset.subset(variable, filename, product=None)
        assert_that(mock_data_reader.read_data.call_count, is_(1))
        assert_that(mock_data_reader.read_data.call_args[0][0], filename)
        assert_that(mock_data_reader.read_data.call_args[0][1], variable)

    def test_GIVEN_single_variable_WHEN_subset_THEN_Subsetter_called_correctly(self):
        variable = 'var_name'
        filename = 'filename'
        xmin, xmax = -10, 10
        ymin, ymax = 40, 60
        limits = {'x': SubsetLimits(xmin, xmax, False),
                  'y': SubsetLimits(ymin, ymax, False)}
        output_file = 'output.hdf'

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=make_regular_2d_ungridded_data())
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_subsetter = Subsetter()
        mock_subsetter.subset = MagicMock(side_effect=lambda *args: args[0])  # Return the data array unmodified

        subset = Subset(limits, output_file, subsetter=mock_subsetter,
                        data_reader=mock_data_reader, data_writer=mock_data_writer)
        subset.subset(variable, filename, product=None)
        assert_that(mock_subsetter.subset.call_count, is_(1))
        called_data = mock_subsetter.subset.call_args[0][0]
        called_constraint = mock_subsetter.subset.call_args[0][1]
        assert_that(called_data.data_flattened.tolist(),
                    is_([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
        assert_that(called_constraint._limits['latitude'][1:3], is_((40, 60)))
        assert_that(called_constraint._limits['longitude'][1:3], is_((-10, 10)))

    def test_GIVEN_single_variable_WHEN_subset_THEN_DataWriter_called_correctly(self):
        variable = 'var_name'
        filename = 'filename'
        xmin, xmax = -10, 10
        ymin, ymax = 40, 60
        limits = {'x': SubsetLimits(xmin, xmax, False),
                  'y': SubsetLimits(ymin, ymax, False)}
        output_file = 'output.hdf'

        def _mock_subset(data, constraint):
            data.data += 1  # Modify the data slightly so we can be sure it's passed in correctly
            return data
        mock_subsetter = Subsetter()
        mock_subsetter.subset = _mock_subset
        mock_data_reader = DataReader()
        mock_data_reader.read_data = lambda *args: make_regular_2d_ungridded_data()  # Lambda avoids args being passed
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = MagicMock()

        subset = Subset(limits, output_file, subsetter=mock_subsetter,
                        data_reader=mock_data_reader, data_writer=mock_data_writer)
        subset.subset(variable, filename, product=None)

        assert_that(mock_data_writer.write_data.call_count, is_(1))
        written_data = mock_data_writer.write_data.call_args[0][0]
        written_filename = mock_data_writer.write_data.call_args[0][1]
        assert_that(written_data.data_flattened.tolist(), is_([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))
        assert_that(written_filename, is_(output_file))

    def test_GIVEN_multiple_variables_and_filenames_WHEN_subset_THEN_DataReader_called_correctly(self):
        variables = ['var_name1', 'var_name2']
        filenames = ['filename1', 'filename2']
        output_file = 'output.hdf'
        xmin, xmax = -10, 10
        ymin, ymax = 40, 60
        limits = {'x': SubsetLimits(xmin, xmax, False),
                  'y': SubsetLimits(ymin, ymax, False)}

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=UngriddedDataList(2*[make_regular_2d_ungridded_data()]))
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_subsetter = Subsetter()
        mock_subsetter.subset = lambda *args: args[0]  # Return the data array unmodified

        subset = Subset(limits, output_file, subsetter=mock_subsetter,
                        data_reader=mock_data_reader, data_writer=mock_data_writer)
        subset.subset(variables, filenames, product=None)
        assert_that(mock_data_reader.read_data.call_count, is_(1))
        assert_that(mock_data_reader.read_data.call_args[0][0], filenames)
        assert_that(mock_data_reader.read_data.call_args[0][1], variables)