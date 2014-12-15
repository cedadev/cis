"""
# Copyright Anne M. Archibald 2008
# Released under the scipy license
"""

from __future__ import division, print_function, absolute_import

import sys
from heapq import heappush, heappop
import math

import numpy as np
import scipy.sparse

__all__ = ['minkowski_distance_p', 'minkowski_distance', 'haversine_distance',
           'distance_matrix',
           'Rectangle', 'KDTree']

RADIUS_EARTH = 6378.0
HALF_PI = np.pi / 2.0
PI = np.pi
TWO_PI = np.pi * 2.0


def minkowski_distance_p(x, y, p=2):
    """
    Compute the p-th power of the L**p distance between two arrays.

    For efficiency, this function computes the L**p distance but does
    not extract the pth root. If `p` is 1 or infinity, this is equal to
    the actual L**p distance.


    :param x: (M, K) array_like
        Input array.
    :param y: (N, K) array_like
        Input array.
    :param p: float, 1 <= p <= infinity
        Which Minkowski p-norm to use.

    Examples

    >>> minkowski_distance_p([[0,0],[0,0]], [[1,1],[0,1]])
    array([2, 1])

    """
    x = np.asarray(x)
    y = np.asarray(y)
    if p == np.inf:
        return np.amax(np.abs(y-x), axis=-1)
    elif p == 1:
        return np.sum(np.abs(y-x), axis=-1)
    else:
        return np.sum(np.abs(y-x)**p, axis=-1)

def minkowski_distance(x, y, p=2):
    """
    Compute the L**p distance between two arrays.

    :param x: (M, K) array_like
        Input array.
    :param y: (N, K) array_like
        Input array.
    :param p: float, 1 <= p <= infinity
        Which Minkowski p-norm to use.
    :return:

    Examples

    >>> minkowski_distance([[0,0],[0,0]], [[1,1],[0,1]])
    array([ 1.41421356,  1.        ])

    """
    x = np.asarray(x)
    y = np.asarray(y)
    if p == np.inf or p == 1:
        return minkowski_distance_p(x, y, p)
    else:
        return minkowski_distance_p(x, y, p)**(1./p)


def haversine_distance(x, y):
    """Computes the Haversine distance in kilometres between two points
    :param x: first point or array of points, each as array of latitude, longitude in degrees
    :param y: second point or array of points, each as array of latitude, longitude in degrees
    :return: distance between the two points in kilometres
    """
    x = np.asarray(x)
    y = np.asarray(y)
    return haversine(x, y)


def haversine(x, y):
    """Computes the Haversine distance in kilometres between two points
    :param x: first point or points as array, each as array of latitude, longitude in degrees
    :param y: second point or points as array, each as array of latitude, longitude in degrees
    :return: distance between the two points in kilometres
    """
    if x.ndim == 1:
        lat1, lon1 = x[0], x[1]
    else:
        lat1, lon1 = x[:, 0], x[:, 1]
    if y.ndim == 1:
        lat2, lon2 = y[0], y[1]
    else:
        lat2, lon2 = y[:, 0], y[:, 1]
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    arclen = 2 * np.arcsin(np.sqrt((np.sin((lat2 - lat1) / 2)) ** 2
                                   + np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1) / 2)) ** 2))
    return arclen * RADIUS_EARTH


def haversine_distance_from_radians(x, y):
    """Computes the Haversine distance in kilometres between two points
    :param x: first point as array of latitude, longitude in radians
    :param y: second point as array of latitude, longitude in radians
    :return: distance between the two points in kilometres
    """
    lat1, lon1 = x[0], x[1]
    lat2, lon2 = y[0], y[1]
    arclen = 2 * np.arcsin(np.sqrt((np.sin((lat2 - lat1) / 2)) ** 2
                                   + np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1) / 2)) ** 2))
    return arclen * RADIUS_EARTH


def geodesic_to_line_of_longitude_crossing_latitude(point, longitude):
    """Given a line of longitude and a point, finds the latitude at which the
    geodesic of shortest distance to the line of longitude crosses the line of
    longitude.
    :param point: point as array of latitude, longitude in radians
    :param longitude: longitude in radians
    :return: latitude at point of intersection in radians
    """
    pt_lat = point[0]
    pt_lon = point[1]

    # Derived from one of Napier's rules for right angled spherical triangles:
    # tan(pt_lat) = tan(latitude) * cos(pt_lon - longitude)
    # - behaves better as |pt_lon - longitude| -> pi/2
    try:
        sin_lat = math.sin(pt_lat) / math.sqrt(1 - math.cos(pt_lat) ** 2 * math.sin(pt_lon - longitude) ** 2)
    except ZeroDivisionError:
        # pt_lat = +/- pi/2 and pt_lon - longitude = pi/2 + n pi
        # - degenerate case - all points on line of longitude equidistant from point.
        # Return arbitrary value since the distance to the point does not depend on the
        # returned value.
        sin_lat = 0.0
    try:
        latitude = math.asin(sin_lat)
    except ValueError:
        # Rounding error has made sin_lat slightly > 1.
        latitude = math.copysign(HALF_PI, sin_lat)

    return latitude


