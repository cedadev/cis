# cython: boundscheck=False, wraparound=False, nonecheck=False
"""
Heavily modified, cython, version of the SciPy KD-tree implementation to calculate haversine distances.
"""
import scipy.sparse

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, sin, cos, asin, pi

__all__ = ['haversine_distance', 'HaversineDistanceKDTree']

cdef double RADIUS_EARTH = 6378.0
cdef double HALF_PI = pi / 2.0
cdef double PI = pi
cdef double TWO_PI = pi * 2.0
cdef double HALF_PI_DEGREES = pi / 180


cdef double haversine_distance(double x_lat, double x_lon, double y_lat, double y_lon):
    """Computes the Haversine distance in kilometres between two points
    :param x: first point as array of latitude, longitude in radians
    :param y: second point as array of latitude, longitude in radians
    :return: distance between the two points in kilometres
    """
    lat1 = x_lat * HALF_PI_DEGREES
    lat2 = y_lat * HALF_PI_DEGREES
    lon1 = x_lon * HALF_PI_DEGREES
    lon2 = y_lon * HALF_PI_DEGREES

    arclen = 2 * asin(sqrt((sin((lat2 - lat1) / 2)) ** 2 +
                                   cos(lat1) * cos(lat2) * (sin((lon2 - lon1) / 2)) ** 2))
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
        sin_lat = np.sin(pt_lat) / np.sqrt(1 - np.cos(pt_lat) ** 2 * np.sin(pt_lon - longitude) ** 2)
    except ZeroDivisionError:
        # pt_lat = +/- pi/2 and pt_lon - longitude = pi/2 + n pi
        # - degenerate case - all points on line of longitude equidistant from point.
        # Return arbitrary value since the distance to the point does not depend on the
        # returned value.
        sin_lat = 0.0
    try:
        latitude = np.asin(sin_lat)
    except ValueError:
        # Rounding error has made sin_lat slightly > 1.
        latitude = np.copysign(HALF_PI, sin_lat)

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
    tan_lat_equi = np.tan(lat_mid) * np.cos(pt_lon - edge_lon)
    return edge_lat_min if np.tan(pt_lat) < tan_lat_equi else edge_lat_max


cdef class RectangleBase(object):
    """Hyperrectangle class.

    Represents a Cartesian product of intervals.
    """

    cdef public np.ndarray maxes, mins
    cdef public int m

    def __init__(self, maxes, mins):
        """Construct a hyperrectangle."""
        self.maxes = np.maximum(maxes, mins).astype(np.float)
        self.mins = np.minimum(maxes, mins).astype(np.float)
        self.m, = np.shape(self.maxes)

    def __repr__(self):
        return "<Rectangle %s>" % list(zip(self.mins, self.maxes))

    def volume(self):
        """Total volume."""
        return np.prod(self.maxes - self.mins)

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


