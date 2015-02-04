"""
Indexes over data used for fast lookup when colocating.
"""
import logging
import math
import datetime

import numpy as np
import numpy.ma as ma

from jasmin_cis.haversinedistancekdtreeindex import HaversineDistanceKDTreeIndex
from time_util import convert_obj_to_standard_date_array


class GridCellBinIndexInSlices(object):
    def __init__(self):
        # cells numbers for each hyperpoint
        self.cell_numbers = None

        # sort order for each hyperpoint, i.e. where they are
        self.sort_order = None

        # position of each hyperpoint in the grid (coordinate x point)
        self._indices = None

        # indexes for the slices through the sorted data.
        # e.g. cell_slices_index[0] = [0, 2] would be points 0, 1 and 2 are in the first cell
        self.cell_slices_indices = None

        # hyper point cordinates list
        self.hp_coords = None

    def index_data(self, coords, hyper_points, coord_map):
        """
        Index the data that falls inside the grid cells

        :param coords: coordinates of grid
        :param hyper_points: list of HyperPoints to index
        :param coord_map: list of tuples relating index in HyperPoint to index in coords and in
                          coords to be iterated over
        """

        #create bounds in correct order
        hp_coords = []
        coord_descreasing = [False] * len(coords)
        coord_lengths = [0] * len(coords)
        lower_bounds = [None] * len(coords)
        max_bounds = [None] * len(coords)
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            # Coordinates must be monotonic; determine whether increasing or decreasing.
            if len(coord.points) > 1:
                if coord.points[1] < coord.points[0]:
                    coord_descreasing[shi] = True
            coord_lengths[shi] = len(coord.points)
            if coord_descreasing[shi]:
                lower_bounds[shi] = coord.bounds[::-1, 1]
                max_bounds[shi] = coord.bounds[0, 1]
            else:
                lower_bounds[shi] = coord.bounds[::, 0]
                max_bounds[shi] = coord.bounds[-1, 1]

            hp_coord = hyper_points.coords[hpi]
            if isinstance(hp_coord[0], datetime.datetime):
                hp_coord = convert_obj_to_standard_date_array(hp_coord)

            hp_coords.append(hp_coord)

        bounds_coords_max = zip(lower_bounds, hp_coords, max_bounds)

        # stack for each coordinate
        #    where the coordinate is larger than the maximum set to -1
        #    otherwise search in the sorted coordinate to find all the index of the hyperpoints
        # The choice of 'left' or 'right' and '<' and '<=' determines which
        #  cell is chosen when the coordinate is equal to the boundary.
        # -1 or M_i indicates the point is outside the grid.
        # Output is a list of coordinates which lists the indexes where the hyper points
        #    should be located in the grid
        indices = np.vstack(
            np.where(
                ci < max_coordinate_value,
                np.searchsorted(bi, ci, side='right') - 1,
                -1)
            for bi, ci, max_coordinate_value in bounds_coords_max)

        # D-tuple giving the shape of the output grid
        grid_shape = tuple(len(bi_ci[0]) for bi_ci in bounds_coords_max)

        # shape (N,) telling which points actually fall within the grid,
        # i.e. have indexes that are not -1 and are not masked data points
        grid_mask = np.all(
            (indices >= 0) &
            (ma.getmaskarray(hyper_points.data) == False),
            axis=0)

        # if the coordinate was decreasing then correct the indices for this cell
        for indices_slice, decreasing, coord_length in zip(xrange(indices.shape[0]), coord_descreasing, coord_lengths):
            if decreasing:
                #indices[indices_slice] += (coord_length - 1) - indices[indices_slice]
                indices[indices_slice] *= -1
                indices[indices_slice] += (coord_length - 1)

        # shape (N,) containing negative scalar cell numbers for each
        # input point (sequence doesn't matter so long as they are unique), or
        # -1 for points outside the grid.
        #
        # Possibly numpy.lexsort could be used to avoid the need for this,
        # although we'd have to be careful about points outside the grid.
        self.cell_numbers = np.where(
            grid_mask,
            np.tensordot(
                np.cumproduct((1,) + grid_shape[:-1]),
                indices,
                axes=1
            ),
            -1)

        # Sort everything by cell number
        self.sort_order = np.argsort(self.cell_numbers)
        self.cell_numbers = self.cell_numbers[self.sort_order]
        self._indices = indices[:, self.sort_order]
        self.hp_coords = [hp_coord[:, self.sort_order] for hp_coord in hp_coords]

    def get_iterator(self):
        """
        Get an iterator through all the points which will contribute to a cell.
        Iteration is through out indices (where the data point is in the grid) and the
        (start, stop) indexes in a sorted list of the points in that cell.
        self.sort_order can be used to order the list

        :return: an iterator out_indices, cell_slice_indices
        """

        # find the index at which the cell number changes, +1 to make this the first point with the new
        # cell number
        indexes_of_first_element_in_slice = np.flatnonzero(np.diff(self.cell_numbers)) + 1

        # shape (L,2) giving the pairs (first, last+1) of indices such that
        # cell_numbers[first:last+1] is the slice of all the elements of each
        # of the L unique values.

        #if some of the points are not in the grid skip these
        if self.cell_numbers[0] == -1:
            #if there are no points in the grid (all -1s)
            if indexes_of_first_element_in_slice.size == 0:
                self.cell_slices_indices = []
            else:
                # for list of start stop indexes starting at first point in the grid
                self.cell_slices_indices = np.concatenate((
                    indexes_of_first_element_in_slice[:1],
                    np.tile(indexes_of_first_element_in_slice[1:], 2),
                    [len(self.cell_numbers)]
                )).reshape(2, -1).T
        else:
            #create list of start stop indexes starting at 0
            self.cell_slices_indices = np.concatenate((
                [0],  # start at first element
                np.tile(indexes_of_first_element_in_slice, 2),
                [len(self.cell_numbers)]  # last at first element
            )).reshape(2, -1).T  # reshape so that it is list of start-end indices

        #iterate around slices
        for cell_slice_indices in self.cell_slices_indices:
            out_indices = tuple(self._indices[:, cell_slice_indices[0]])
            yield out_indices, cell_slice_indices


