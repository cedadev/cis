import logging
from jasmin_cis.data_io.read import read_data
from jasmin_cis.exceptions import CISError, InvalidVariableError
from jasmin_cis.utils import isnan, guess_coord_axis
from jasmin_cis.cis import __version__
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels
from jasmin_cis.data_io.gridded_data import GriddedData
import iris
import iris.analysis
from iris.exceptions import IrisError


class Aggregate():
    def __init__(self, grid, output_file):
        self._grid = grid
        self._output_file = output_file

    def aggregate(self, variable, filenames, product, kernel_name):

        # Read the input data - the parser limits the number of data groups to one for this command.
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variable: %s", variable)
            data = read_data(filenames, variable, product)
        except (IrisError, InvalidVariableError) as e:
            raise CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise CISError("There was an error reading one of the files: \n" + str(e))

        if not isinstance(data, iris.cube.Cube):
            raise IOError('Only gridded data is currently supported')

        kernel = aggregation_kernels[kernel_name] if kernel_name is not None else aggregation_kernels['mean']

        for coord in data.coords():
            grid = None
            guessed_axis = guess_coord_axis(coord)
            if coord.name() in self._grid:
                grid = self._grid[coord.name()]
            elif guessed_axis is not None:
                if guessed_axis in self._grid:
                    grid = self._grid[guessed_axis]
                elif guessed_axis.lower() in self._grid:
                    grid = self._grid[guessed_axis.lower()]

            if grid is not None:
                if isnan(grid[0]):
                    data = data.collapsed(coord.name(), kernel)
                    # data will have ended up a cube again, now change it back to a GriddedData object
                    data.__class__ = GriddedData
                else:
                    raise CISError('Incomplete coordinate collapse not yet supported')

        history = "Subsetted using CIS version " + __version__ + \
                  "\nvariable: " + str(variable) + \
                  "\nfrom files: " + str(filenames) + \
                  "\nusing new grid: " + str(self._grid) + \
                  "\nwith kernel:" + str(kernel)
        data.add_history(history)

        if isinstance(data, iris.cube.Cube):
            iris.save(data, self._output_file)