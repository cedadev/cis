from iris import Constraint


class SubsetConstraint(object):
    """Constraint for subsetting.

    Holds the limits for subsetting in each dimension.
    """

    def __init__(self):
        self._limits = {}

    def set_limit(self, dim_name, dim_min, dim_max):
        """Sets boundary values for a dimension to be used in subsetting.

        @param dim_name: dimension name
        @param dim_min: lower bound on dimension or None to indicate no lower bound
        @param dim_max: upper bound on dimension or None to indicate no upper bound
        """
        self._limits[dim_name] = (dim_min, dim_max)

    @staticmethod
    def _make_iris_constraint_function(dim_min, dim_max):
        """Constructs a function enforcing the specified bounds on the values of a dimension.

        The boundary values are included in the constrained interval.
        @param dim_min: lower bound on dimension or None to indicate no lower bound
        @param dim_max: upper bound on dimension or None to indicate no upper bound
        @return: lambda function with one argument returning bool
        """
        if dim_min is not None and dim_max is not None:
            return lambda x: dim_min <= x <= dim_max
        elif dim_min is not None and dim_max is None:
            return lambda x: dim_min <= x
        elif dim_min is None and dim_max is not None:
            return lambda x: x <= dim_max
        else:
            return None

    def make_iris_constraint(self):
        """Constructs an Iris constraint corresponding to the limits set for each dimension.

        @return: iris.Constraint object
        """
        constraint = None
        for dim_name in self._limits.iterkeys():
            limits = self._limits[dim_name]
            constraint_function = self._make_iris_constraint_function(limits[0], limits[1])
            if constraint_function is not None:
                if constraint is None:
                    constraint = Constraint(**{dim_name: constraint_function})
                else:
                    constraint = constraint & Constraint(**{dim_name: constraint_function})
        return constraint
