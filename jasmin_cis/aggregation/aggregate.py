import logging
import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
from jasmin_cis.data_io.read import read_data
from jasmin_cis.exceptions import CISError, InvalidVariableError
from jasmin_cis.utils import isnan, guess_coord_axis
from jasmin_cis.cis import __version__
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels
from jasmin_cis.data_io.gridded_data import GriddedData
from iris.exceptions import IrisError
import numpy


def find_nearest(array, value):
    idx = (numpy.abs(array-value)).argmin()
    return array[idx]


def categorise_coord_function(start, end, delta):
    def returned_func(_coordinate, value):
        new_grid = numpy.arange(start, end, delta)
        return find_nearest(new_grid, value)
    return returned_func


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
                if isnan(grid.delta):
                    data = data.collapsed(coord.name(), kernel)
                else:
                    if coord.points[0] < coord.points[-1]:
                        start = min(coord.bounds[0])
                        end = max(coord.bounds[-1])
                    else:
                        start = min(coord.bounds[-1])
                        end = max(coord.bounds[0])
                    if grid.start - grid.delta/2 < start:
                        raise CISError('Specified a start and delta such that the aggregation grid starts before the '
                                       'data grid. Please increase the value of start or reduce the value of delta. '
                                       'The requested starting point would be ' + str(grid.start - grid.delta/2) +
                                       ' but the data grid only starts at ' + str(start) + '.')
                    iris.coord_categorisation.add_categorised_coord(data, 'aggregation_coord_for_'+coord.name(),
                                                                    coord.name(),
                                                                    categorise_coord_function(start, end, grid.delta),
                                                                    units=coord.units)
                    data = data.aggregated_by(['aggregation_coord_for_'+coord.name()], kernel)
                # 'data' will have ended up as a cube again, now change it back to a GriddedData object
                data.__class__ = GriddedData

        history = "Subsetted using CIS version " + __version__ + \
                  "\nvariable: " + str(variable) + \
                  "\nfrom files: " + str(filenames) + \
                  "\nusing new grid: " + str(self._grid) + \
                  "\nwith kernel:" + str(kernel)
        data.add_history(history)

        if isinstance(data, iris.cube.Cube):
            iris.save(data, self._output_file)