cdef class RectangleHaversine(RectangleBase):
    """Rectangular region in latitude/longitude coordinates on a sphere.
    """

    def min_distance_point(self, x):
        """Find the distance to the point in the rectangle closest to x.
        :param x: point as array of latitude, longitude in degrees
        :return: distance in kilometres
        """
        return self._min_distance_point(np.radians(x))

    def max_distance_point(self, x):
        """Find the distance to the point in the rectangle furthest from x.
        This is the semi-circumference minus the distance to the point closest
        to the polar opposite point.
        :param x: point as array of latitude, longitude in degrees
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
            if (lon0 < lon_mid and lon_mid - lon0 < PI) or (lon0 > lon_mid and lon0 - lon_mid > PI):
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
            dist = haversine_distance(lat0, lon0, lat1, lon1)
        return dist

    def min_distance_point_approx(self, x):
        """Return the minimum distance between input and points in the hyperrectangle.

        Approximate implementation determining the point to which to measure as if
        in Euclidean space.

        :param x: array_like
            Input.
        :param p: float, optional
            Input.

        """
        closest_point = np.minimum(np.maximum(x, self.mins), self.maxes)
        return haversine_distance(x[0], x[1], closest_point[0], closest_point[1])

    def max_distance_point_approx(self, x):
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
        return haversine_distance(x[0], x[1], furthest_point[0], furthest_point[1])

    def min_distance_rectangle(self, other):
        """
        Compute the minimum distance between points in the two hyperrectangles.

        :param other: hyperrectangle
            Input.
        :param p: float
            Input.

        """
        nearest_corner = np.maximum(0, np.maximum(self.mins - other.maxes, other.mins - self.maxes))
        return haversine_distance(0.0, 0.0, nearest_corner[0], nearest_corner[1])

    def max_distance_rectangle(self, other):
        """
        Compute the maximum distance between points in the two hyperrectangles.

        :param other: hyperrectangle
            Input.
        :param p: float, optional
            Input.

        """
        furthest_corner = np.maximum(self.maxes - other.mins, other.maxes - self.mins)
        return haversine_distance(0.0, 0.0, furthest_corner[0], furthest_corner[1])


cdef class node(object):

    def __richcmp__(self, other, int_op):
        if int_op == 0:
            return id(self) < id(other)
        elif int_op == 1:
            return id(self) <= id(other)
        elif int_op == 2:
            return id(self) == id(other)
        elif int_op == 3:
            return id(self) != id(other)
        elif int_op == 4:
            return id(self) > id(other)
        elif int_op == 5:
            return id(self) >= id(other)


cdef class leafnode(node):

    cdef public np.int_t[:] idx
    cdef public int children

    def __init__(self, idx):
        self.idx = idx
        self.children = len(idx)

cdef class innernode(node):

    cdef public int split_dim, children
    cdef public double split
    cdef public node less, greater

    def __init__(self, split_dim, split, less, greater):
        self.split_dim = split_dim
        self.split = split
        self.less = less
        self.greater = greater
        self.children = less.children + greater.children


cdef void traverse(object result,
                   node node1, RectangleHaversine rect1,
                   node node2, RectangleHaversine rect2,
                   float max_distance, np.float_t[:, :] self_data, np.float_t[:, :] other_data):

    cdef int i, j
    cdef float d

    if rect1.min_distance_rectangle(rect2) > max_distance:
        return
    elif isinstance(node1, leafnode):
        if isinstance(node2, leafnode):
            for i in node1.idx:
                for j in node2.idx:
                    d = haversine_distance(self_data[i, 0], self_data[i, 1], other_data[j, 0], other_data[j, 1])
                    if d <= max_distance:
                        # Set the dict values directly to bypass the scipy type checking
                        dict.__setitem__(result, (i, j), d)
        else:
            less, greater = rect2.split(node2.split_dim, node2.split)
            traverse(result, node1, rect1, node2.less, less, max_distance, self_data, other_data)
            traverse(result, node1, rect1, node2.greater, greater, max_distance, self_data, other_data)
    elif isinstance(node2, leafnode):
        less, greater = rect1.split(node1.split_dim, node1.split)
        traverse(result, node1.less, less, node2, rect2, max_distance, self_data, other_data)
        traverse(result, node1.greater, greater, node2, rect2, max_distance, self_data, other_data)
    else:
        less1, greater1 = rect1.split(node1.split_dim, node1.split)
        less2, greater2 = rect2.split(node2.split_dim, node2.split)
        traverse(result, node1.less, less1, node2.less, less2, max_distance, self_data, other_data)
        traverse(result, node1.less, less1, node2.greater, greater2, max_distance, self_data, other_data)
        traverse(result, node1.greater, greater1, node2.less, less2, max_distance, self_data, other_data)
        traverse(result, node1.greater, greater1, node2.greater, greater2, max_distance, self_data, other_data)


def _build(np.int_t[:] idx, np.float_t[:] maxes, np.float_t[:] mins, np.int_t leafsize, np.float_t[:, :] data):

    cdef np.int_t[:] less_idx_vals, greater_idx_vals
    cdef np.float_t[:, :] local_data
    cdef np.float_t[:] local_single_dim_points
    cdef float split
    cdef int n_points, d, i

    n_points = len(idx)
    local_data = np.empty((n_points, 2), dtype=np.float)

    less_idx, greater_idx = [], []

    if len(idx) <= leafsize:
        return leafnode(idx)
    else:
        for i in range(n_points):
            local_data[i] = data[idx[i]]

        d = -1
        local_max = -np.inf
        for d_i in range(2):
            diff = maxes[d_i] - mins[d_i]
            if diff > local_max:
                local_max = diff
                d = d_i
        # Replaced by the loop above
        # In which dimension is the biggest difference?
        # d = np.argmax(maxes-mins)
        # TODO: I'm not sure this is valid for Haversine distance trees - what about lon wraparound??
        # What is that difference
        maxval = maxes[d]
        minval = mins[d]
        if maxval == minval:
            # all points are identical; warn user?
            return leafnode(idx)
        # Choose all the points in that dimension
        local_single_dim_points = local_data[:, d]

        # sliding midpoint rule; see Maneewongvatana and Mount 1999
        # for arguments that this is a good idea.
        # TODO: This won't work for longitudes either
        split = (maxval+minval)/2
        for i in range(n_points):
            if local_single_dim_points[i] <= split:
                less_idx.append(i)
            else:
                greater_idx.append(i)

        if len(less_idx) == 0:
            less_idx, greater_idx = [], []
            split = np.amin(local_single_dim_points)

            for i in range(n_points):
                if local_single_dim_points[i] <= split:
                    less_idx.append(i)
                else:
                    greater_idx.append(i)

        if len(greater_idx) == 0:
            less_idx, greater_idx = [], []

            split = np.amax(local_single_dim_points)
            for i in range(n_points):
                if local_single_dim_points[i] < split:
                    less_idx.append(i)
                else:
                    greater_idx.append(i)

        if len(less_idx) == 0:
            # _still_ zero? all must have the same value
            split = local_single_dim_points[0]
            less_idx = np.arange(len(local_single_dim_points)-1)
            greater_idx = np.array([len(local_single_dim_points)-1])

        lessmaxes = np.copy(maxes)
        lessmaxes[d] = split
        greatermins = np.copy(mins)
        greatermins[d] = split

        less_idx_vals = np.empty((len(less_idx), ), dtype=np.int)
        greater_idx_vals = np.empty((len(greater_idx), ), dtype=np.int)

        for i in range(len(less_idx)):
            less_idx_vals[i] = idx[less_idx[i]]

        for i in range(len(greater_idx)):
            greater_idx_vals[i] = idx[greater_idx[i]]

        return innernode(d, split,
                _build(less_idx_vals,lessmaxes,mins,leafsize,data),
                _build(greater_idx_vals,maxes,greatermins,leafsize,data))


cdef class HaversineDistanceKDTree(object):
    """Modification of the scipy.spatial.KDTree class to allow querying for
    nearest neighbours measured by distance along the Earth's surface.
    """
    cdef public np.float_t[:] maxes, mins
    cdef public np.float_t[:, :] data
    cdef public np.int_t m, n, leafsize
    cdef public node tree

    def __init__(self, data, mask, int leafsize=10):

        self.data = data
        self.n, self.m = np.shape(self.data)
        self.leafsize = leafsize
        if self.leafsize < 1:
            raise ValueError("leafsize must be at least 1")
        self.maxes = np.amax(self.data, axis=0)
        self.mins = np.amin(self.data, axis=0)

        indices = np.arange(self.n)
        indices = np.ma.array(indices, mask=mask)
        indices = indices.compressed()
        self.tree = _build(indices, self.maxes, self.mins, leafsize, data)

    def sparse_distance_matrix(self, other, max_distance):
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
        result = scipy.sparse.dok_matrix((self.n, other.n))

        traverse(result,
                 self.tree, RectangleHaversine(self.maxes, self.mins),
                 other.tree, RectangleHaversine(other.maxes, other.mins),
                 max_distance, self.data, other.data)

        return result

