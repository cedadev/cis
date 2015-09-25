"""
    Top level collocation objects
"""
import logging
from cis.exceptions import InvalidCommandLineOptionError


class _GenericKernel(object):
    """
    Marker class used by _get_collocator_classes_for_method to indicate that one of the generic kernels is needed.
    """
    pass


class CollocatorFactory(object):
    """
    Class for creating Collocator, Constraint and Kernel instances
    """

    def get_collocator_instances_for_method(self, method_name, kernel_name, collocator_params, kernel_params,
                                            sample_gridded, data_gridded):
        """
        Get instances of the correct classes for collocation
        :param method_name: Collocation method name (e.g. 'lin', 'nn')
        :param kernel_name: Kernel class name
        :param collocator_params: Collocation parameters
        :param kernel_params: Kernel parameters
        :param sample_gridded: Is the sample data gridded?
        :param data_gridded: Is the collocation data gridded?
        :return: Collocator, Constrain and Kernel instances
        """
        import cis.collocation.col_implementations as ci
        col_cls, constraint_cls, kernel_cls = self._get_collocator_classes_for_method(method_name, kernel_name,
                                                                                      sample_gridded, data_gridded)
        # We aren't able to pass any arguments to the li kernel when using the lin collocator so we pop them off here...
        if kernel_cls is ci.li:
            kernel_params = {k: collocator_params.get(k, None) for k in ('nn_vertical', 'extrapolate')}
        collocator_params, constraint_params = self._get_collocator_params(collocator_params)
        col = self._instantiate_with_params(col_cls, collocator_params)
        del constraint_params['missing_data_for_missing_sample']
        con = self._instantiate_with_params(constraint_cls, constraint_params)
        kernel = self._instantiate_with_params(kernel_cls, kernel_params)
        return col, con, kernel

    def get_default_collocator_name(self, method_name, sample_gridded, data_gridded):
        # Default collocators - (sample_gridded, data_gridded) : collocator_name
        default_methods = {(True, True): 'lin',
                           (True, False): 'bin',
                           (False, True): 'nn',
                           (False, False): 'box'}

        if method_name is None:
            # If no collocator has been specified we'll identify a default.
            method_name = default_methods.get((sample_gridded, data_gridded))
        return method_name

    def _get_collocator_classes_for_method(self, method_name, kernel_name, sample_gridded, data_gridded):
        """
        Gets the collocator, constraint and kernel classes corresponding to a specified collocation method and kernel
        name.
        :param method_name: collocation method name
        :param kernel_name: kernel name
        :param sample_gridded: True if sample points are gridded, otherwise False
        :param data_gridded: True if data points are gridded, otherwise False
        :return: CollocationOptions containing relevant classes
        """
        import cis.collocation.col_implementations as ci
        from cis.collocation.col_framework import get_kernel

        method_name = self.get_default_collocator_name(method_name, sample_gridded, data_gridded)

        key = '_'.join([method_name, str(sample_gridded), str(data_gridded)])

        # Method Sample  Data    collocator                      constraint                    kernel
        #   name   gridded gridded
        options = {
            'lin_False_False': None,
            'lin_True_False': None,
            'lin_False_True': [ci.GeneralUngriddedCollocator, None, ci.li],
            'lin_True_True': [ci.GriddedCollocator, None, ci.gridded_gridded_li],
            'nn_False_False': None,
            'nn_True_False': None,
            'nn_False_True': [ci.GeneralUngriddedCollocator, None, ci.nn_gridded],
            'nn_True_True': [ci.GriddedCollocator, None, ci.gridded_gridded_nn],
            'bin_False_False': None,
            'bin_True_False': [ci.GeneralGriddedCollocator, ci.BinnedCubeCellOnlyConstraint, _GenericKernel],
            'bin_False_True': None,
            'bin_True_True': None,
            'box_False_False': [ci.GeneralUngriddedCollocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_True_False': [ci.GeneralGriddedCollocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_False_True': [ci.GeneralUngriddedCollocator, ci.SepConstraintKdtree, _GenericKernel],
            'box_True_True': [ci.GeneralGriddedCollocator, ci.SepConstraintKdtree, _GenericKernel],
            'dummy_False_False': [ci.DummyCollocator, None, None],
            'dummy_True_False': None,
            'dummy_False_True': None,
            'dummy_True_True': None
        }
        option = options.get(key)
        if option is None:
            raise InvalidCommandLineOptionError("Collocator/kernel/data type combination is not compatible")
        if option[2] is _GenericKernel:
            if kernel_name is None:
                kernel_name = 'moments'
            option[2] = get_kernel(kernel_name)
        else:
            if kernel_name is not None:
                raise InvalidCommandLineOptionError(
                    'A kernel cannot be specified for collocator "{}"'.format(method_name))
        return option

    def _get_collocator_params(self, params):
        """
        Separates the parameters understood by the collocator from those for the constraint.
        :param params: combined collocator/constraint parameters
        :return: tuple containing (dict of collocator parameters, dict of constraint parameters)
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


class Collocate(object):
    """
    Perform a general collocation
    """

    def __init__(self, sample_points, missing_data_for_missing_sample=False, collocator_factory=CollocatorFactory()):
        """
        Constructor

        :param CommonData sample_points: Sample points to collocate on to
        :param output_filename: Filename to output to
        :param missing_data_for_missing_sample: Write missing values out when sample data is missing
        :param CollocatorFactory collocator_factory: An optional configuration object
        """
        self.sample_points = sample_points
        self.missing_data_for_missing_sample = missing_data_for_missing_sample
        self.coords_to_be_written = True
        self.collocator_factory = collocator_factory

    def collocate(self, data, col_name=None, col_params=None, kern=None, kern_params=None):
        """
        Perform the collocation.

        :param CommonData data: Data to collocate
        :param str col_name: Name of the collocator
        :param dict col_params: Parameters dictionary for the collocation and constraint
        :param str kern: The kernel to use
        :param dict kern_params: The kernel parameters to use
        :return CommonData: The collocated data
        :raises CoordinateNotFoundError: If the collocator was unable to compare the sample and data points
        """
        from cis.exceptions import CoordinateNotFoundError
        from time import time
        from cis import __version__

        # Find collocator, constraint and kernel to use
        col_params['missing_data_for_missing_sample'] = self.missing_data_for_missing_sample
        col, con, kernel = self.collocator_factory.get_collocator_instances_for_method(col_name, kern, col_params,
                                                                                     kern_params,
                                                                                     self.sample_points.is_gridded,
                                                                                     data.is_gridded)

        col_name = self.collocator_factory.get_default_collocator_name(col_name, self.sample_points.is_gridded,
                                                                     data.is_gridded)
        logging.info("Collocator: " + str(col_name))
        if kern is None:
            kernel_name = kernel.__class__.__name__
        else:
            kernel_name = str(kern)

        logging.info("Kernel: " + str(kernel_name))

        logging.info("Collocating, this could take a while...")
        t1 = time()
        try:
            new_data = col.collocate(self.sample_points, data, con, kernel)
        except TypeError as e:
            raise CoordinateNotFoundError('Collocator was unable to compare data points, check the dimensions of each '
                                          'data set and the collocation methods chosen. \n' + str(e))

        logging.info("Completed. Total time taken: " + str(time() - t1))

        filenames = None
        variables = None
        try:
            filenames = data.filenames
            variables = data.var_name
        except AttributeError:
            pass  # It's not critical if we can't get the history.

        for data in new_data:
            history = "Collocated onto sampling from: " + str(self.sample_points.filenames) + " " \
                      "\nusing CIS version " + __version__ + " " + \
                      "\nvariables: " + str(variables) + " " + \
                      "\nwith files: " + str(filenames) + " " + \
                      "\nusing collocator: " + str(col_name) + " " + \
                      "\ncollocator parameters: " + str(col_params) + " " + \
                      "\nkernel: " + str(kern) + " " + \
                      "\nkernel parameters: " + str(kern_params)
            data.add_history(history)
        return new_data