def line_of_longitude_segment_nearer_end_latitude(edge_lat_min, edge_lat_max, edge_lon, pt_lat, pt_lon):
    """Given a segment of a line of longitude and a point, determines the end
    of the segment nearer to the point.
    :param edge_lat_min: lower latitude on line of longitude segment in radians
    :param edge_lat_max: upper latitude on line of longitude segment in radians
    :param edge_lon: longitude of segment in radians
    :param pt_lat: latitude of point in radians
    :param pt_lon: longitude of point in radians
    :return: latitude of nearer segment endpoint in radians
    """
    # Determine which side of a great circle perpendicular to the mid-point of
    # the edge that the point lies on.
    lat_mid = (edge_lat_min + edge_lat_max) / 2.0
    # One of Napier's rules for right angled spherical triangles:
    tan_lat_equi = math.tan(lat_mid) * math.cos(pt_lon - edge_lon)
    return edge_lat_min if math.tan(pt_lat) < tan_lat_equi else edge_lat_max


class RectangleBase(object):
    """Hyperrectangle class.

    Represents a Cartesian product of intervals.
    """
    def __init__(self, maxes, mins):
        """Construct a hyperrectangle."""
        self.maxes = np.maximum(maxes,mins).astype(np.float)
        self.mins = np.minimum(maxes,mins).astype(np.float)
        self.m, = self.maxes.shape

    def __repr__(self):
        return "<Rectangle %s>" % list(zip(self.mins, self.maxes))

    def volume(self):
        """Total volume."""
        return np.prod(self.maxes-self.mins)

    def split(self, d, split):
        """
        Produce two hyperrectangles by splitting.

        In general, if you need to compute maximum and minimum
        distances to the children, it can be done more efficiently
        by updating the maximum and minimum distances to the parent.

        :param d: int
            Axis to split hyperrectangle along.
        :param split:
            Input.

        """
        mid = np.copy(self.maxes)
        mid[d] = split
        less = self.__class__(self.mins, mid)
        mid = np.copy(self.mins)
        mid[d] = split
        greater = self.__class__(mid, self.maxes)
        return less, greater


class Rectangle(RectangleBase):
    """Rectangle using Euclidean metric.
    """
    def min_distance_point(self, x, p=2.):
        """
        Return the minimum distance between input and points in the hyperrectangle.

        :param x: array_like
            Input.
        :param p: float, optional
            Input.

        """
        # a = self.mins - x
        # b = x - self.maxes
        # c = np.maximum(a, b)
        # d = np.maximum(0, c)
        return minkowski_distance(0, np.maximum(0,np.maximum(self.mins-x,x-self.maxes)),p)

    def max_distance_point(self, x, p=2.):
        """
        Return the maximum distance between input and points in the hyperrectangle.

        :param x: array_like
            Input array.
        :param p: float, optional
            Input.

        """
        return minkowski_distance(0, np.maximum(self.maxes-x,x-self.mins),p)

    def min_distance_rectangle(self, other, p=2.):
        """
        Compute the minimum distance between points in the two hyperrectangles.

        :param other: hyperrectangle
            Input.
        :param p: float
            Input.

        """
        return minkowski_distance(0, np.maximum(0,np.maximum(self.mins-other.maxes,other.mins-self.maxes)),p)

    def max_distance_rectangle(self, other, p=2.):
        """
        Compute the maximum distance between points in the two hyperrectangles.

        :param other: hyperrectangle
            Input.
        :param p: float, optional
            Input.

        """
        return minkowski_distance(0, np.maximum(self.maxes-other.mins,other.maxes-self.mins),p)


