import logging
import numpy as np
from datetime import datetime


class UngriddedAggregator(object):

    def __init__(self, data, grid):
        self.data = data
        self._grid = grid

    def get_grid(self, coord):
        from cis.utils import guess_coord_axis
        grid = None
        guessed_axis = guess_coord_axis(coord)
        if coord.name() in self._grid:
            grid = self._grid.pop(coord.name())
        elif hasattr(coord, 'var_name') and coord.var_name in self._grid:
            grid = self._grid.pop(coord.var_name)
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

    def aggregate(self, kernel):
        """
        Performs aggregation for ungridded data by first generating a new grid, converting it into a cube, then
        collocating using the appropriate kernel and a cube cell constraint
        """
        from cis.exceptions import CoordinateNotFoundError
        from cis.utils import isnan
        from iris.cube import Cube
        from cis.collocation.col_implementations import GeneralGriddedCollocator, BinnedCubeCellOnlyConstraint
        new_cube_coords = []
        new_cube_shape = []

        i = 0

        for coord in self.data.coords():
            grid, guessed_axis = self.get_grid(coord)
            if grid is None:
                new_coord = self._make_fully_collapsed_coord(coord)
            if grid is not None and isnan(grid.delta):
                # TODO: Remove this isnan - the delta should just be None if not specified
                # Issue a warning and then still collapse fully
                logging.warning('Coordinate ' + guessed_axis + ' was given without a grid. No need to specify '
                                'coordinates for complete collapse, all coordinates without a grid specified are '
                                'automatically collapsed for ungridded aggregation.')
                new_coord = self._make_fully_collapsed_coord(coord)
            if grid is not None and not isnan(grid.delta):
                new_coord = self._make_partially_collapsed_coord(coord, grid, guessed_axis)
            new_cube_coords.append((new_coord, i))
            new_cube_shape.append(len(new_coord.points))
            i += 1

        if len(self._grid) != 0:
            raise CoordinateNotFoundError("No coordinate found that matches '{}'. Please check the coordinate "
                                          "name.".format("' or '".join(list(self._grid.keys()))))

        dummy_data = np.reshape(np.arange(int(np.prod(new_cube_shape))) + 1.0, tuple(new_cube_shape))
        aggregation_cube = Cube(dummy_data, dim_coords_and_dims=new_cube_coords)

        collocator = GeneralGriddedCollocator()
        constraint = BinnedCubeCellOnlyConstraint()
        aggregated_cube = collocator.collocate(aggregation_cube, self.data, constraint, kernel)
        self._add_max_min_bounds_for_collapsed_coords(aggregated_cube, self.data)

        # We need to rename any variables which clash with coordinate names otherwise they will not output correctly, we
        # prepend it with 'aggregated_' to make it clear which variable has been aggregated (the original coordinate
        # value will not have been.)
        for idx, d in enumerate(aggregated_cube):
            if d.var_name in [coord.var_name for coord in aggregation_cube.coords()]:
                new_name = "aggregated_" + d.var_name
                aggregated_cube[idx].rename(new_name)
                aggregated_cube[idx].var_name = new_name
                logging.warning("Variable {} clashes with a coordinate variable name and has been renamed to: {}"
                                .format(d.var_name, new_name))

        return aggregated_cube

    @staticmethod
    def _get_CF_coordinate_units(coord):
        """
        Return a CF compliant coordinate unit from a given Coord. Tries common units based on coordinate standard names
        if needed.
        :param coord: A data_io.Coord.Coord object
        :return: a valid cf_units.Unit
        :raises ValueError for invalid CF units (which can't be fixed)
        """
        from cf_units import as_unit
        coordinate_unit_mappings = {'latitude': 'degrees_north', 'longitude': 'degrees_east'}

        try:
            coord_unit = as_unit(coord.units)
        except ValueError as e:
            if e.args[0].startswith('[UT_UNKNOWN]') and coord.standard_name in coordinate_unit_mappings:
                # For some common coordinates we can fix this...
                coord_unit = as_unit(coordinate_unit_mappings[coord.standard_name])
                logging.warning("Converting units for {coord} from {old} to the CF-compliant units: {new}"
                                .format(**{'coord': coord.standard_name, 'old': coord.units, 'new': coord_unit}))
            else:
                # Otherwise give up
                raise e
        return coord_unit

    def _make_fully_collapsed_coord(self, coord):
        """
        Make a new DimCoord which represents a fully collapsed coordinate.
        This DimCoord will have infinite bounds so as to include all points.
        :param coord:
        :return:
        """
        from iris.coords import DimCoord
        cell_start, cell_end, cell_centre = self._get_coord_start_end_centre(coord)
        cell_points = np.array([cell_centre])
        cell_bounds = np.array([[-np.inf, np.inf]])
        new_coord = DimCoord(cell_points, var_name=coord.name(), standard_name=coord.standard_name,
                             units=self._get_CF_coordinate_units(coord), bounds=cell_bounds)
        return new_coord

    def _make_partially_collapsed_coord(self, coord, grid, guessed_axis):
        """
        Make a new DimCoord which represents a partially collapsed (aggregated into bins) coordinate.
        This dimcoord will have a grid
        :type coord: data_io.Coord.Coord
        :param coord: Coordinate to partially collapse
        :type grid: aggregation.aggregation_grid.AggregationGrid
        :param grid: grid on which this coordinate will aggregate
        :type guessed_axis: str
        :param guessed_axis: String identifier of the axis to which this coordinate belongs (e.g. 'T', 'X')
        :return: DimCoord
        """
        from cis.subsetting.subset import _convert_datetime_to_coord_unit, _fix_non_circular_limits
        from iris.coords import DimCoord
        from cis.time_util import PartialDateTime
        if isinstance(grid.start, datetime):
            # Ensure that the limits are date/times.
            grid_start = _convert_datetime_to_coord_unit(coord, grid.start)
            grid_end = _convert_datetime_to_coord_unit(coord, grid.end)
            grid_delta = grid.delta
        elif isinstance(grid.start, PartialDateTime):
            dt_start, dt_end = grid.start.range()
            grid_start = _convert_datetime_to_coord_unit(coord, dt_start)
            grid_end = _convert_datetime_to_coord_unit(coord, dt_end)
            grid_delta = grid.delta
        else:
            # Assume to be a non-time axis
            (grid_start, grid_end) = _fix_non_circular_limits(float(grid.start), float(grid.end))
            grid_delta = float(grid.delta)
        new_coordinate_grid = aggregation_grid_array(grid_start, grid_end, grid_delta, grid.is_time, coord)
        new_coord = DimCoord(new_coordinate_grid, var_name=coord.name(), standard_name=coord.standard_name,
                             units=self._get_CF_coordinate_units(coord))
        if len(new_coord.points) == 1:
            new_coord.bounds = [[grid_start, grid_end]]
        else:
            new_coord.guess_bounds()
        return new_coord

    def _add_max_min_bounds_for_collapsed_coords(self, aggregated_cube, source_cube):
        """
        Add bounds onto all coordinates which have been full collapsed, and for which no explicit bounds have been
        supplied (iris will have guessed these to be +/- inf). The new bounds will be the maximum and minimum values of
        those coordinates
        :param aggregated_cube: The aggregated cube to give new bounds
        :param source_cube: The source cube which the aggregation was made from.
        """
        for coord in aggregated_cube.coords():
            if len(coord.points) == 1 and np.all(np.isinf(coord.bounds)):
                source_coord = source_cube.coord(coord.name())
                coord_start, coord_end, coord_centre = self._get_coord_start_end_centre(source_coord)
                coord.bounds = np.array([[coord_start, coord_end]])

    def _get_coord_start_end_centre(self, coord):
        """
        Get the coordinates start, end and midpoint values
        :param coord: Coordinate
        :return: Tuple of (start, end, midpoint)
        """
        start = np.min(coord.points)
        end = np.max(coord.points)
        centre = start + (end - start) / 2.0
        return start, end, centre


