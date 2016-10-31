import logging
import numpy as np
from datetime import datetime


class UngriddedAggregator(object):

    def __init__(self, grid):
        self._grid = grid

    def aggregate(self, data, kernel):
        """
        Performs aggregation for ungridded data by first generating a new grid, converting it into a cube, then
        collocating using the appropriate kernel and a cube cell constraint
        """
        from cis.exceptions import CoordinateNotFoundError
        from iris.cube import Cube
        from cis.collocation.col_implementations import GeneralGriddedCollocator, BinnedCubeCellOnlyConstraint
        new_cube_coords = []
        new_cube_shape = []

        for i, coord in enumerate(data.coords()):
            # Pop off the grid once we have it so that we can check for coords we didn't find
            grid = self._grid.pop(coord.name(), None)
            if grid is None:
                new_coord = self._make_fully_collapsed_coord(coord)
            else:
                new_coord = self._make_partially_collapsed_coord(coord, grid)
            new_cube_coords.append((new_coord, i))
            new_cube_shape.append(len(new_coord.points))

        if len(self._grid) != 0:
            raise CoordinateNotFoundError("No coordinate found that matches '{}'. Please check the coordinate "
                                          "name.".format("' or '".join(list(self._grid.keys()))))

        dummy_data = np.reshape(np.arange(int(np.prod(new_cube_shape))) + 1.0, tuple(new_cube_shape))
        aggregation_cube = Cube(dummy_data, dim_coords_and_dims=new_cube_coords)

        collocator = GeneralGriddedCollocator()
        constraint = BinnedCubeCellOnlyConstraint()
        aggregated_cube = collocator.collocate(aggregation_cube, data, constraint, kernel)
        self._add_max_min_bounds_for_collapsed_coords(aggregated_cube, data)

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

    def _make_partially_collapsed_coord(self, coord, grid):
        """
        Make a new DimCoord which represents a partially collapsed (aggregated into bins) coordinate.
        This dimcoord will have a grid
        :type coord: data_io.Coord.Coord
        :param coord: Coordinate to partially collapse
        :type grid: slice
        :param grid: grid on which this coordinate will aggregate
        :return: DimCoord
        """
        from iris.coords import DimCoord
        new_coordinate_grid = aggregation_grid_array(grid.start, grid.stop, grid.step)
        new_coord = DimCoord(new_coordinate_grid, var_name=coord.name(), standard_name=coord.standard_name,
                             units=self._get_CF_coordinate_units(coord))
        if len(new_coord.points) == 1:
            new_coord.bounds = [[grid.start, grid.stop]]
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


def aggregation_grid_array(start, end, delta):
    from cis.time_util import cis_standard_time_unit
    new_grid = np.arange(start + delta / 2, end + delta / 2, delta)
    if 'datetime64' in str(new_grid.dtype):
        # This goes via datetimes with all the associated overheads but is probably safer than doing it manually
        new_grid = cis_standard_time_unit.date2num(new_grid.astype(datetime))
    return new_grid