class RectangleHaversine(RectangleBase):
    """Rectangular region in latitude/longitude coordinates on a sphere.
    """
    def min_distance_point(self, x, p=2.):
        """Find the distance to the point in the rectangle closest to x.
        :param x: point as array of latitude, longitude in degrees
        :param p: unused
        :return: distance in kilometres
        """
        return self._min_distance_point(np.radians(x))

    def max_distance_point(self, x, p=2.):
        """Find the distance to the point in the rectangle furthest from x.
        This is the semi-circumference minus the distance to the point closest
        to the polar opposite point.
        :param x: point as array of latitude, longitude in degrees
        :param p: unused
        :return: distance in kilometres
        """
        point = np.radians(x)
        opp_pt = [-point[0], point[1] + PI]
        opp_dist = self._min_distance_point(opp_pt)
        return PI * RADIUS_EARTH - opp_dist

    def _min_distance_point(self, point):
        """Find the distance to the point in the rectangle closest to x.
        :param point: point as array of latitude, longitude in radians
        :return: distance in kilometres
        """
        rect_lat_min, rect_lon_min = np.radians(self.mins)
        rect_lat_max, rect_lon_max = np.radians(self.maxes)

        lat0 = point[0]
        # Shift point longitude to be within pi of rectangle mid-longitude.
        range_start = (rect_lon_min + rect_lon_max) / 2.0 - PI
        lon0 = np.fmod(point[1] - range_start, TWO_PI) + range_start

        inside = False

        if rect_lon_min <= lon0 <= rect_lon_max:
            # Within longitude range of rectangle - geodesic is line of longitude.
            # Could simplify distance calculation.
            lon1 = lon0
            if lat0 < rect_lat_min:
                lat1 = rect_lat_min
            elif lat0 > rect_lat_max:
                lat1 = rect_lat_max
            else:
                inside = True
                # print("Inside")
        else:
            # Determine which side of the rectangle the point is nearer to allowing for longitude circularity.
            lon_mid = (rect_lon_min + rect_lon_max) / 2.0
            if ((lon0 < lon_mid and lon_mid - lon0 < PI)
                    or (lon0 > lon_mid and lon0 - lon_mid > PI)):
                # Point is nearest to left side of rectangle.
                lon1 = rect_lon_min
                lon_diff = rect_lon_min - lon0
                if lon_diff < 0.0:
                    lon_diff += TWO_PI
                if lon_diff > HALF_PI:
                    # Nearest point cannot be on rectangle edge - must be a vertex.
                    lat1 = line_of_longitude_segment_nearer_end_latitude(rect_lat_min, rect_lat_max, lon1, lat0, lon0)
                else:
                    # To left of rectangle
                    lat1 = geodesic_to_line_of_longitude_crossing_latitude(point, rect_lon_min)
                    lat1 = np.minimum(np.maximum(lat1, rect_lat_min), rect_lat_max)
            else:
                # Point is nearest to right side of rectangle.
                lon1 = rect_lon_max
                lon_diff = lon0 - rect_lon_max
                if lon_diff < 0.0:
                    lon_diff += TWO_PI
                if lon_diff > HALF_PI:
                    # Nearest point cannot be on rectangle edge - must be a vertex.
                    lat1 = line_of_longitude_segment_nearer_end_latitude(rect_lat_min, rect_lat_max, lon1, lat0, lon0)
                else:
                    lat1 = geodesic_to_line_of_longitude_crossing_latitude(point, rect_lon_max)
                    lat1 = np.minimum(np.maximum(lat1, rect_lat_min), rect_lat_max)

        if inside:
            dist = 0.0
        else:
            # print("Nearest point:", [np.degrees(lat1), np.degrees(lon1)])
            dist = haversine_distance_from_radians([lat0, lon0], [lat1, lon1])
        return dist

    def min_distance_point_approx(self, x, p=2.):
        """Return the minimum distance between input and points in the hyperrectangle.

        Approximate implementation determining the point to which to measure as if
        in Euclidean space.

        :param x: array_like
            Input.
        :param p: float, optional
            Input.

        """
        closest_point = np.minimum(np.maximum(x, self.mins), self.maxes)
        return haversine_distance(x, closest_point)

    def max_distance_point_approx(self, x, p=2.):
        """
        Return the maximum distance between input and points in the hyperrectangle.

        Approximate implementation determining the point to which to measure as if
        in Euclidean space.

        Parameters
        ----------
        :param x: array_like
            Input.
        :param p: float, optional
            Input.

        """
        furthest_point = np.where(self.maxes - x > x - self.mins, self.maxes, self.mins)
        return haversine_distance(x, furthest_point)


