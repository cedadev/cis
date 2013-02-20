from col_framework import Colocator, Constraint, Kernel
from time import time
import logging

class DefaultColocator(Colocator):

    def colocate(self, points, data, constraint, kernel):
        from data_io.ungridded_data import LazyData
        import numpy as np
        values = np.zeros(len(points))
        times = np.zeros(len(points))
        for i, point in enumerate(points):
            t1 = time()
            con_points = constraint.constraint(point, data)
            try:
                values[i] = kernel.kernel(point, con_points)
            except ValueError:
                values[i] = constraint.fill_value
            times[i] = time() - t1
        logging.info("Average time per point: " + str(np.sum(times)/len(self.points)))
        new_data = LazyData(values, data.metadata)
        new_data.missing_value = constraint.fill_value
        return new_data

class DefaultConstraint(Constraint):

    def constraint(self, point, data):
        # This is a null constraint - all of the points just get passed back
        return data

class find_nn_value(Kernel):

    def kernel(self, point, data):
        '''
            Colocation using nearest neighbours without any constraints where both points and
              data are a list of HyperPoints
        '''
        nearest_point = point.furthest_point_from()
        for data_point in self.data:
            if point.compdist(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val

class find_nn_value_ungridded(Kernel):

    def kernel(self, point, data):
        '''
            Co-location routine using nearest neighbour algorithm optimized for ungridded data
        '''
        import numpy as np
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        nearest_point = point.furthest_point_from()
        for (x,y), value in np.ndenumerate(data.data):
            ug_point = HyperPoint(data.lat[x,y],data.lon[x,y],val=value)
            if point.compdist(nearest_point, ug_point): nearest_point = ug_point

        return nearest_point.val

class find_nn_value_gridded(Kernel):
    def kernel(self, point, data):
        '''
            Co-location routine using nearest neighbour algorithm optimized for gridded data.
             This calls out to iris to do the work.
        '''
        from iris.analysis.interpolate import nearest_neighbour_data_value
        return nearest_neighbour_data_value(data, point.get_coord_tuple())

class find_value_by_li(Kernel):
    def kernel(self, point, data):
        '''
            Co-location routine using iris' linear interpolation algorithm. This only makes sense for gridded data.
        '''
        from iris.analysis.interpolate import linear
        return linear(data, point.get_coord_tuple()).data
