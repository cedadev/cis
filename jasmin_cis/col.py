'''
    Top level colocation object
'''
from collections import namedtuple
import logging

import jasmin_cis.col_implementations as ci
from jasmin_cis.col_framework import get_kernel
from jasmin_cis.exceptions import InvalidCommandLineOptionError


class ColocationOptions(namedtuple('ColocationOptions', ['colocator', 'constraint', 'kernel'])):
    """Colocator, constraint, kernel combination.
    """
    pass


class _GenericKernel(object):
    """Marker class used by _get_colocator_classes_for_method to indicate that one of the generic kernels is needed.
    """
    pass


def _instantiate_with_params(cls, params):
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

    def __init__(self, sample_files, sample_var, sample_product, output_file):
        from jasmin_cis.data_io.read import read_coordinates, read_data

        self.sample_files = sample_files
        self.missing_data_for_missing_sample = False
        if sample_var is None:
            sample_points = read_coordinates(sample_files, sample_product)
        else:
            sample_points = read_data(sample_files, sample_var, sample_product)
            self.missing_data_for_missing_sample = True

        self.sample_points = sample_points
        self.output_file = output_file
        self.coords_to_be_written = True

    @staticmethod
    def _get_colocator_classes_for_method(method_name, kernel_name, sample_gridded, data_gridded):
        """Gets the colocator, constraint and kernel classes corresponding to a specified colocation method and kernel
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

        #   Method Sample  Data    colocator                      constraint                    kernel
        #   name   gridded gridded
        options = {
            'lin_False_False':   None,
            'lin_True_False':    None,
            'lin_False_True':    [ci.GeneralUngriddedColocator, None,                         ci.li],
            'lin_True_True':     [ci.GriddedColocator,          None,                         ci.gridded_gridded_li],
            'nn_False_False':    None,
            'nn_True_False':     None,
            'nn_False_True':     [ci.GeneralUngriddedColocator, None,                         ci.nn_gridded],
            'nn_True_True':      [ci.GriddedColocator,          None,                         ci.gridded_gridded_nn],
            'bin_False_False':   None,
            'bin_True_False':    [ci.GeneralGriddedColocator,   ci.BinningCubeCellConstraint, _GenericKernel],
            'bin_False_True':    None,
            'bin_True_True':     [ci.GeneralGriddedColocator,   ci.BinningCubeCellConstraint, _GenericKernel],
            'box_False_False':   [ci.GeneralUngriddedColocator, ci.SepConstraintKdtree,       _GenericKernel],
            'box_True_False':    [ci.GeneralGriddedColocator,   ci.SepConstraintKdtree,       _GenericKernel],
            'box_False_True':    [ci.GeneralUngriddedColocator, ci.SepConstraintKdtree,       _GenericKernel],
            'box_True_True':     [ci.GeneralGriddedColocator,   ci.SepConstraintKdtree,       _GenericKernel],
            'dummy_False_False': [ci.DummyColocator,            None,                         None],
            'dummy_True_False':  None,
            'dummy_False_True':  None,
            'dummy_True_True':   None
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
        return ColocationOptions(*option)

    @staticmethod
    def _get_colocator_params(params):
        """Separates the parameters understood by the colocator from those for the constraint.
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

    def colocate(self, variable, filenames, col_name=None, col_params=None, kern=None, kern_params=None, product=None):
        from jasmin_cis.data_io.read import read_data
        from jasmin_cis.data_io.write_netcdf import add_data_to_file
        from jasmin_cis.data_io.write_netcdf import write_coordinates
        from jasmin_cis.utils import remove_file_prefix
        from jasmin_cis.exceptions import CoordinateNotFoundError
        from time import time
        import iris
        from jasmin_cis.cis import __version__

        logging.info("Reading data for: "+variable)
        data = read_data(filenames, variable, product)

        # Find colocator, constraint and kernel to use
        col_classes = self._get_colocator_classes_for_method(col_name, kern, self.sample_points.is_gridded,
                                                             data.is_gridded)
        col_params, con_params = self._get_colocator_params(col_params)
        col_params['missing_data_for_missing_sample'] = self.missing_data_for_missing_sample
        col = _instantiate_with_params(col_classes.colocator, col_params)
        con = _instantiate_with_params(col_classes.constraint, con_params)
        kernel = _instantiate_with_params(col_classes.kernel, kern_params)

        logging.info("Colocator: " + str(col_name))
        logging.info("Kernel: " + str(kern))

        logging.info("Colocating, this could take a while...")
        t1 = time()
        try:
            new_data = col.colocate(self.sample_points, data, con, kernel)
        except TypeError as e:
            raise CoordinateNotFoundError('Colocator was unable to compare data points, check the dimensions of each '
                                          'data set and the co-location methods chosen. \n'+str(e))

        logging.info("Completed. Total time taken: " + str(time()-t1))

        logging.info("Appending data to "+self.output_file)

        # Must explicitly write coordinates for ungridded data.
        self.coords_to_be_written = self.coords_to_be_written and not isinstance(new_data[0], iris.cube.Cube)

        for data in new_data:
            history = "Colocated onto sampling from: " + str(self.sample_files) + " "\
                                      "\nusing CIS version " + __version__ + " " +\
                                      "\nvariable: " + str(variable) + " " +\
                                      "\nwith files: " + str(filenames) + " " +\
                                      "\nusing colocator: " + str(col_name) + " " +\
                                      "\ncolocator parameters: " + str(col_params) + " " +\
                                      "\nkernel: " + str(kern) + " " +\
                                      "\nkernel parameters: " + str(kern_params)
            data.add_history(history)

            if self.coords_to_be_written:
                write_coordinates(self.sample_points, self.output_file)
                self.coords_to_be_written = False

            if isinstance(data, iris.cube.Cube):
                self.output_file = remove_file_prefix('cis-', self.output_file)
                iris.save(data, self.output_file)
            else:
                add_data_to_file(data, self.output_file)
