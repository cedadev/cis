import numpy as np

from jasmin_cis.kdtree import HaversineDistanceKDTree
from jasmin_cis.data_io.hyperpoint import HyperPoint


class HaversineDistanceKDTreeIndex(object):
    """k-D tree index using distance along the surface 
    """
    def __init__(self):
        self.index = None

    def index_data(self, points, data, coord_map):
        """
        @param points: sample points
        @param data: list of HyperPoints to index
        @param coord_map: list of tuples relating index in HyperPoint to index in sample point
                          coords and in coords to be output
        """
        lat = data.coords[HyperPoint.LATITUDE]
        lon = data.coords[HyperPoint.LONGITUDE]
        spatial_points = np.ma.empty((len(data), 2))
        spatial_points[:, 0] = lat
        spatial_points[:, 1] = lon
        mask = np.ma.getmask(data.data)
        self.index = HaversineDistanceKDTree(spatial_points, mask=mask)

    def find_nearest_point(self, point):
        query_pt = [[point.latitude, point.longitude]]
        (distances, indices) = self.index.query(query_pt)
        if distances[0] == np.inf:
            return None
        else:
            return indices[0]

    def find_points_within_distance(self, point, distance):
        query_pt = [[point.latitude, point.longitude]]
        return self.index.query_ball_point(query_pt, distance)[0]