class KDTree(object):
    """
    kd-tree for quick nearest-neighbor lookup

    This class provides an index into a set of k-dimensional points which
    can be used to rapidly look up the nearest neighbors of any point.

    :param data: (N,K) array_like
        The data points to be indexed. This array is not copied, and
        so modifying this data will result in bogus results.
    :param leafsize: int, optional
        The number of points at which the algorithm switches over to
        brute-force.  Has to be positive.

    :raises:
     RuntimeError
        The maximum recursion limit can be exceeded for large data
        sets.  If this happens, either increase the value for the `leafsize`
        parameter or increase the recursion limit by::

            >>> import sys
            >>> sys.setrecursionlimit(10000)

    Notes

    The algorithm used is described in Maneewongvatana and Mount 1999.
    The general idea is that the kd-tree is a binary tree, each of whose
    nodes represents an axis-aligned hyperrectangle. Each node specifies
    an axis and splits the set of points based on whether their coordinate
    along that axis is greater than or less than a particular value.

    During construction, the axis and splitting point are chosen by the
    "sliding midpoint" rule, which ensures that the cells do not all
    become long and thin.

    The tree can be queried for the r closest neighbors of any given point
    (optionally returning only those within some maximum distance of the
    point). It can also be queried, with a substantial gain in efficiency,
    for the r approximate closest neighbors.

    For large dimensions (20 is already large) do not expect this to run
    significantly faster than brute force. High-dimensional nearest-neighbor
    queries are a substantial open problem in computer science.

    The tree also supports all-neighbors queries, both with arrays of points
    and with other kd-trees. These do use a reasonably efficient algorithm,
    but the kd-tree is not necessarily the best data structure for this
    sort of calculation.

    """
    def __init__(self, data, leafsize=10):
        self.data = np.asarray(data)
        self.n, self.m = np.shape(self.data)
        self.leafsize = int(leafsize)
        if self.leafsize<1:
            raise ValueError("leafsize must be at least 1")
        self.maxes = np.amax(self.data,axis=0)
        self.mins = np.amin(self.data,axis=0)

        self.tree = self._build(np.arange(self.n), self.maxes, self.mins)

    class node(object):
        if sys.version_info[0] >= 3:
            def __lt__(self, other): id(self) < id(other)
            def __gt__(self, other): id(self) > id(other)
            def __le__(self, other): id(self) <= id(other)
            def __ge__(self, other): id(self) >= id(other)
            def __eq__(self, other): id(self) == id(other)

    class leafnode(node):
        def __init__(self, idx):
            self.idx = idx
            self.children = len(idx)

    class innernode(node):
        def __init__(self, split_dim, split, less, greater):
            self.split_dim = split_dim
            self.split = split
            self.less = less
            self.greater = greater
            self.children = less.children+greater.children

    def _build(self, idx, maxes, mins):
        if len(idx)<=self.leafsize:
            return KDTree.leafnode(idx)
        else:
            data = self.data[idx]
            #maxes = np.amax(data,axis=0)
            #mins = np.amin(data,axis=0)
            d = np.argmax(maxes-mins)
            maxval = maxes[d]
            minval = mins[d]
            if maxval==minval:
                # all points are identical; warn user?
                return KDTree.leafnode(idx)
            data = data[:,d]

            # sliding midpoint rule; see Maneewongvatana and Mount 1999
            # for arguments that this is a good idea.
            split = (maxval+minval)/2
            less_idx = np.nonzero(data<=split)[0]
            greater_idx = np.nonzero(data>split)[0]
            if len(less_idx)==0:
                split = np.amin(data)
                less_idx = np.nonzero(data<=split)[0]
                greater_idx = np.nonzero(data>split)[0]
            if len(greater_idx)==0:
                split = np.amax(data)
                less_idx = np.nonzero(data<split)[0]
                greater_idx = np.nonzero(data>=split)[0]
            if len(less_idx)==0:
                # _still_ zero? all must have the same value
                if not np.all(data==data[0]):
                    raise ValueError("Troublesome data array: %s" % data)
                split = data[0]
                less_idx = np.arange(len(data)-1)
                greater_idx = np.array([len(data)-1])

            lessmaxes = np.copy(maxes)
            lessmaxes[d] = split
            greatermins = np.copy(mins)
            greatermins[d] = split
            return KDTree.innernode(d, split,
                    self._build(idx[less_idx],lessmaxes,mins),
                    self._build(idx[greater_idx],maxes,greatermins))

    def _query(self, x, k=1, eps=0, p=2, distance_upper_bound=np.inf):

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
            if isinstance(node, KDTree.leafnode):
                # brute-force
                data = self.data[node.idx]
                ds = minkowski_distance_p(data,x[np.newaxis,:],p)
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

    def query(self, x, k=1, eps=0, p=2, distance_upper_bound=np.inf):
        """
        Query the kd-tree for nearest neighbors

        :param x: array_like, last dimension self.m
            An array of points to query.
        :param k: integer
            The number of nearest neighbors to return.
        :param eps: nonnegative float
            Return approximate nearest neighbors; the kth returned value
            is guaranteed to be no further than (1+eps) times the
            distance to the real kth nearest neighbor.
        :param p: float, 1<=p<=infinity
            Which Minkowski p-norm to use.
            1 is the sum-of-absolute-values "Manhattan" distance
            2 is the usual Euclidean distance
            infinity is the maximum-coordinate-difference distance
        :param distance_upper_bound: nonnegative float
            Return only neighbors within this distance. This is used to prune
            tree searches, so if you are doing a series of nearest-neighbor
            queries, it may help to supply the distance to the nearest neighbor
            of the most recent point.

        :returns :
            d : array of floats
                The distances to the nearest neighbors.
                If x has shape tuple+(self.m,), then d has shape tuple if
                k is one, or tuple+(k,) if k is larger than one.  Missing
                neighbors are indicated with infinite distances.  If k is None,
                then d is an object array of shape tuple, containing lists
                of distances. In either case the hits are sorted by distance
                (nearest first).
            i : array of integers
                The locations of the neighbors in self.data. i is the same
                shape as d.

        Examples

        >>> from scipy import spatial
        >>> x, y = np.mgrid[0:5, 2:8]
        >>> tree = spatial.KDTree(zip(x.ravel(), y.ravel()))
        >>> tree.data
        array([[0, 2],
               [0, 3],
               [0, 4],
               [0, 5],
               [0, 6],
               [0, 7],
               [1, 2],
               [1, 3],
               [1, 4],
               [1, 5],
               [1, 6],
               [1, 7],
               [2, 2],
               [2, 3],
               [2, 4],
               [2, 5],
               [2, 6],
               [2, 7],
               [3, 2],
               [3, 3],
               [3, 4],
               [3, 5],
               [3, 6],
               [3, 7],
               [4, 2],
               [4, 3],
               [4, 4],
               [4, 5],
               [4, 6],
               [4, 7]])
        >>> pts = np.array([[0, 0], [2.1, 2.9]])
        >>> tree.query(pts)
        (array([ 2.        ,  0.14142136]), array([ 0, 13]))

        """
        x = np.asarray(x)
        if np.shape(x)[-1] != self.m:
            raise ValueError("x must consist of vectors of length %d but has shape %s" % (self.m, np.shape(x)))
        if p<1:
            raise ValueError("Only p-norms with 1<=p<=infinity permitted")
        retshape = np.shape(x)[:-1]
        if retshape!=():
            if k is None:
                dd = np.empty(retshape,dtype=np.object)
                ii = np.empty(retshape,dtype=np.object)
            elif k>1:
                dd = np.empty(retshape+(k,),dtype=np.float)
                dd.fill(np.inf)
                ii = np.empty(retshape+(k,),dtype=np.int)
                ii.fill(self.n)
            elif k==1:
                dd = np.empty(retshape,dtype=np.float)
                dd.fill(np.inf)
                ii = np.empty(retshape,dtype=np.int)
                ii.fill(self.n)
            else:
                raise ValueError("Requested %s nearest neighbors; acceptable numbers are integers greater than or equal to one, or None")
            for c in np.ndindex(retshape):
                hits = self._query(x[c], k=k, eps=eps, p=p, distance_upper_bound=distance_upper_bound)
                if k is None:
                    dd[c] = [d for (d,i) in hits]
                    ii[c] = [i for (d,i) in hits]
                elif k>1:
                    for j in range(len(hits)):
                        dd[c+(j,)], ii[c+(j,)] = hits[j]
                elif k==1:
                    if len(hits)>0:
                        dd[c], ii[c] = hits[0]
                    else:
                        dd[c] = np.inf
                        ii[c] = self.n
            return dd, ii
        else:
            hits = self._query(x, k=k, eps=eps, p=p, distance_upper_bound=distance_upper_bound)
            if k is None:
                return [d for (d,i) in hits], [i for (d,i) in hits]
            elif k==1:
                if len(hits)>0:
                    return hits[0]
                else:
                    return np.inf, self.n
            elif k>1:
                dd = np.empty(k,dtype=np.float)
                dd.fill(np.inf)
                ii = np.empty(k,dtype=np.int)
                ii.fill(self.n)
                for j in range(len(hits)):
                    dd[j], ii[j] = hits[j]
                return dd, ii
            else:
                raise ValueError("Requested %s nearest neighbors; acceptable numbers are integers greater than or equal to one, or None")


    def _query_ball_point(self, x, r, p=2., eps=0):
        R = Rectangle(self.maxes, self.mins)

        def traverse_checking(node, rect):
            if rect.min_distance_point(x, p) > r / (1. + eps):
                return []
            elif rect.max_distance_point(x, p) < r * (1. + eps):
                return traverse_no_checking(node)
            elif isinstance(node, KDTree.leafnode):
                d = self.data[node.idx]
                return node.idx[minkowski_distance(d, x, p) <= r].tolist()
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

    def query_ball_point(self, x, r, p=2., eps=0):
        """Find all points within distance r of point(s) x.

        :param x: array_like, shape tuple + (self.m,)
            The point or points to search for neighbors of.
        :param r: positive float
            The radius of points to return.
        :param p: float, optional
            Which Minkowski p-norm to use.  Should be in the range [1, inf].
        :param eps: nonnegative float, optional
            Approximate search. Branches of the tree are not explored if their
            nearest points are further than ``r / (1 + eps)``, and branches are
            added in bulk if their furthest points are nearer than
            ``r * (1 + eps)``.

        :returns: list or array of lists
            If `x` is a single point, returns a list of the indices of the
            neighbors of `x`. If `x` is an array of points, returns an object
            array of shape tuple containing lists of neighbors.

        **Notes**

        If you have many points whose neighbors you want to find, you may save
        substantial amounts of time by putting them in a KDTree and using
        query_ball_tree.

        **Examples**

        >>> from scipy import spatial
        >>> x, y = np.mgrid[0:4, 0:4]
        >>> points = zip(x.ravel(), y.ravel())
        >>> tree = spatial.KDTree(points)
        >>> tree.query_ball_point([2, 0], 1)
        [4, 8, 9, 12]

        """
        x = np.asarray(x)
        if x.shape[-1] != self.m:
            raise ValueError("Searching for a %d-dimensional point in a " \
                             "%d-dimensional KDTree" % (x.shape[-1], self.m))
        if len(x.shape) == 1:
            return self._query_ball_point(x, r, p, eps)
        else:
            retshape = x.shape[:-1]
            result = np.empty(retshape, dtype=np.object)
            for c in np.ndindex(retshape):
                result[c] = self._query_ball_point(x[c], r, p=p, eps=eps)
            return result

    def query_ball_tree(self, other, r, p=2., eps=0):
        """Find all pairs of points whose distance is at most r

        :param other: KDTree instance
            The tree containing points to search against.
        :param r: float
            The maximum distance, has to be positive.
        :param p: float, optional
            Which Minkowski norm to use.  `p` has to meet the condition
            ``1 <= p <= infinity``.
        :param eps: float, optional
            Approximate search.  Branches of the tree are not explored
            if their nearest points are further than ``r/(1+eps)``, and
            branches are added in bulk if their furthest points are nearer
            than ``r * (1+eps)``.  `eps` has to be non-negative.

        :returns:  list of lists
            For each element ``self.data[i]`` of this tree, ``results[i]`` is a
            list of the indices of its neighbors in ``other.data``.

        """
        results = [[] for i in range(self.n)]
        def traverse_checking(node1, rect1, node2, rect2):
            if rect1.min_distance_rectangle(rect2, p)>r/(1.+eps):
                return
            elif rect1.max_distance_rectangle(rect2, p)<r*(1.+eps):
                traverse_no_checking(node1, node2)
            elif isinstance(node1, KDTree.leafnode):
                if isinstance(node2, KDTree.leafnode):
                    d = other.data[node2.idx]
                    for i in node1.idx:
                        results[i] += node2.idx[minkowski_distance(d,self.data[i],p)<=r].tolist()
                else:
                    less, greater = rect2.split(node2.split_dim, node2.split)
                    traverse_checking(node1,rect1,node2.less,less)
                    traverse_checking(node1,rect1,node2.greater,greater)
            elif isinstance(node2, KDTree.leafnode):
                less, greater = rect1.split(node1.split_dim, node1.split)
                traverse_checking(node1.less,less,node2,rect2)
                traverse_checking(node1.greater,greater,node2,rect2)
            else:
                less1, greater1 = rect1.split(node1.split_dim, node1.split)
                less2, greater2 = rect2.split(node2.split_dim, node2.split)
                traverse_checking(node1.less,less1,node2.less,less2)
                traverse_checking(node1.less,less1,node2.greater,greater2)
                traverse_checking(node1.greater,greater1,node2.less,less2)
                traverse_checking(node1.greater,greater1,node2.greater,greater2)

        def traverse_no_checking(node1, node2):
            if isinstance(node1, KDTree.leafnode):
                if isinstance(node2, KDTree.leafnode):
                    for i in node1.idx:
                        results[i] += node2.idx.tolist()
                else:
                    traverse_no_checking(node1, node2.less)
                    traverse_no_checking(node1, node2.greater)
            else:
                traverse_no_checking(node1.less, node2)
                traverse_no_checking(node1.greater, node2)

        traverse_checking(self.tree, Rectangle(self.maxes, self.mins),
                          other.tree, Rectangle(other.maxes, other.mins))
        return results

    def query_pairs(self, r, p=2., eps=0):
        """
        Find all pairs of points within a distance.

        :param r: positive float
            The maximum distance.
        :param p: float, optional
            Which Minkowski norm to use.  `p` has to meet the condition
            ``1 <= p <= infinity``.
        :param eps: float, optional
            Approximate search.  Branches of the tree are not explored
            if their nearest points are further than ``r/(1+eps)``, and
            branches are added in bulk if their furthest points are nearer
            than ``r * (1+eps)``.  `eps` has to be non-negative.

        :returns: set
            Set of pairs ``(i,j)``, with ``i < j``, for which the corresponding
            positions are close.

        """
        results = set()
        def traverse_checking(node1, rect1, node2, rect2):
            if rect1.min_distance_rectangle(rect2, p)>r/(1.+eps):
                return
            elif rect1.max_distance_rectangle(rect2, p)<r*(1.+eps):
                traverse_no_checking(node1, node2)
            elif isinstance(node1, KDTree.leafnode):
                if isinstance(node2, KDTree.leafnode):
                    # Special care to avoid duplicate pairs
                    if id(node1) == id(node2):
                        d = self.data[node2.idx]
                        for i in node1.idx:
                            for j in node2.idx[minkowski_distance(d,self.data[i],p)<=r]:
                                if i<j:
                                    results.add((i,j))
                    else:
                        d = self.data[node2.idx]
                        for i in node1.idx:
                            for j in node2.idx[minkowski_distance(d,self.data[i],p)<=r]:
                                if i<j:
                                    results.add((i,j))
                                elif j<i:
                                    results.add((j,i))
                else:
                    less, greater = rect2.split(node2.split_dim, node2.split)
                    traverse_checking(node1,rect1,node2.less,less)
                    traverse_checking(node1,rect1,node2.greater,greater)
            elif isinstance(node2, KDTree.leafnode):
                less, greater = rect1.split(node1.split_dim, node1.split)
                traverse_checking(node1.less,less,node2,rect2)
                traverse_checking(node1.greater,greater,node2,rect2)
            else:
                less1, greater1 = rect1.split(node1.split_dim, node1.split)
                less2, greater2 = rect2.split(node2.split_dim, node2.split)
                traverse_checking(node1.less,less1,node2.less,less2)
                traverse_checking(node1.less,less1,node2.greater,greater2)

                # Avoid traversing (node1.less, node2.greater) and
                # (node1.greater, node2.less) (it's the same node pair twice
                # over, which is the source of the complication in the
                # original KDTree.query_pairs)
                if id(node1) != id(node2):
                    traverse_checking(node1.greater,greater1,node2.less,less2)

                traverse_checking(node1.greater,greater1,node2.greater,greater2)

        def traverse_no_checking(node1, node2):
            if isinstance(node1, KDTree.leafnode):
                if isinstance(node2, KDTree.leafnode):
                    # Special care to avoid duplicate pairs
                    if id(node1) == id(node2):
                        for i in node1.idx:
                            for j in node2.idx:
                                if i<j:
                                    results.add((i,j))
                    else:
                        for i in node1.idx:
                            for j in node2.idx:
                                if i<j:
                                    results.add((i,j))
                                elif j<i:
                                    results.add((j,i))
                else:
                    traverse_no_checking(node1, node2.less)
                    traverse_no_checking(node1, node2.greater)
            else:
                # Avoid traversing (node1.less, node2.greater) and
                # (node1.greater, node2.less) (it's the same node pair twice
                # over, which is the source of the complication in the
                # original KDTree.query_pairs)
                if id(node1) == id(node2):
                    traverse_no_checking(node1.less, node2.less)
                    traverse_no_checking(node1.less, node2.greater)
                    traverse_no_checking(node1.greater, node2.greater)
                else:
                    traverse_no_checking(node1.less, node2)
                    traverse_no_checking(node1.greater, node2)

        traverse_checking(self.tree, Rectangle(self.maxes, self.mins),
                          self.tree, Rectangle(self.maxes, self.mins))
        return results


    def count_neighbors(self, other, r, p=2.):
        """
        Count how many nearby pairs can be formed.

        Count the number of pairs (x1,x2) can be formed, with x1 drawn
        from self and x2 drawn from `other`, and where
        ``distance(x1, x2, p) <= r``.
        This is the "two-point correlation" described in Gray and Moore 2000,
        "N-body problems in statistical learning", and the code here is based
        on their algorithm.

        :param other: KDTree instance
            The other tree to draw points from.
        :param r: float or one-dimensional array of floats
            The radius to produce a count for. Multiple radii are searched with
            a single tree traversal.
        :param p: float, 1<=p<=infinity
            Which Minkowski p-norm to use

        :returns: int or 1-D array of ints
            The number of pairs. Note that this is internally stored in a numpy
            int, and so may overflow if very large (2e9).

        """
        def traverse(node1, rect1, node2, rect2, idx):
            min_r = rect1.min_distance_rectangle(rect2,p)
            max_r = rect1.max_distance_rectangle(rect2,p)
            c_greater = r[idx]>max_r
            result[idx[c_greater]] += node1.children*node2.children
            idx = idx[(min_r<=r[idx]) & (r[idx]<=max_r)]
            if len(idx)==0:
                return

            if isinstance(node1,KDTree.leafnode):
                if isinstance(node2,KDTree.leafnode):
                    ds = minkowski_distance(self.data[node1.idx][:,np.newaxis,:],
                                  other.data[node2.idx][np.newaxis,:,:],
                                  p).ravel()
                    ds.sort()
                    result[idx] += np.searchsorted(ds,r[idx],side='right')
                else:
                    less, greater = rect2.split(node2.split_dim, node2.split)
                    traverse(node1, rect1, node2.less, less, idx)
                    traverse(node1, rect1, node2.greater, greater, idx)
            else:
                if isinstance(node2,KDTree.leafnode):
                    less, greater = rect1.split(node1.split_dim, node1.split)
                    traverse(node1.less, less, node2, rect2, idx)
                    traverse(node1.greater, greater, node2, rect2, idx)
                else:
                    less1, greater1 = rect1.split(node1.split_dim, node1.split)
                    less2, greater2 = rect2.split(node2.split_dim, node2.split)
                    traverse(node1.less,less1,node2.less,less2,idx)
                    traverse(node1.less,less1,node2.greater,greater2,idx)
                    traverse(node1.greater,greater1,node2.less,less2,idx)
                    traverse(node1.greater,greater1,node2.greater,greater2,idx)

        R1 = Rectangle(self.maxes, self.mins)
        R2 = Rectangle(other.maxes, other.mins)
        if np.shape(r) == ():
            r = np.array([r])
            result = np.zeros(1,dtype=int)
            traverse(self.tree, R1, other.tree, R2, np.arange(1))
            return result[0]
        elif len(np.shape(r))==1:
            r = np.asarray(r)
            n, = r.shape
            result = np.zeros(n,dtype=int)
            traverse(self.tree, R1, other.tree, R2, np.arange(n))
            return result
        else:
            raise ValueError("r must be either a single value or a one-dimensional array of values")

    def sparse_distance_matrix(self, other, max_distance, p=2.):
        """
        Compute a sparse distance matrix

        Computes a distance matrix between two KDTrees, leaving as zero
        any distance greater than max_distance.

        :param other:  KDTree

        :param max_distance: positive float

        :param p: float, optional

        :returns: dok_matrix
            Sparse matrix representing the results in "dictionary of keys" format.

        """
        result = scipy.sparse.dok_matrix((self.n,other.n))

        def traverse(node1, rect1, node2, rect2):
            if rect1.min_distance_rectangle(rect2, p)>max_distance:
                return
            elif isinstance(node1, KDTree.leafnode):
                if isinstance(node2, KDTree.leafnode):
                    for i in node1.idx:
                        for j in node2.idx:
                            d = minkowski_distance(self.data[i],other.data[j],p)
                            if d<=max_distance:
                                result[i,j] = d
                else:
                    less, greater = rect2.split(node2.split_dim, node2.split)
                    traverse(node1,rect1,node2.less,less)
                    traverse(node1,rect1,node2.greater,greater)
            elif isinstance(node2, KDTree.leafnode):
                less, greater = rect1.split(node1.split_dim, node1.split)
                traverse(node1.less,less,node2,rect2)
                traverse(node1.greater,greater,node2,rect2)
            else:
                less1, greater1 = rect1.split(node1.split_dim, node1.split)
                less2, greater2 = rect2.split(node2.split_dim, node2.split)
                traverse(node1.less,less1,node2.less,less2)
                traverse(node1.less,less1,node2.greater,greater2)
                traverse(node1.greater,greater1,node2.less,less2)
                traverse(node1.greater,greater1,node2.greater,greater2)
        traverse(self.tree, Rectangle(self.maxes, self.mins),
                 other.tree, Rectangle(other.maxes, other.mins))

        return result


