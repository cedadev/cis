import logging

import iris.analysis
import iris.coords
import iris.coord_categorisation
from iris.exceptions import IrisError

from cis.data_io.data_reader import DataReader
from cis.data_io.data_writer import DataWriter
from cis.aggregation.aggregator import Aggregator
from cis.collocation.col_framework import get_kernel
from cis.exceptions import CISError, InvalidVariableError
from cis import __version__
from cis.aggregation.aggregation_kernels import aggregation_kernels as cube_aggregation_kernels


class Aggregate(object):
    def __init__(self, grid, output_file, data_reader=DataReader(), data_writer=DataWriter()):
        """
        Constructor

        :param dict grid: A dictionary of dimension_name:AggregationGrid key value pairs.
        :param output_file: The filename to output the result to
        :param data_reader: Optional :class:`DataReader` configuration object
        :param data_writer: Optional :class:`DataWriter` configuration object
        """
        self._data_writer = data_writer
        self._data_reader = data_reader
        self._grid = grid
        self._output_file = output_file

    def _create_aggregator(self, data, grid):
        return Aggregator(data, grid)

    def aggregate(self, variables, filenames, product=None, kernel=None):
        """
        Aggregate the given variables based on the initialised grid

        :param variables: One or more variables to read from the files
        :type variables: string or list
        :param filenames: One or more filenames of the files to read
        :type filenames: string or list
        :param str product: Name of data product to use (optional)
        :param str kernel: Name of kernel to use (the default is 'moments')
        """
        # Set the default kernel here rather than in the signature as the input_group dict passes None by default
        kernel_name = kernel or 'moments'
        # Read the input data - the parser limits the number of data groups to one for this command.
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variables: %s", variables)
            data = self._data_reader.read_data_list(filenames, variables, product)
        except (IrisError, InvalidVariableError) as e:
            raise CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise CISError("There was an error reading one of the files: \n" + str(e))

        aggregator = self._create_aggregator(data, self._grid)

        if isinstance(data, iris.cube.CubeList):
            kernel_inst = cube_aggregation_kernels[kernel_name]
            data = aggregator.aggregate_gridded(kernel_inst)
        else:
            kernel_class = get_kernel(kernel_name)
            kernel_inst = kernel_class()
            data = aggregator.aggregate_ungridded(kernel_inst)

        # TODO Tidy up output of grid in the history
        history = "Aggregated using CIS version " + __version__ + \
                  "\n variables: " + str(variables) + \
                  "\n from files: " + str(filenames) + \
                  "\n using new grid: " + str(self._grid) + \
                  "\n with kernel: " + kernel_name + "."
        data.add_history(history)

        self._data_writer.write_data(data, self._output_file)
