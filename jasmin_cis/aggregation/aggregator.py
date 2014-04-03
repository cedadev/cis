import logging
import datetime
import iris.coord_categorisation
import numpy
from jasmin_cis.data_io.gridded_data import GriddedData
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.subsetting.subset import Subset
from jasmin_cis.subsetting.subset_constraint import GriddedSubsetConstraint
from jasmin_cis.subsetting.subsetter import Subsetter
from jasmin_cis.utils import isnan


class Aggregator:
    def __init__(self, data, kernel, grid):
        self.data = data
        self.kernel = kernel
        self._grid = grid

    def aggregate_gridded(self):
        for coord in self.data.coords():
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
                    self.data = self.data.collapsed(coord.name(), self.kernel)
                    logging.info('Aggregating on ' + coord.name() + ', collapsing completely and using ' +
                                 self.kernel.cell_method + ' kernel.')
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
                        grid_delta = float(grid.delta)

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
                        if grid.is_time or guessed_axis == 'T':
                            start_requested = Subset._convert_coord_unit_to_datetime(coord, start)
                        else:
                            start_requested = start
                    if grid_end > end:
                        logging.warning('Specified an end such that the aggregation grid ends after the '
                                        'data grid. The requested ending point would be ' + str(end_requested) +
                                        ' this will now be changed to the end of the grid at ' + str(end_of_grid) + '.')
                        grid_end = end
                        if grid.is_time or guessed_axis == 'T':
                            end_requested = Subset._convert_coord_unit_to_datetime(coord, end)
                        else:
                            end_requested = end

                    # Subset the data. This ensures the Iris cube only has the data in that we actually want to
                    # aggregate, making it easier to make use of Iris's aggregation function while ignoring data outside
                    # the aggregation range.
                    subsetter = Subsetter()
                    subset_constraint = GriddedSubsetConstraint()

                    # Need to work out slightly different limits for the subset, as by default it will return anything
                    # that has bounds inside the limit.
                    cell_start_index = coord.nearest_neighbour_index(grid_start)
                    while coord.cell(cell_start_index).point < grid_start:
                        cell_start_index += 1
                    actual_start = float(max(coord.cell(cell_start_index).bound))
                    cell_end_index = coord.nearest_neighbour_index(grid_end)
                    while coord.cell(cell_end_index).point > grid_end:
                        cell_end_index -= 1
                    if cell_end_index == cell_start_index:
                        # In case we are now on longitude bounds and have wrapped around.
                        cell_end_index -= 1
                    actual_end = float(min(coord.cell(cell_end_index).bound))

                    subset_constraint.set_limit(coord, actual_start, actual_end)
                    self.data = subsetter.subset(self.data, subset_constraint)

                    iris.coord_categorisation.add_categorised_coord(self.data, 'aggregation_coord_for_'+coord.name(),
                                                                    coord.name(),
                                                                    categorise_coord_function(grid_start, grid_end,
                                                                                              grid_delta, grid.is_time),
                                                                    units=coord.units)

                    # Get Iris to do the aggregation
                    logging.info('Aggregating on ' + coord.name() + ' over range ' + str(start_requested) + ' to ' +
                                 str(end_requested) + ' using steps of ' + str(grid_delta) + ' and ' +
                                 self.kernel.cell_method + ' kernel.')
                    self.data = self.data.aggregated_by(['aggregation_coord_for_'+coord.name()], self.kernel)

                    # Now make a new_coord, as the exiting coord will have the wrong coordinate points
                    new_coord = self.data.coord(coord.name())
                    new_coord.points = self.data.coord('aggregation_coord_for_'+coord.name()).points
                    try:
                        new_coord.bounds = None
                        new_coord.guess_bounds()
                    except ValueError:
                        logging.warn('Only one ' + coord.name() + ' coordinate left after aggregation. Bounds '
                                     'information will be missing for this coordinate.')
                    new_coord_number = self.data.coord_dims(coord)

                    # Remove the old coord and add the new one
                    self.data.remove_coord(coord.name())
                    self.data.add_dim_coord(new_coord, new_coord_number)
                # 'data' will have ended up as a cube again, now change it back to a GriddedData object
                self.data.__class__ = GriddedData

        return self.data


def find_nearest(array, value):
    idx = (numpy.abs(array-value)).argmin()
    return array[idx]


def add_year_midpoint(dt_object, years):

    if not isinstance(years, int):
        raise TypeError
    if not isinstance(dt_object, datetime.datetime):
        raise TypeError

    new_month = dt_object.month + 6 * (years % 2)
    new_year = dt_object.year + years//2
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    return dt_object.replace(year=new_year, month=new_month)


def add_month_midpoint(dt_object, months):

    if not isinstance(months, int):
        raise TypeError
    if not isinstance(dt_object, datetime.datetime):
        raise TypeError

    new_month = dt_object.month + months//2
    new_year = dt_object.year
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    dt_object = dt_object.replace(year=new_year, month=new_month)

    if months % 2 != 0:
        dt_object += datetime.timedelta(days=14, seconds=0, microseconds=0, milliseconds=0,
                                        minutes=0, hours=0, weeks=0)

    return dt_object


def month_past_end_of_year(month, year):
    year += month//12
    month %= 12
    if month == 0:
        month = 12

    return month, year


def categorise_coord_function(start, end, delta, is_time):
    if is_time:
        def returned_func(coordinate, value):
            start_dt = Subset._convert_coord_unit_to_datetime(coordinate, start)
            end_dt = Subset._convert_coord_unit_to_datetime(coordinate, end)

            # Some logic to find the mid point to start on
            if delta.year > 0:
                start_dt = add_year_midpoint(start_dt, delta.year)

            # We make an assumption here that half a month is always 15 days.
            if delta.month > 0:
                start_dt = add_month_midpoint(start_dt, delta.month)

            dt = datetime.timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
                                    minutes=delta.minute, hours=delta.hour, weeks=0)

            start_dt += dt/2

            new_time_grid = []
            new_time = start_dt

            while new_time < end_dt:
                new_time_grid.append(Subset._convert_datetime_to_coord_unit(coordinate, new_time))

                new_year = new_time.year + delta.year
                new_month = new_time.month + delta.month
                if new_month > 12:
                    new_month, new_year = month_past_end_of_year(new_month, new_year)
                #TODO this is a slightly inelegant fix for the problem of something like 30th Jan +1 month
                # Need to work out what correct behaivour should be in this case.
                try:
                    new_time = new_time.replace(year=new_year, month=new_month)
                except ValueError:
                    new_time += datetime.timedelta(days=28)
                new_time += datetime.timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
                                               minutes=delta.minute, hours=delta.hour, weeks=0)

            new_time_grid = numpy.array(new_time_grid)

            return find_nearest(new_time_grid, value)
    else:
        new_grid = numpy.arange(start+delta/2, end+delta/2, delta)

        def returned_func(_coordinate, value):
            return find_nearest(new_grid, value)

    return returned_func