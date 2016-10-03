import logging
import datetime

import iris.coord_categorisation
import iris.analysis.cartography
from iris.coords import DimCoord
import numpy as np

from cis.collocation.col_implementations import GeneralGriddedCollocator, BinnedCubeCellOnlyConstraint
import cis.parse_datetime as parse_datetime
from cis.subsetting.subset import Subset
from cis.utils import isnan, guess_coord_axis
from cis.exceptions import ClassNotFoundError, CoordinateNotFoundError
from cis.aggregation.aggregation_kernels import MultiKernel
from cis.data_io.gridded_data import GriddedDataList
from functools import reduce


class Aggregator(object):
    def __init__(self, data, grid):
        self.data = data
        self._grid = grid

    @staticmethod
    def _partially_collapse_multidimensional_coord(coord, dims_to_collapse, kernel=iris.analysis.MEAN):
        import operator

        # First calculate our new shape and dims
        dims_to_collapse = sorted(dims_to_collapse)
        end_size = reduce(operator.mul, (coord.shape[dim] for dim in dims_to_collapse))
        untouched_dims = list(set(range(coord.ndim)) - set(dims_to_collapse))
        untouched_shape = [coord.shape[dim] for dim in untouched_dims]
        new_shape = untouched_shape + [end_size]
        dims = untouched_dims + dims_to_collapse

        # Then reshape the data so that the dimensions being aggregated
        # over are grouped 'at the end' (i.e. axis=-1).
        unrolled_data = np.transpose(coord.points, dims).reshape(new_shape)

        new_points = kernel.aggregate(unrolled_data, axis=-1)
        new_coord = coord.copy(points=new_points)
        return new_coord

    @staticmethod
    def _calc_new_dims(coord_dims, dims_to_collapse):
        """
            Calculate the new dimensions for the coordinate.
        :param coord_dims: the original dimensions
        :param dims_to_collapse: The dimensions which are being collapsed over
        :return: The new coordinates which the coord will take on the collapsed cube
        """
        new_dims = []
        # For each original dimension subtract one for every collapsed coordinate which came before it.
        # TODO: There must be a cleaner way to do this...
        for d in coord_dims:
            new_d = d
            for dc in dims_to_collapse:
                if d > dc:
                    new_d -= 1
            # If the dimension is one being collapsed then we don't include it in the new dimensions
            if d not in dims_to_collapse:
                new_dims.append(new_d)

        return new_dims

    @staticmethod
    def _update_aux_factories(data, *args, **kwargs):
        from cis.utils import listify
        d_list = listify(data)
        for d in d_list:
            for factory in d.aux_factories:
                factory.update(*args, **kwargs)

    def _gridded_full_collapse(self, coords, kernel):
        from cis.utils import demote_warnings
        from copy import deepcopy
        ag_args = {}
        if isinstance(kernel, iris.analysis.WeightedAggregator):
            # If this is a list we can calculate weights using the first item (all variables should be on
            # same grid)
            data_for_weights = self.data[0] if isinstance(self.data, list) else self.data
            # Weights to correctly calculate areas.
            logging.info("Calculating area weights for gridded collapse")
            # Iris throws warnings about which radius it's using to calculate the weights, but these are really just
            #  INFO level things.
            with demote_warnings():
                ag_args['weights'] = iris.analysis.cartography.area_weights(data_for_weights)
        elif not isinstance(kernel, iris.analysis.Aggregator):
            raise ClassNotFoundError('Error - unexpected aggregator type.')

        dims_to_collapse = set()
        for coord in coords:
            dims_to_collapse.update(self.data.coord_dims(coord))

        coords_for_partial_collapse = []

        # Collapse any coords that span the dimension(s) being collapsed
        for coord in self.data.aux_coords:
            coord_dims = self.data.coord_dims(coord)
            # If a coordinate has any of the dimensions we wan't to collapse AND has some dimensions we don't...
            if set(dims_to_collapse).intersection(coord_dims) and \
                    set(coord_dims).difference(dims_to_collapse):
                # ... add it to our list of partial coordinates to collapse.
                coords_for_partial_collapse.append((coord, coord_dims))

        # Before we remove the coordinates which need to be partially collapsed we take a copy of the data. We need
        #  this so that the aggregation doesn't have any side effects on the input data. This is particularly important
        #  when using a MultiKernel for which this routine gets called multiple times.
        data_for_collapse = deepcopy(self.data)

        for coord, _ in coords_for_partial_collapse:
            data_for_collapse.remove_coord(coord)

        new_data = data_for_collapse.collapsed(coords, kernel, **ag_args)

        for coord, old_dims in coords_for_partial_collapse:
            collapsed_coord = Aggregator._partially_collapse_multidimensional_coord(coord, dims_to_collapse)
            new_dims = Aggregator._calc_new_dims(old_dims, dims_to_collapse)

            new_data.add_aux_coord(collapsed_coord, new_dims)
            # If the coordinate we had to collapse manually was a dependency in an aux factory (which is quite likely)
            #  then we need to put it back in and fix the factory, this will update any missing dependencies.
            self._update_aux_factories(new_data, None, collapsed_coord)

        return new_data

    def aggregate_gridded(self, kernel):
        # Make sure all coordinate have bounds - important for weighting and aggregating
        # Only try and guess bounds on Dim Coords
        for coord in self.data.coords(dim_coords=True):
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
        collocating using the appropriate kernel and a cube cell constraint
        """
        new_cube_coords = []
        new_cube_shape = []

        i = 0

        for coord in self.data.coords():
            grid, guessed_axis = self.get_grid(coord)
            if grid is None:
                new_coord = self._make_fully_collapsed_coord(coord)
            if grid is not None and isnan(grid.delta):
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
        aggregation_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=new_cube_coords)

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

    def get_grid(self, coord):

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


def add_year_midpoint(dt_object, years):
    if not isinstance(years, int):
        raise TypeError
    if not isinstance(dt_object, datetime.datetime):
        raise TypeError

    new_month = dt_object.month + 6 * (years % 2)
    new_year = dt_object.year + years // 2
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    return dt_object.replace(year=new_year, month=new_month)


def add_month_midpoint(dt_object, months):
    if not isinstance(months, int):
        raise TypeError
    if not isinstance(dt_object, datetime.datetime):
        raise TypeError

    new_month = dt_object.month + months // 2
    new_year = dt_object.year
    if new_month > 12:
        new_month, new_year = month_past_end_of_year(new_month, new_year)

    dt_object = dt_object.replace(year=new_year, month=new_month)

    if months % 2 != 0:
        dt_object += datetime.timedelta(days=14, seconds=0, microseconds=0, milliseconds=0,
                                        minutes=0, hours=0, weeks=0)

    return dt_object


def month_past_end_of_year(month, year):
    year += month // 12
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

        start_dt += dt / 2

        new_time_grid = []
        new_time = start_dt

        while new_time < end_dt:
            new_time_grid.append(Subset._convert_datetime_to_coord_unit(coordinate, new_time))

            new_year = new_time.year + delta.year
            new_month = new_time.month + delta.month
            if new_month > 12:
                new_month, new_year = month_past_end_of_year(new_month, new_year)
            # TODO this is a slightly inelegant fix for the problem of something like 30th Jan +1 month
            # Need to work out what correct behaviour should be in this case.
            try:
                new_time = new_time.replace(year=new_year, month=new_month)
            except ValueError:
                new_time += datetime.timedelta(days=28)
            new_time += datetime.timedelta(days=delta.day, seconds=delta.second, microseconds=0, milliseconds=0,
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
