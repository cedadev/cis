import logging
import datetime
import iris.coord_categorisation
import iris.analysis.cartography
from iris.coords import DimCoord
import numpy
from jasmin_cis.col_implementations import GeneralGriddedColocator, BinnedCubeCellOnlyConstraint
from jasmin_cis.data_io.gridded_data import make_from_cube
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.subsetting.subset import Subset
from jasmin_cis.utils import isnan, guess_coord_axis
from jasmin_cis.exceptions import ClassNotFoundError, CoordinateNotFoundError
from jasmin_cis.aggregation.aggregation_kernels import MultiKernel
from jasmin_cis.data_io.gridded_data import GriddedDataList


class Aggregator(object):
    def __init__(self, data, grid):
        self.data = data
        self._grid = grid

    def _gridded_full_collapse(self, coords, kernel):
        if isinstance(kernel, iris.analysis.WeightedAggregator):
            # If this is a list we can calculate weights using the first item (all variables should be on
            # same grid)
            data_for_weights = self.data[0] if isinstance(self.data, list) else self.data
            # Weights to correctly calculate areas.
            area_weights = iris.analysis.cartography.area_weights(data_for_weights)
            return self.data.collapsed(coords, kernel, weights=area_weights)
        elif isinstance(kernel, iris.analysis.Aggregator):
            return self.data.collapsed(coords, kernel)
        else:
            raise ClassNotFoundError('Error - unexpected aggregator type.')

    def aggregate_gridded(self, kernel):
        # Make sure all coordinate have bounds - important for weighting and aggregating
        for coord in self.data.coords():
            if not coord.has_bounds() and len(coord.points) > 1:
                coord.guess_bounds()
                logging.warning("Creating guessed bounds as none exist in file")
                new_coord_number = self.data.coord_dims(coord)
                self.data.remove_coord(coord.name())
                self.data.add_dim_coord(coord, new_coord_number)
        coords = []
        for coord in self.data.coords():
            grid, guessed_axis = self.get_grid(coord)

            if grid is not None:
                if isnan(grid.delta):
                    logging.info('Aggregating on ' + coord.name() + ', collapsing completely and using ' +
                                 kernel.cell_method + ' kernel.')
                    coords.append(coord)
                else:
                    raise NotImplementedError("Aggregation using partial collapse of "
                                              "coordinates is not supported for GriddedData")

        output = GriddedDataList([])
        if isinstance(kernel, MultiKernel):
            for sub_kernel in kernel.sub_kernels:
                sub_kernel_out = self._gridded_full_collapse(coords, sub_kernel)
                output.append_or_extend(sub_kernel_out)
        else:
            output.append_or_extend(self._gridded_full_collapse(coords, kernel))
        return output

    def aggregate_ungridded(self, kernel):
        """
        Performs aggregation for ungridded data by first generating a new grid, converting it into a cube, then
        colocating using the appropriate kernel and a cube cell constraint
        """
        new_cube_coords = []
        new_cube_shape = []

        i = 0

        for coord in self.data.coords():
            grid, guessed_axis = self.get_grid(coord)

            if grid is not None and isnan(grid.delta):
                logging.warning('Coordinate ' + guessed_axis + ' was given without a grid. No need to specify '
                                'coordinates for complete collapse, all coordinates without a grid specified are '
                                'automatically collapsed for ungridded aggregation.')

            if grid is not None and not isnan(grid.delta):
                if grid.is_time or guessed_axis == 'T':
                    # Ensure that the limits are date/times.
                    dt = parse_datetime.convert_datetime_components_to_datetime(grid.start, True)
                    grid_start = Subset._convert_datetime_to_coord_unit(coord, dt)
                    dt = parse_datetime.convert_datetime_components_to_datetime(grid.end, False)
                    grid_end = Subset._convert_datetime_to_coord_unit(coord, dt)
                    grid_delta = grid.delta
                else:
                    # Assume to be a non-time axis
                    (grid_start, grid_end) = Subset._fix_non_circular_limits(float(grid.start), float(grid.end))
                    grid_delta = float(grid.delta)

                new_coordinate_grid = aggregation_grid_array(grid_start, grid_end, grid_delta, grid.is_time, coord)
                new_coord = DimCoord(new_coordinate_grid, var_name=coord.name(), standard_name=coord.standard_name,
                                     units=coord.units)
                new_cube_coords.append((new_coord, i))
                new_cube_shape.append(len(new_coord.points))
                i += 1

        if len(self._grid) != 0:
            raise CoordinateNotFoundError('No coordinate found that matches {}. Please check the coordinate '
                                          'name.'.format(self._grid.keys()))

        dummy_data = numpy.reshape(numpy.arange(int(numpy.prod(new_cube_shape)))+1.0, tuple(new_cube_shape))
        aggregation_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=new_cube_coords)

        colocator = GeneralGriddedColocator()
        constraint = BinnedCubeCellOnlyConstraint()
        aggregated_cube = colocator.colocate(aggregation_cube, self.data, constraint, kernel)

        if len(aggregated_cube) == 1:
            return aggregated_cube[0]
        else:
            return aggregated_cube

    def get_grid(self, coord):

        grid = None
        guessed_axis = guess_coord_axis(coord)
        if coord.name() in self._grid:
            grid = self._grid.pop(coord.name())
        elif coord.standard_name in self._grid:
            grid = self._grid.pop(coord.standard_name)
        elif coord.long_name in self._grid:
            grid = self._grid.pop(coord.long_name)
        elif guessed_axis is not None:
            if guessed_axis in self._grid:
                grid = self._grid.pop(guessed_axis)
            elif guessed_axis.lower() in self._grid:
                grid = self._grid.pop(guessed_axis.lower())

        return grid, guessed_axis


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


def aggregation_grid_array(start, end, delta, is_time, coordinate):
    if is_time:
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

        return new_time_grid
    else:
        new_grid = numpy.arange(start+delta/2, end+delta/2, delta)

        return new_grid


def find_nearest(array, value):
    """
    Find the nearest to the parameter value in the array
    :param array: A numpy array
    :param value: A single value
    :return: A single value from the array
    """
    idx = (numpy.abs(array-value)).argmin()
    return array[idx]


def categorise_coord_function(start, end, delta, is_time):
    def returned_func(coordinate, value):
        return find_nearest(aggregation_grid_array(start, end, delta, is_time, coordinate), value)

    return returned_func