class GridCellBinIndex(object):
    def __init__(self):
        self.index = None

    def index_data(self, coords, data, coord_map):
        """
        Creates an index of points that fall within grid cells.

        :param coords: coordinates of grid
        :param data: list of HyperPoints to index
        :param coord_map: list of tuples relating index in HyperPoint to index in coords and in
                          coords to be iterated over
        """
        # Create an index array matching the shape of the coordinates to be iterated over.
        shape = []
        for (hpi, ci, shi) in coord_map:
            shape.append(len(coords[ci].points))
        num_cell_indices = len(shape)

        # Set a logging interval.
        num_bin_checks = sum([math.log(x) for x in shape])
        log_every_points = 2000000 / num_bin_checks
        log_every_points -= log_every_points % 100
        log_every_points = max(log_every_points, 100)

        # Create the index, which will be an array containing of a lists of data points that are
        # within each cell.
        self.index = np.empty(tuple(shape), dtype=np.dtype(object))
        self.index.fill(None)

        coord_descreasing = [False] * len(coords)
        coord_lengths = [0] * len(coords)
        lower_bounds = [None] * len(coords)
        upper_bounds = [None] * len(coords)
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            # Coordinates must be monotonic; determine whether increasing or decreasing.
            if len(coord.points) > 1:
                if coord.points[1] < coord.points[0]:
                    coord_descreasing[ci] = True
            coord_lengths[ci] = len(coord.points)
            if coord_descreasing[ci]:
                lower_bounds[ci] = coord.bounds[::-1, 1]
                upper_bounds[ci] = coord.bounds[::-1, 0]
            else:
                lower_bounds[ci] = coord.bounds[::, 0]
                upper_bounds[ci] = coord.bounds[::, 1]

        # Populate the index by finding the cell containing each data point.
        num_points = len(data)
        pt_count = 0
        pt_total = 0
        for pt_idx, point in data.enumerate_non_masked_points():
            point_cell_indices = [None] * num_cell_indices

            # Find the interval that the point resides in for each relevant coordinate.
            for (hpi, ci, shi) in coord_map:
                search_index = np.searchsorted(lower_bounds[ci], point[hpi], side='right') - 1
                if (search_index >= 0) and (point[hpi] < upper_bounds[ci][search_index]):
                    if coord_descreasing[ci]:
                        point_cell_indices[shi] = coord_lengths[ci] - search_index - 1
                    else:
                        point_cell_indices[shi] = search_index

            # Add point to index if a containing interval was found for each coordinate.
            if point_cell_indices.count(None) == 0:
                index_entry = self.index[tuple(point_cell_indices)]
                if index_entry is None:
                    index_entry = []
                index_entry.append(pt_idx)
                self.index[tuple(point_cell_indices)] = index_entry

            # Periodically log progress.
            pt_count += 1
            pt_total += 1
            if pt_count == log_every_points:
                logging.info("    Indexed %d points of %d (%d%%)",
                             pt_total, num_points, int(pt_total * 100 / num_points))
                pt_count = 0

    def get_points_by_indices(self, indices):
        return self.index[tuple(indices)]


# Map of names of attributes of a constraint or kernel to the class used to
# create an index to which the attribute should be set
_index_attributes = {'grid_cell_bin_index': GridCellBinIndex,
                     'grid_cell_bin_index_slices': GridCellBinIndexInSlices,
                     'haversine_distance_kd_tree_index': HaversineDistanceKDTreeIndex}


def create_indexes(operator, coords, data, coord_map):
    """
    :param operator: constraint or kernel instance
    :param coords: coordinates of grid
    :param data: list of HyperPoints to index
    :param coord_map: list of tuples relating index in HyperPoint to index in coords and in
                      coords to be iterated over
    """
    for attr, cls in _index_attributes.iteritems():
        if hasattr(operator, attr) and (getattr(operator, attr) is None):
            index = cls()
            logging.info("--> Creating index for %s", operator.__class__.__name__)
            index.index_data(coords, data, coord_map)
            setattr(operator, attr, index)
