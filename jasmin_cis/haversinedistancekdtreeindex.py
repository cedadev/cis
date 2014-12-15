import numpy as np

from jasmin_cis.kdtree import HaversineDistanceKDTree
from jasmin_cis.data_io.hyperpoint import HyperPoint


class HaversineDistanceKDTreeIndex(object):
    """k-D tree index that can be used to query using distance along the Earth's surface.
    """
    def __init__(self):
        self.index = None

    def index_data(self, points, data, coord_map, leafsize=10):
        """
        Creates the k-D tree index.

        :param points: (not used) sample points
        :param data: list of HyperPoints to index
        :param coord_map: (not used) list of tuples relating index in HyperPoint
                          to index in sample point coords and in coords to be output
        """
        if len(data.data.shape) > 1:
            # Flatten coordinates.
            lat_idx = [key for key, value in data.dims_to_std_coords_map.items()
                       if value == HyperPoint.LATITUDE][0]
            lon_idx = [key for key, value in data.dims_to_std_coords_map.items()
                       if value == HyperPoint.LONGITUDE][0]
            flattened_coords = np.meshgrid(*data.coords, indexing='ij')
            lat = flattened_coords[lat_idx].ravel()
            lon = flattened_coords[lon_idx].ravel()
        else:
            lat = data.coords[HyperPoint.LATITUDE]
            lon = data.coords[HyperPoint.LONGITUDE]
        spatial_points = np.ma.empty((len(data), 2))
        spatial_points[:, 0] = lat
        spatial_points[:, 1] = lon
        mask = np.ma.getmask(data.data).ravel()
        self.index = HaversineDistanceKDTree(spatial_points, mask=mask, leafsize=leafsize)

    def find_nearest_point(self, point):
        """Finds the indexed point nearest to a specified point.
        :param point: point for which the nearest point is required
        :return: index in data of closest point
        """
        query_pt = [[point.latitude, point.longitude]]
        (distances, indices) = self.index.query(query_pt)
        if distances[0] == np.inf:
            return None
        else:
            return indices[0]

    def find_points_within_distance(self, point, distance):
        """Finds the points within a specified distance of a specified point.
        :param point: reference point
        :param distance: distance in kilometres
        :return: list indices in data of points
        """
        query_pt = [[point.latitude, point.longitude]]
        return self.index.query_ball_point(query_pt, distance)[0]
