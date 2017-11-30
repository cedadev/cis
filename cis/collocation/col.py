"""
    Top level collocation objects
"""
import six
from functools import wraps


def get_kernel(kernel):
    """
     Return a valid kernel instance from either an instance or a string, default is moments if no kernel is specified

    :param str or cis.collocation.col_framework.Kernel kernel:
    :param default:
    :return cis.collocation.col_framework.Kernel:
    """
    from cis.collocation.col_framework import get_kernel, Kernel
    from cis.collocation.col_implementations import moments
    if not kernel:
        kernel = moments()
    elif isinstance(kernel, six.string_types):
        kernel = get_kernel(kernel)()
    elif not isinstance(kernel, Kernel):
        raise ValueError("Invalid kernel argument, it must be either a string or a Kernel instance")
    return kernel


def cube_unify_col_wrapper(xr_func):
    """
    Wrap a function which works on two xarray Datasets with an Cube->Dataset converter to allow calling with an
     two Cube objects. Takes advantage of the cube metadata to perform unification on the two cubes before converting.

    :param func: A (collocation) function which takes two Datasets as its first arguments and returns a Dataset
    :return: A function which takes two Cube objects as its first arguments and returns a Cube object
    """
    from cis.data_io.convert import from_iris, to_iris
    from iris.util import unify_time_units
    from cis import __version__

    @wraps
    def cube_func(a, b, *args, **kwargs):

        # Unify the coordinate units
        for a_c in a.coords():
            for b_c in b.coords(standard_name=a_c.standard_name):
                a_c.convert_units(b_c.units)
        # Fix the longitude ranges
        if a.coords(standard_name='longitude'):
            lon_min = a.coord(standard_name='longitude').points.min()
            # First fix the sample points so that they all fall within the same 360 degree longitude range
            _fix_longitude_range(a, lon_min)
            # Then fix the data points so that they fall onto the same 360 degree longitude range as the sample points
            _fix_longitude_range(b, lon_min)

        unify_time_units([a, b])
        # Convert to xarray
        ds_a = from_iris(a)
        ds_b = from_iris(b)
        # Collocate
        ds = xr_func(ds_a, ds_b, *args, **kwargs)
        # Convert back and return
        res = to_iris(ds)

        history = "Collocated {} onto sampling from {}".format(a.name(), b.name()) + " " + \
                  "\nusing CIS version " + __version__ + " " + \
                  "\nwith collocator: " + str(xr_func)
        res.add_history(history)

        return res

    return cube_func


def _fix_longitude_range(data_points, range_start):
    """Sets the longitude range of the data points to match that of the sample coordinates.
    :param range_start: The longitude
    :param data_points: HyperPointList or GriddedData of data to fix
    """
    from cis.data_io.cube_utils import set_longitude_range
    from iris.analysis.cartography import wrap_lons

    if data_points.coords('longitude', dim_coords=True) and (len(data_points.shape) > 1):
        # For multidimensional cubes we need to rotate the whole object to keep the points monotonic
        set_longitude_range(data_points, range_start)
    else:
        # But we can just wrap auxilliary longitude coordinates
        data_points.coord('longitude').points = wrap_lons(data_points.coord('longitude').points, range_start, 360)
