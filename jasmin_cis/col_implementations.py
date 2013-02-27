from data_io.hyperpoint import HyperPoint
from jasmin_cis.col_framework import Colocator, Constraint, Kernel
from timeUtil import time
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
        from jasmin_cis.data_io.ungridded_data import LazyData
        import numpy as np
        values = np.zeros(len(points))
        for i, point in enumerate(points):
            con_points = constraint.constrain_points(point, data)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                values[i] = constraint.fill_value
        new_data = LazyData(values, data.metadata)
        new_data.missing_value = constraint.fill_value
        return [new_data]


class DebugColocator(Colocator):

    def colocate(self, points, data, constraint, kernel):
        # This is the same colocate method as above with extra logging and timing steps. This is useful for debugging
        #  but will be slower than the default colocator.
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData
        import numpy as np
        import math

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data_points = data.get_points()

        short_points = points if len(points)<1000 else points[:999]
        values = np.zeros(len(short_points))
        times = np.zeros(len(short_points))
        for i, point in enumerate(short_points):
            t1 = time()
            con_points = constraint.constrain_points(point, data_points)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                values[i] = constraint.fill_value
            times[i] = time() - t1
            frac, rem = math.modf(i/10.0)
            if frac == 0: print str(i)+" took: "+str(times[i])
        logging.info("Average time per point: " + str(np.sum(times)/len(short_points)))
        new_data = LazyData(values, data.metadata)
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

    def constrain_points(self, ref_point, data):
        con_points = []
        for point in data:
            checks = [point.haversine_dist(ref_point) < self.h_sep,
                      point.time_sep < self.t_sep,
                      point.alt_sep < self.a_sep]
            if all(checks):
                con_points.append(point)
        return con_points


class nn_horizontal(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours along the face of the earth where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        nearest_point = data[0]
        for data_point in data[1:]:
            if point.compdist(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val


class nn_vertical(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in altitude, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        nearest_point = data[0]
        for data_point in data[1:]:
            if point.compalt(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val


class nn_time(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours without any constraints where both points and
              data are a list of HyperPoints
        '''
        nearest_point = HyperPoint(t=0.0)
        for data_point in data:
            if point.comptime(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val


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
