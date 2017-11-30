"""
    Top level collocation objects
"""
import logging
import six
from functools import wraps


def collocate(data, sample, collocator, constraint, kernel):
    """
    Perform the collocation.

    :param CommonData or CommonDataList data: Data to collocate
    :param CommonData sample: Sampling to collocate onto
    :param cis.collocation.col_framework.Collocator collocator: The collocator object to use
    :param cis.collocation.col_framework.Constraint constraint: The constraint object
    :param cis.collocation.col_framework.Kernel  kernel: The kernel to use
    :return CommonData: The collocated data
    :raises CoordinateNotFoundError: If the collocator was unable to compare the sample and data points
    """
    from cis.exceptions import CoordinateNotFoundError
    from time import time
    from cis import __version__

    logging.info("Collocator: " + str(collocator))
    logging.info("Kernel: " + str(kernel))

    logging.info("Collocating, this could take a while...")
    t1 = time()
    try:
        new_data = collocator.collocate(sample, data, constraint, kernel)
    except (TypeError, AttributeError) as e:
        raise CoordinateNotFoundError('Collocator was unable to compare data points, check the dimensions of each '
                                      'data set and the collocation methods chosen. \n' + str(e))

    logging.info("Completed. Total time taken: " + str(time() - t1))

    for d in new_data:
        history = "Collocated onto sampling from: " + str(getattr(sample, "filenames", "Unknown")) + " " + \
                  "\nusing CIS version " + __version__ + " " + \
                  "\nvariables: " + str(getattr(data, "var_name", "Unknown")) + " " + \
                  "\nwith files: " + str(getattr(data, "filenames", "Unknown")) + " " + \
                  "\nusing collocator: " + str(collocator) + " " + \
                  "\nkernel: " + str(kernel)
        d.add_history(history)
    return new_data


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

    @wraps
    def cube_func(a, b, *args, **kwargs):
        # TODO UNIFY OTHER COORDS AND LONGITUDES HERE
        unify_time_units([a, b])
        ds_a = from_iris(a)
        ds_b = from_iris(b)
        ds = xr_func(ds_a, ds_b, *args, **kwargs)
        return to_iris(ds)
    return cube_func

