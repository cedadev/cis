from jasmin_cis.col_framework import Colocator, Constraint, Kernel
import logging


class DefaultColocator(Colocator):
    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator takes a list of HyperPoints and a data object (currently either Ungridded data or a Cube) and returns
             one new LazyData object with the values as determined by the constraint and kernel objects. The metadata
             for the output LazyData object is copied from the input data object.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube, or any other object containing metadata that the constraint object can read
        @param constraint: An instance of a Constraint subclass which takes a data object and returns a subset of that data
                            based on it's internal parameters
        @param kernel: An instance of a Kernel subclass which takes a numberof points and returns a single value
        @return: A single LazyData object
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData
        import numpy as np

        metadata = data.metadata

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data = data.get_points()

        # Fill will the FillValue from the start
        values = np.zeros(len(points)) + constraint.fill_value

        for i, point in enumerate(points):
            con_points = constraint.constrain_points(point, data)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                pass
        new_data = LazyData(values, metadata)
        new_data.metadata.shape = (len(points),)
        new_data.metadata.missing_value = constraint.fill_value
        return [new_data]


class DebugColocator(Colocator):

    def __init__(self, max_vals=1000, print_step=10.0):
        super(DebugColocator, self).__init__()
        self.max_vals = int(max_vals)
        self.print_step = float(print_step)

    def colocate(self, points, data, constraint, kernel):
        # This is the same colocate method as above with extra logging and timing steps. This is useful for debugging
        #  but will be slower than the default colocator.
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData
        import numpy as np
        import math
        from time import time

        metadata = data.metadata

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data = data.get_points()

        # Only colocate a certain number of points, as a quick test
        short_points = points if len(points)<self.max_vals else points[:self.max_vals-1]

        # We still need to output the full size list, to match the size of the coordinates
        values = np.zeros(len(points)) + constraint.fill_value

        times = np.zeros(len(short_points))
        for i, point in enumerate(short_points):
            t1 = time()
            con_points = constraint.constrain_points(point, data)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                pass
            times[i] = time() - t1
            frac, rem = math.modf(i/self.print_step)
            if frac == 0: print str(i)+" took: "+str(times[i])
        logging.info("Average time per point: " + str(np.sum(times)/len(short_points)))
        new_data = LazyData(values, metadata)
        new_data.missing_value = constraint.fill_value
        return [new_data]


class DummyColocator(Colocator):

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator does no colocation at all - it just returns the original data values. This might be useful
            if the input data for one variable is already known to be on the same grid as points. This routine could
            check the coordinates are the same but currently does no such check.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube
        @param constraint: Unused
        @param kernel: Unused
        @return: A single LazyData object
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData
        new_data = LazyData(data.data, data.metadata)
        return [new_data]


class DummyConstraint(Constraint):

    def constrain_points(self, point, data):
        # This is a null constraint - all of the points just get passed back
        return data


class SepConstraint(Constraint):

    def __init__(self, h_sep=None, a_sep=None, t_sep=None, fill_value=None):
        super(SepConstraint, self).__init__()
        if fill_value is not None:
            self.fill_value = fill_value
        self.checks = []
        if h_sep is not None:
            self.h_sep = h_sep
            self.checks.append(self.horizontal_constraint)
        if a_sep is not None:
            self.a_sep = a_sep
            self.checks.append(self.alt_constraint)
        if t_sep is not None:
            from jasmin_cis.time_util import parse_datetimestr_delta_to_float_days
            self.t_sep = parse_datetimestr_delta_to_float_days(t_sep)
            self.checks.append(self.time_constraint)

    def time_constraint(self, point, ref_point):
        return point.time_sep(ref_point) < self.t_sep

    def alt_constraint(self, point, ref_point):
        return point.alt_sep(ref_point) < self.a_sep

    def horizontal_constraint(self, point, ref_point):
        return point.haversine_dist(ref_point) < self.h_sep

    def constrain_points(self, ref_point, data):
        from jasmin_cis.data_io.hyperpoint import HyperPointList
        con_points = HyperPointList()
        for point in data:
            if all(check(point, ref_point) for check in self.checks):
                con_points.append(point)
        return con_points


class mean(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using the mean of any points left after a constraint.
        '''
        from numpy import mean
        values = data.vals
        if len(values) == 0: raise ValueError
        return mean(data.vals)


class nn_horizontal(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours along the face of the earth where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        nearest_point = data[0]
        for data_point in data[1:]:
            if point.compdist(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_vertical(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in altitude, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        nearest_point = data[0]
        for data_point in data[1:]:
            if point.compalt(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_time(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in time, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        nearest_point = data[0]
        for data_point in data[1:]:
            if point.comptime(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_gridded(Kernel):
    def get_value(self, point, data):
        '''
            Co-location routine using nearest neighbour algorithm optimized for gridded data.
             This calls out to iris to do the work.
        '''
        from iris.analysis.interpolate import nearest_neighbour_data_value
        return nearest_neighbour_data_value(data, point.get_coord_tuple())


class li(Kernel):
    def get_value(self, point, data):
        '''
            Co-location routine using iris' linear interpolation algorithm. This only makes sense for gridded data.
        '''
        from iris.analysis.interpolate import linear
        return linear(data, point.get_coord_tuple()).data