class HaversineDistanceKDTree(KDTree):
    """Modification of the scipy.spatial.KDTree class to allow querying for
    nearest neighbours measured by distance along the Earth's surface.
    """
    def __init__(self, data, leafsize=10, mask=None):
        self.data = np.ma.asarray(data)
        if mask is not None:
            self.data.mask = np.column_stack([mask] * data.shape[1])
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
        self.tree = self._build(indices, self.maxes, self.mins)

    def _query(self, x, k=1, eps=0, p=2, distance_upper_bound=np.inf):

        metric = np.array([1.0] * x.size)
        metric[1] = math.cos(x[1] * math.pi / 180.0)
        side_distances = np.maximum(0,np.maximum(x-self.maxes,self.mins-x)) * metric
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

    def _query_ball_point(self, x, r, p=2., eps=0):
        R = RectangleHaversine(self.maxes, self.mins)

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


def distance_matrix(x,y,p=2,threshold=1000000):
    """
    Compute the distance matrix.

    Returns the matrix of all pair-wise distances.

    :param x: (M, K) array_like
        TODO: description needed
    :param y: (N, K) array_like
        TODO: description needed
    :param p: float, 1 <= p <= infinity
        Which Minkowski p-norm to use.
    :param threshold: positive int
        If ``M * N * K`` > `threshold`, algorithm uses a Python loop instead
        of large temporary arrays.
    :returns: (M, N) ndarray
        Distance matrix.

    Examples

    >>> distance_matrix([[0,0],[0,1]], [[1,0],[1,1]])
    array([[ 1.        ,  1.41421356],
           [ 1.41421356,  1.        ]])

    """

    x = np.asarray(x)
    m, k = x.shape
    y = np.asarray(y)
    n, kk = y.shape

    if k != kk:
        raise ValueError("x contains %d-dimensional vectors but y contains %d-dimensional vectors" % (k, kk))

    if m*n*k <= threshold:
        return minkowski_distance(x[:,np.newaxis,:],y[np.newaxis,:,:],p)
    else:
        result = np.empty((m,n),dtype=np.float) #FIXME: figure out the best dtype
        if m<n:
            for i in range(m):
                result[i,:] = minkowski_distance(x[i],y,p)
        else:
            for j in range(n):
                result[:,j] = minkowski_distance(x,y[j],p)
        return result
