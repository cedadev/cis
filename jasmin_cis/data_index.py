"""
Indexes over data used for fast lookup when colocating.
"""
import logging
import math

import numpy as np

from jasmin_cis.haversinedistancekdtreeindex import HaversineDistanceKDTreeIndex


class GridCellBinIndex(object):
    def __init__(self):
        self.index = None

    def index_data(self, coords, data, coord_map):
        """
        @param coords: coordinates of grid
        @param data: list of HyperPoints to index
        @param coord_map: list of tuples relating index in HyperPoint to index in coords and in
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
                if (search_index >= 0) and (point[hpi] <= upper_bounds[ci][search_index]):
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


_index_attributes = {'grid_cell_bin_index': GridCellBinIndex,
                     'haversine_distance_kd_tree_index': HaversineDistanceKDTreeIndex}


def create_indexes(operator, coords, data, coord_map):
    for attr, cls in _index_attributes.iteritems():
        if hasattr(operator, attr) and (getattr(operator, attr) is None):
            index = cls()
            logging.info("--> Creating index for %s", operator.__class__.__name__)
            index.index_data(coords, data, coord_map)
            setattr(operator, attr, index)
