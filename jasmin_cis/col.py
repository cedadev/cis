"""
    Top level colocation objects
"""
import logging

import jasmin_cis.col_implementations as ci
from jasmin_cis.col_framework import get_kernel
from jasmin_cis.exceptions import InvalidCommandLineOptionError


class _GenericKernel(object):
    """
    Marker class used by _get_colocator_classes_for_method to indicate that one of the generic kernels is needed.
    """
    pass


class ColocatorFactory(object):
    """
    Class for creating Colocator, Constraint and Kernel instances
    """

    def get_colocator_instances_for_method(self, method_name, kernel_name, colocator_params, kernel_params,
                                           sample_gridded, data_gridded):
        """
        Get instances of the correct classes for colocation
        :param method_name: Colocation method name (e.g. 'lin', 'nn')
        :param kernel_name: Kernel class name
        :param colocator_params: Colocation parameters
        :param kernel_params: Kernel parameters
        :param sample_gridded: Is the sample data gridded?
        :param data_gridded: Is the colocation data gridded?
        :return: Colocator, Constrain and Kernel instances
        """
        col_cls, constraint_cls, kernel_cls = self._get_colocator_classes_for_method(method_name, kernel_name,
                                                                                     sample_gridded, data_gridded)
        colocator_params, constraint_params = self._get_colocator_params(colocator_params)
        col = self._instantiate_with_params(col_cls, colocator_params)
        del constraint_params['missing_data_for_missing_sample']
        con = self._instantiate_with_params(constraint_cls, constraint_params)
        kernel = self._instantiate_with_params(kernel_cls, kernel_params)
        return col, con, kernel

    def _get_colocator_classes_for_method(self, method_name, kernel_name, sample_gridded, data_gridded):
        """
        Gets the colocator, constraint and kernel classes corresponding to a specified colocation method and kernel
        name.
        :param method_name: colocation method name
        :param kernel_name: kernel name
        :param sample_gridded: True if sample points are gridded, otherwise False
        :param data_gridded: True if data points are gridded, otherwise False
        :return: ColocationOptions containing relevant classes
        """
        if method_name is None:
            raise InvalidCommandLineOptionError("A colocator must be specified")

        key = method_name + ('_True' if sample_gridded else '_False') + ('_True' if data_gridded else '_False')

        # Method Sample  Data    colocator                      constraint                    kernel
        #   name   gridded gridded
        options = {
            'lin_False_False': None,
            'lin_True_False': None,
            'lin_False_True': [ci.GeneralUngriddedColocator, None, ci.li],
            'lin_True_True': [ci.GriddedColocator, None, ci.gridded_gridded_li],
            'nn_False_False': None,
            'nn_True_False': None,
            'nn_False_True': [ci.GeneralUngriddedColocator, None, ci.nn_gridded],
            'nn_True_True': [ci.GriddedColocator, None, ci.gridded_gridded_nn],
            'bin_False_False': None,
            'bin_True_False': [ci.GeneralGriddedColocator, ci.BinnedCubeCellOnlyConstraint, _GenericKernel],
            'bin_False_True': None,
            'bin_True_True': [ci.GeneralGriddedColocator, ci.BinningCubeCellConstraint, _GenericKernel],
            'box_False_False': [ci.GeneralUngriddedColocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_True_False': [ci.GeneralGriddedColocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_False_True': [ci.GeneralUngriddedColocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_True_True': [ci.GeneralGriddedColocator, ci.SepConstraintKdtree, _GenericKernel],
            'dummy_False_False': [ci.DummyColocator, None, None],
            'dummy_True_False': None,
            'dummy_False_True': None,
            'dummy_True_True': None
        }
        option = options.get(key)
        if option is None:
            raise InvalidCommandLineOptionError("Colocator/kernel/data type combination is not compatible")
        if option[2] is _GenericKernel:
            if kernel_name is None:
                raise InvalidCommandLineOptionError('A kernel must be specified for colocator "{}"'.format(method_name))
            else:
                option[2] = get_kernel(kernel_name)
        else:
            if kernel_name is not None:
                raise InvalidCommandLineOptionError(
                    'A kernel cannot be specified for colocator "{}"'.format(method_name))
        return option

    def _get_colocator_params(self, params):
        """
        Separates the parameters understood by the colocator from those for the constraint.
        :param params: combined colocator/constraint parameters
        :return: tuple containing (dict of colocator parameters, dict of constraint parameters)
        """
        col_param_names = ['fill_value', 'var_name', 'var_long_name', 'var_units']
        col_params = {}
        con_params = {}
        for key, value in params.iteritems():
            if key in col_param_names:
                col_params[key] = value
            else:
                con_params[key] = value
        return col_params, con_params

    def _instantiate_with_params(self, cls, params):
        """Create an instance of a class, if non-None, passing the supplied parameters, if any, to the constructor.
        :param cls: class of object to instantiate
        :param params: parameters to pass to constructor
        :return: object or None if class is None
        """
        obj = None
        if cls is not None:
            if params is not None:
                obj = cls(**params)
            else:
                obj = cls()
        return obj


class Colocate(object):
    """
    Perform a general colocation
    """

    def __init__(self, sample_points, output_filename, missing_data_for_missing_sample=False,
                 colocator_factory=ColocatorFactory()):
        """
        Constructor
        :param sample_points: Sample points to colocate on to
        :param output_filename: Filename to output to
        :param missing_data_for_missing_sample: Write missing values out when sample data is missing
        :return:
        """
        self.sample_points = sample_points
        self.output_file = output_filename
        self.missing_data_for_missing_sample = missing_data_for_missing_sample
        self.coords_to_be_written = True
        self.colocator_factory = colocator_factory

    def colocate(self, data, col_name=None, col_params=None, kern=None, kern_params=None):
        """
        Perform the colocation
        :param data: data to colocate
        :param col_name: name of the colocator
        :param col_params: parameters dictionary for the colocation and constraint
        :param kern: the kernel to use
        :param kern_params: the kernel parameters to use
        :return: colocated data
        """
        from jasmin_cis.exceptions import CoordinateNotFoundError
        from time import time
        from jasmin_cis.cis import __version__

        # Find colocator, constraint and kernel to use
        col_params['missing_data_for_missing_sample'] = self.missing_data_for_missing_sample
        col, con, kernel = self.colocator_factory.get_colocator_instances_for_method(col_name, kern, col_params,
                                                                                     kern_params,
                                                                                     self.sample_points.is_gridded,
                                                                                     data.is_gridded)
        logging.info("Colocator: " + str(col_name))
        logging.info("Kernel: " + str(kern))

        logging.info("Colocating, this could take a while...")
        t1 = time()
        try:
            new_data = col.colocate(self.sample_points, data, con, kernel)
        except TypeError as e:
            raise CoordinateNotFoundError('Colocator was unable to compare data points, check the dimensions of each '
                                          'data set and the co-location methods chosen. \n' + str(e))

        logging.info("Completed. Total time taken: " + str(time() - t1))

        filenames = None
        variables = None
        try:
            filenames = data.filenames
            variables = data.var_name
        except AttributeError:
            pass  # It's not critical if we can't get the history.

        for data in new_data:
            history = "Colocated onto sampling from: " + str(self.sample_points.filenames) + " " \
                      "\nusing CIS version " + __version__ + " " + \
                      "\nvariables: " + str(variables) + " " + \
                      "\nwith files: " + str(filenames) + " " + \
                      "\nusing colocator: " + str(col_name) + " " + \
                      "\ncolocator parameters: " + str(col_params) + " " + \
                      "\nkernel: " + str(kern) + " " + \
                      "\nkernel parameters: " + str(kern_params)
            data.add_history(history)
        return new_data
