import logging
import iris.analysis
import iris.coords
import iris.coord_categorisation

from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
from jasmin_cis.aggregation.aggregator import Aggregator
from jasmin_cis.col_framework import get_kernel
from jasmin_cis.exceptions import CISError, InvalidVariableError
from jasmin_cis.cis import __version__
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels
from iris.exceptions import IrisError


class Aggregate(object):
    def __init__(self, grid, output_file, data_reader=DataReader(), data_writer=DataWriter()):
        self._data_writer = data_writer
        self._data_reader = data_reader
        self._grid = grid
        self._output_file = output_file

    def _create_aggregator(self, data, grid):
        return Aggregator(data, grid)

    def aggregate(self, variables, filenames, product, kernel_name):

        # Read the input data - the parser limits the number of data groups to one for this command.
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variables: %s", variables)
            data = self._data_reader.read_data(filenames, variables, product)
        except (IrisError, InvalidVariableError) as e:
            raise CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise CISError("There was an error reading one of the files: \n" + str(e))

        aggregator = self._create_aggregator(data, self._grid)

        if isinstance(data, iris.cube.Cube) or isinstance(data, iris.cube.CubeList):
            kernel = aggregation_kernels[kernel_name]
            data = aggregator.aggregate_gridded(kernel)
        else:
            kernel_class = get_kernel(kernel_name)
            kernel = kernel_class()
            data = aggregator.aggregate_ungridded(kernel)

        #TODO Tidy up output of grid in the history
        history = "Aggregated using CIS version " + __version__ + \
                  "\n variables: " + str(variables) + \
                  "\n from files: " + str(filenames) + \
                  "\n using new grid: " + str(self._grid) + \
                  "\n with kernel: " + kernel_name + "."
        data.add_history(history)

        self._data_writer.write_data(data, self._output_file)
