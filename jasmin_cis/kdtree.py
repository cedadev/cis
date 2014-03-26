from heapq import heappush, heappop
import math

import numpy as np
from scipy.spatial.kdtree import KDTree, Rectangle

from jasmin_cis.data_io.hyperpoint import HyperPoint


RADIUS_EARTH = 6378000


def haversine_distance(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    return haversine(x, y)


def haversine(x, y):
    """Computes the Haversine distance between two points"""
    lat1, lon1 = x[:, 0], x[:, 1]
    lat2, lon2 = y[:, 0], y[:, 1]
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    arclen = 2 * np.arcsin(np.sqrt((np.sin((lat2 - lat1) / 2)) ** 2
                                   + np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1) / 2)) ** 2))
    return arclen * RADIUS_EARTH


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
        if distances[0] == np.inf or distances[0] > 0.5:
            return None
        else:
            return indices[0]


class HaversineDistanceKDTree(KDTree):
    """Modification of the scipy.spatial.KDTree class to allow querying for
    nearest neighbours measured by distance along the Earth's surface.
    """
    def __init__(self, data, leafsize=10, mask=None):
        self.data = np.ma.asarray(data)
        if mask is not None:
            self.data.mask = mask
        self.n, self.m = np.shape(self.data)
        self.leafsize = int(leafsize)
        if self.leafsize<1:
            raise ValueError("leafsize must be at least 1")
        self.maxes = np.amax(self.data, axis=0)
        self.mins = np.amin(self.data, axis=0)

        indices = np.arange(self.n)
        if mask is not None:
            indices = np.ma.array(indices, mask=mask)
            indices = indices.compressed()
        self.tree = self._KDTree__build(indices, self.maxes, self.mins)

    def __query(self, x, k=1, eps=0, p=2, distance_upper_bound=np.inf):

        side_distances = np.maximum(0,np.maximum(x-self.maxes,self.mins-x))
        if p!=np.inf:
            side_distances**=p
            min_distance = np.sum(side_distances)
        else:
            min_distance = np.amax(side_distances)

        # priority queue for chasing nodes
        # entries are:
        #  minimum distance between the cell and the target
        #  distances between the nearest side of the cell and the target
        #  the head node of the cell
        q = [(min_distance,
              tuple(side_distances),
              self.tree)]
        # priority queue for the nearest neighbors
        # furthest known neighbor first
        # entries are (-distance**p, i)
        neighbors = []

        if eps==0:
            epsfac=1
        elif p==np.inf:
            epsfac = 1/(1+eps)
        else:
            epsfac = 1/(1+eps)**p

        if p!=np.inf and distance_upper_bound!=np.inf:
            distance_upper_bound = distance_upper_bound**p

        while q:
            min_distance, side_distances, node = heappop(q)
            if isinstance(node, HaversineDistanceKDTree.leafnode):
                # brute-force
                data = self.data[node.idx]
                ds = haversine_distance(data,x[np.newaxis,:])
                for i in range(len(ds)):
                    if ds[i]<distance_upper_bound:
                        if len(neighbors)==k:
                            heappop(neighbors)
                        heappush(neighbors, (-ds[i], node.idx[i]))
                        if len(neighbors)==k:
                            distance_upper_bound = -neighbors[0][0]
            else:
                # we don't push cells that are too far onto the queue at all,
                # but since the distance_upper_bound decreases, we might get
                # here even if the cell's too far
                if min_distance>distance_upper_bound*epsfac:
                    # since this is the nearest cell, we're done, bail out
                    break
                # compute minimum distances to the children and push them on
                if x[node.split_dim]<node.split:
                    near, far = node.less, node.greater
                else:
                    near, far = node.greater, node.less

                # near child is at the same distance as the current node
                heappush(q,(min_distance, side_distances, near))

                # far child is further by an amount depending only
                # on the split value
                sd = list(side_distances)
                if p == np.inf:
                    min_distance = max(min_distance, abs(node.split-x[node.split_dim]))
                elif p == 1:
                    sd[node.split_dim] = np.abs(node.split-x[node.split_dim])
                    min_distance = min_distance - side_distances[node.split_dim] + sd[node.split_dim]
                else:
                    sd[node.split_dim] = np.abs(node.split-x[node.split_dim])**p
                    min_distance = min_distance - side_distances[node.split_dim] + sd[node.split_dim]

                # far child might be too far, if so, don't bother pushing it
                if min_distance<=distance_upper_bound*epsfac:
                    heappush(q,(min_distance, tuple(sd), far))

        if p==np.inf:
            return sorted([(-d,i) for (d,i) in neighbors])
        else:
            return sorted([((-d)**(1./p),i) for (d,i) in neighbors])

    def __query_ball_point(self, x, r, p=2., eps=0):
        R = Rectangle(self.maxes, self.mins)

        def traverse_checking(node, rect):
            if rect.min_distance_point(x, p) > r / (1. + eps):
                return []
            elif rect.max_distance_point(x, p) < r * (1. + eps):
                return traverse_no_checking(node)
            elif isinstance(node, KDTree.leafnode):
                d = self.data[node.idx]
                return node.idx[haversine_distance(d, x) <= r].tolist()
            else:
                less, greater = rect.split(node.split_dim, node.split)
                return traverse_checking(node.less, less) + \
                       traverse_checking(node.greater, greater)

        def traverse_no_checking(node):
            if isinstance(node, KDTree.leafnode):
                return node.idx.tolist()
            else:
                return traverse_no_checking(node.less) + \
                       traverse_no_checking(node.greater)

        return traverse_checking(self.tree, R)
