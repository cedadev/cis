import logging
import iris
import iris.analysis
import iris.coords
import iris.coord_categorisation
from jasmin_cis.data_io.read import read_data
from jasmin_cis.exceptions import CISError, InvalidVariableError
from jasmin_cis.utils import isnan
from jasmin_cis.cis import __version__
from jasmin_cis.aggregation.aggregation_kernels import aggregation_kernels
from jasmin_cis.data_io.gridded_data import GriddedData
from iris.exceptions import IrisError
import numpy

from jasmin_cis.subsetting.subset import Subset
import jasmin_cis.parse_datetime as parse_datetime

import datetime


def find_nearest(array, value):
    idx = (numpy.abs(array-value)).argmin()
    return array[idx]


def categorise_coord_function(start, end, delta, is_time):
    if is_time:
        def returned_func(coordinate, value):
            start_dt = Subset._convert_coord_unit_to_datetime(coordinate, start)
            end_dt = Subset._convert_coord_unit_to_datetime(coordinate, end)
            new_time_grid = []
            new_time = start_dt
            while new_time < end_dt:
                new_time_grid.append(Subset._convert_datetime_to_coord_unit(coordinate, new_time))
                new_year = new_time.year + delta.year
                new_time = datetime.datetime(new_year, new_time.month, new_time.day, new_time.hour, new_time.minute,
                                             new_time.second)
                new_month = (new_time.month + delta.month)
                #TODO This will fail for cases such as January 30th -> +1 month -> February 30th.
                # Need to work out what correct behaivour should be in this case.
                if new_month > 12:
                    new_year += new_month//12
                    new_month %= 12
                    if new_month == 0:
                        new_month = 12
                new_time = datetime.datetime(new_year, new_month, new_time.day, new_time.hour, new_time.minute,
                                             new_time.second)
                new_time += datetime.timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
                                               minutes=delta.minute, hours=delta.hour, weeks=0)
            new_time_grid = numpy.array(new_time_grid)

            return find_nearest(new_time_grid, value)
    else:
        new_grid = numpy.arange(start+delta/2, end+delta/2, delta)

        def returned_func(_coordinate, value):
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
            guessed_axis = Subset._guess_coord_axis(coord)
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
                    logging.info('Aggregating on ' + coord.name() + ', collapsing completely and using ' + kernel_name +
                                 ' kernel.')
                else:
                    if coord.points[0] < coord.points[-1]:
                        start = min(coord.bounds[0])
                        end = max(coord.bounds[-1])
                    else:
                        start = min(coord.bounds[-1])
                        end = max(coord.bounds[0])

                    if grid.is_time or guessed_axis == 'T':
                        # Ensure that the limits are date/times.
                        dt = parse_datetime.convert_datetime_components_to_datetime(grid.start, True)
                        grid_start = Subset._convert_datetime_to_coord_unit(coord, dt)
                        dt = parse_datetime.convert_datetime_components_to_datetime(grid.end, False)
                        grid_end = Subset._convert_datetime_to_coord_unit(coord, dt)
                        grid_delta = grid.delta

                        # The following are used to generate helpful error messages, with the time in a user friendly
                        # format
                        start_of_grid = Subset._convert_coord_unit_to_datetime(coord, start)
                        end_of_grid = Subset._convert_coord_unit_to_datetime(coord, end)
                        start_requested = Subset._convert_coord_unit_to_datetime(coord, grid_start)
                        end_requested = Subset._convert_coord_unit_to_datetime(coord, grid_end)
                    else:
                        # Assume to be a non-time axis
                        (grid_start, grid_end) = Subset._fix_non_circular_limits(float(grid.start), float(grid.end))
                        grid_delta = grid.delta

                        # The following are used to generate helpful error messages
                        start_of_grid = start
                        end_of_grid = end
                        start_requested = grid.start
                        end_requested = grid.end
                    if grid_start < start:
                        logging.warning('Specified a start such that the aggregation grid starts before the '
                                        'data grid. The requested starting point would be ' + str(start_requested) +
                                        ' this will now be changed to the start of the grid at ' + str(start_of_grid) +
                                        '.')
                        grid_start = start
                        start_requested = Subset._convert_coord_unit_to_datetime(coord, start)
                    if grid_end > end:
                        logging.warning('Specified an end such that the aggregation grid ends after the '
                                        'data grid. The requested ending point would be ' + str(end_requested) +
                                        ' this will now be changed to the end of the grid at ' + str(end_of_grid) + '.')
                        grid_end = end
                        end_requested = Subset._convert_coord_unit_to_datetime(coord, end)
                    iris.coord_categorisation.add_categorised_coord(data, 'aggregation_coord_for_'+coord.name(),
                                                                    coord.name(),
                                                                    categorise_coord_function(grid_start, grid_end,
                                                                                              grid_delta, grid.is_time),
                                                                    units=coord.units)
                    # Get Iris to do the aggregation
                    logging.info('Aggregating on ' + coord.name() + ' over range ' + str(start_requested) + ' to ' +
                                 str(end_requested) + ' using steps of ' + str(grid_delta) + ' and ' + kernel_name +
                                 ' kernel.')
                    data = data.aggregated_by(['aggregation_coord_for_'+coord.name()], kernel)

                    # Now make a new_coord, as the exiting coord will have the wrong coordinate points
                    new_coord = data.coord(coord.name())
                    new_coord.points = data.coord('aggregation_coord_for_'+coord.name()).points
                    new_coord.bounds = None
                    new_coord.guess_bounds()
                    new_coord_number = data.coord_dims(coord)

                    # Remove the old coord and add the new one
                    data.remove_coord(coord.name())
                    data.add_dim_coord(new_coord, new_coord_number)
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

