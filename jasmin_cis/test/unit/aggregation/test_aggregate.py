import unittest
from hamcrest import assert_that, is_
from mock import MagicMock, Mock

from jasmin_cis.aggregation.aggregate import Aggregate
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
from jasmin_cis.data_io.gridded_data import GriddedDataList, make_from_cube
from jasmin_cis.test.util.mock import make_square_5x3_2d_cube


class TestAggregate(unittest.TestCase):

    def test_GIVEN_single_variable_WHEN_aggregate_THEN_DataReader_called_correctly(self):
        variables = 'var_name'
        filenames = 'filename'
        output_file = 'output.hdf'
        kernel = 'mean'
        grid = None
        input_data = make_from_cube(make_square_5x3_2d_cube())
        output_data = input_data

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=input_data)
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_aggregator = Aggregator(None, None)
        mock_aggregator.aggregate_gridded = MagicMock(return_value=output_data)  # Return the data array unmodified

        aggregate = Aggregate(grid, output_file, data_reader=mock_data_reader, data_writer=mock_data_writer)
        aggregate._create_aggregator = MagicMock(return_value=mock_aggregator)
        aggregate.aggregate(variables, filenames, None, kernel)

        assert_that(mock_data_reader.read_data.call_count, is_(1))
        assert_that(mock_data_reader.read_data.call_args[0][0], is_(filenames))
        assert_that(mock_data_reader.read_data.call_args[0][1], is_(variables))

    def test_GIVEN_multiple_variables_and_filenames_WHEN_aggregate_THEN_DataReader_called_correctly(self):
        variables = ['var_name1', 'var_name2']
        filenames = ['filename1', 'filename2']
        output_file = 'output.hdf'
        kernel = 'mean'
        grid = None
        input_data = GriddedDataList(2*[make_from_cube(make_square_5x3_2d_cube())])
        output_data = input_data

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=input_data)
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_aggregator = Aggregator(None, None)
        mock_aggregator.aggregate_gridded = MagicMock(return_value=output_data)  # Return the data array unmodified

        aggregate = Aggregate(grid, output_file, data_reader=mock_data_reader, data_writer=mock_data_writer)
        aggregate._create_aggregator = MagicMock(return_value=mock_aggregator)
        aggregate.aggregate(variables, filenames, None, kernel)

        assert_that(mock_data_reader.read_data.call_count, is_(1))
        assert_that(mock_data_reader.read_data.call_args[0][0], is_(filenames))
        assert_that(mock_data_reader.read_data.call_args[0][1], is_(variables))

    def test_GIVEN_multiple_variables_and_filenames_WHEN_aggregate_THEN_Aggregate_called_correctly(self):
        variables = ['var_name1', 'var_name2']
        filenames = ['filename1', 'filename2']
        output_file = 'output.hdf'
        kernel = 'mean'
        grid = 'grid'
        input_data = GriddedDataList(2*[make_from_cube(make_square_5x3_2d_cube())])
        output_data = input_data

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=input_data)
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_aggregator = Aggregator(None, None)
        mock_aggregator.aggregate_gridded = MagicMock(return_value=output_data)  # Return the data array unmodified

        aggregate = Aggregate(grid, output_file, data_reader=mock_data_reader, data_writer=mock_data_writer)
        aggregate._create_aggregator = MagicMock(return_value=mock_aggregator)
        aggregate.aggregate(variables, filenames, None, kernel)

        assert_that(mock_aggregator.aggregate_gridded.call_count, is_(1))
        assert_that(mock_aggregator.aggregate_gridded.call_args[0][0], kernel)

    def test_GIVEN_single_variable_WHEN_aggregate_THEN_DataWriter_called_correctly(self):
        variables = 'var_name'
        filenames = 'filename'
        output_file = 'output.hdf'
        kernel = 'mean'
        grid = None
        input_data = make_from_cube(make_square_5x3_2d_cube())
        output_data = make_from_cube(make_square_5x3_2d_cube() + 1)

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=input_data)
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_aggregator = Aggregator(None, None)
        mock_aggregator.aggregate_gridded = MagicMock(return_value=output_data)  # Return the modified data array

        aggregate = Aggregate(grid, output_file, data_reader=mock_data_reader, data_writer=mock_data_writer)
        aggregate._create_aggregator = MagicMock(return_value=mock_aggregator)
        aggregate.aggregate(variables, filenames, None, kernel)

        assert_that(mock_data_writer.write_data.call_count, is_(1))
        written_data = mock_data_writer.write_data.call_args[0][0]
        written_filename = mock_data_writer.write_data.call_args[0][1]
        assert_that(written_data.data.tolist(), is_([[2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16]]))
        assert_that(written_filename, is_(output_file))

    def test_GIVEN_multiple_variables_WHEN_aggregate_THEN_DataWriter_called_correctly(self):
        variables = ['var_name1', 'var_name2']
        filenames = ['filename1', 'filename2']
        output_file = 'output.hdf'
        kernel = 'mean'
        grid = 'grid'
        input_data = GriddedDataList(2*[make_from_cube(make_square_5x3_2d_cube())])
        output_data = GriddedDataList(2*[make_from_cube(make_square_5x3_2d_cube()) + 1])

        mock_data_reader = DataReader()
        mock_data_reader.read_data = MagicMock(return_value=input_data)
        mock_data_writer = DataWriter()
        mock_data_writer.write_data = Mock()
        mock_aggregator = Aggregator(None, None)
        mock_aggregator.aggregate_gridded = MagicMock(return_value=output_data)  # Return the modified data array

        aggregate = Aggregate(grid, output_file, data_reader=mock_data_reader, data_writer=mock_data_writer)
        aggregate._create_aggregator = MagicMock(return_value=mock_aggregator)
        aggregate.aggregate(variables, filenames, None, kernel)

        assert_that(mock_data_writer.write_data.call_count, is_(1))
        written_data = mock_data_writer.write_data.call_args[0][0]
        written_filename = mock_data_writer.write_data.call_args[0][1]
        assert_that(written_data[0].data.tolist(), is_([[2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12, 13], [14, 15, 16]]))
        assert_that(written_filename, is_(output_file))