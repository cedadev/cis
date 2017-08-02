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


def _ungridded_sampled_from(sample, data, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                            var_name='', var_long_name='', var_units='', **kwargs):
    """
    Collocate the CommonData object with another CommonData object using the specified collocator and kernel

    :param CommonData or CommonDataList data: The data to resample
    :param str how: Collocation method (e.g. lin, nn, bin or box)
    :param str or cis.collocation.col_framework.Kernel kernel:
    :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
    :param float fill_value: Value to use for missing data
    :param str var_name: The output variable name
    :param str var_long_name: The output variable's long name
    :param str var_units: The output variable's units
    :return CommonData: The collocated dataset
    """
    from cis.collocation import col_implementations as ci
    from cis.collocation.col import collocate, get_kernel

    if isinstance(data, UngriddedData) or isinstance(data, UngriddedDataList):
        col = ci.GeneralUngriddedCollocator(fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                            var_units=var_units,
                                            missing_data_for_missing_sample=missing_data_for_missing_sample)

        # Box is the default, and only option for ungridded -> ungridded collocation
        if how not in ['', 'box']:
            raise ValueError("Invalid method specified for ungridded -> ungridded collocation: " + how)
        con = ci.SepConstraintKdtree(**kwargs)
        # We can have any kernel, default to moments
        kernel = get_kernel(kernel)
    elif isinstance(data, GriddedData) or isinstance(data, GriddedDataList):
        col = ci.GriddedUngriddedCollocator(fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                            var_units=var_units,
                                            missing_data_for_missing_sample=missing_data_for_missing_sample)
        con = None
        kernel = 'lin'
    else:
        raise ValueError("Invalid argument, data must be either GriddedData or UngriddedData")

    return collocate(data, sample, col, con, kernel)


def _gridded_sampled_from(self, data, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                 var_name='', var_long_name='', var_units='', **kwargs):
    """
    Collocate the CommonData object with another CommonData object using the specified collocator and kernel

    :param CommonData or CommonDataList data: The data to resample
    :param str how: Collocation method (e.g. lin, nn, bin or box)
    :param str or cis.collocation.col_framework.Kernel kernel:
    :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
    :param float fill_value: Value to use for missing data
    :param str var_name: The output variable name
    :param str var_long_name: The output variable's long name
    :param str var_units: The output variable's units
    :return CommonData: The collocated dataset
    """
    from cis.collocation import col_implementations as ci

    if isinstance(data, UngriddedData) or isinstance(data, UngriddedDataList):
        col_cls = ci.GeneralGriddedCollocator
        # Bin is the default for ungridded -> gridded collocation
        if how == '' or how == 'bin':
            con = ci.BinnedCubeCellOnlyConstraint()
        elif how == 'box':
            con = ci.SepConstraintKdtree(**kwargs)
        else:
            raise ValueError("Invalid method specified for ungridded -> gridded collocation: " + how)

        # We can have any kernel, default to moments
        kernel = get_kernel(kernel)
    elif isinstance(data, GriddedData) or isinstance(data, DataList):
        col_cls = ci.GriddedCollocator
        con = None
        if kernel is not None:
            raise ValueError("Cannot specify kernel when method is 'lin' or 'nn'")

        # Lin is the default for gridded -> gridded
        if how == '' or how == 'lin':
            kernel = ci.gridded_gridded_li()
        elif how == 'nn':
            kernel = ci.gridded_gridded_nn()
        else:
            raise ValueError("Invalid method specified for gridded -> gridded collocation: " + how)
    else:
        raise ValueError("Invalid argument, data must be either GriddedData or UngriddedData")

    col = col_cls(missing_data_for_missing_sample=missing_data_for_missing_sample, fill_value=fill_value,
                  var_name=var_name, var_long_name=var_long_name, var_units=var_units)

    return collocate(data, self, col, con, kernel)
