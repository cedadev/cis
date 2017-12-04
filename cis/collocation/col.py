"""
    Top level collocation objects
"""
import logging
from cis.collocation.col_implementations import moments
import six


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


def get_kernel(kernel, default=moments):
    """
     Return a valid kernel instance from either an instance or a string, default is moments if no kernel is specified

    :param str or cis.collocation.col_framework.Kernel kernel:
    :param default:
    :return cis.collocation.col_framework.Kernel:
    """
    from cis.collocation.col_framework import get_kernel, Kernel
    if not kernel:
        kernel = default()
    elif isinstance(kernel, six.string_types):
        kernel = get_kernel(kernel)()
    elif not isinstance(kernel, Kernel):
        raise ValueError("Invalid kernel argument, it must be either a string or a Kernel instance")
    return kernel
