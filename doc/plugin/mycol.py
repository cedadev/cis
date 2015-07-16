from cis.col_framework import Colocator, Constraint, Kernel
from cis.data_io.ungridded_data import LazyData


class MyColocator(Colocator):

    def colocate(self, points, data, constraint, kernel):
        values = []
        for point in points:
            con_points = constraint.constrain_points(point, data)
            try:
                values.append(kernel.get_value(point, con_points))
            except ValueError:
                values.append(constraint.fill_value)
        new_data = LazyData(values, data.metadata)
        new_data.missing_value = constraint.fill_value
        return new_data


class MyConstraint(Constraint):

    def constrain_points(self, ref_point, data):
        con_points = []
        for point in data:
            if point.value > self.val_check:
                con_points.append(point)
        return con_points


class MyKernel(Kernel):

    def get_value(self, point, data):
        nearest_point = point.furthest_point_from()
        for data_point in data:
            if point.compdist(nearest_point, data_point):
                nearest_point = data_point
        return nearest_point.val