def add_year_midpoint(dt_object, years):
    if not isinstance(years, int):
        raise TypeError
    if not isinstance(dt_object, datetime):
        raise TypeError

    new_month = dt_object.month + 6 * (years % 2)
    new_year = dt_object.year + years // 2
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    return dt_object.replace(year=new_year, month=new_month)


def add_month_midpoint(dt_object, months):
    from datetime import timedelta
    if not isinstance(months, int):
        raise TypeError
    if not isinstance(dt_object, datetime):
        raise TypeError

    new_month = dt_object.month + months // 2
    new_year = dt_object.year
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    dt_object = dt_object.replace(year=new_year, month=new_month)

    if months % 2 != 0:
        dt_object += timedelta(days=14, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    return dt_object


def month_past_end_of_year(month, year):
    year += month // 12
    month %= 12
    if month == 0:
        month = 12

    return month, year


def aggregation_grid_array(start, end, delta, is_time, coordinate):
    from cis.subsetting.subset import _convert_coord_unit_to_datetime, _convert_datetime_to_coord_unit
    from datetime import timedelta
    if is_time:
        start_dt = _convert_coord_unit_to_datetime(coordinate, start)
        end_dt = _convert_coord_unit_to_datetime(coordinate, end)

        # Some logic to find the mid point to start on
        if delta.year > 0:
            start_dt = add_year_midpoint(start_dt, delta.year)

        # We make an assumption here that half a month is always 15 days.
        if delta.month > 0:
            start_dt = add_month_midpoint(start_dt, delta.month)

        dt = timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
                                minutes=delta.minute, hours=delta.hour, weeks=0)

        start_dt += dt / 2

        new_time_grid = []
        new_time = start_dt

        while new_time < end_dt:
            new_time_grid.append(_convert_datetime_to_coord_unit(coordinate, new_time))

            new_year = new_time.year + delta.year
            new_month = new_time.month + delta.month
            if new_month > 12:
                new_month, new_year = month_past_end_of_year(new_month, new_year)
            # TODO this is a slightly inelegant fix for the problem of something like 30th Jan +1 month
            # Need to work out what correct behaviour should be in this case.
            try:
                new_time = new_time.replace(year=new_year, month=new_month)
            except ValueError:
                new_time += timedelta(days=28)
            new_time += timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
                                           minutes=delta.minute, hours=delta.hour, weeks=0)

        new_time_grid = np.array(new_time_grid)

        return new_time_grid
    else:
        new_grid = np.arange(start + delta / 2, end + delta / 2, delta)

        return new_grid


def find_nearest(array, value):
    """
    Find the nearest to the parameter value in the array
    :param array: A numpy array
    :param value: A single value
    :return: A single value from the array
    """
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def categorise_coord_function(start, end, delta, is_time):
    def returned_func(coordinate, value):
        return find_nearest(aggregation_grid_array(start, end, delta, is_time, coordinate), value)

    return returned_func
