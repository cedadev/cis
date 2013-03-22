'''
    Top level colocation object
'''
import logging


class Colocate(object):

    def __init__(self, sample_files, sample_var, sample_product, output_file):
        from jasmin_cis.data_io.read import read_coordinates, read_data
        from jasmin_cis.data_io.write_netcdf import write_coordinates

        self.sample_files = sample_files
        if sample_var is None:
            coords = read_coordinates(sample_files, sample_product)
            sample_points = coords.get_coordinates_points()

        else:
            data = read_data(sample_files, sample_var, sample_product)
            coords = data.coords()
            sample_points = data.get_all_points()

        write_coordinates(coords, output_file)

        self.sample_points = sample_points
        self.output_file = output_file

    @staticmethod
    def _get_valid_colocator_instance(col_name, col_params):
        from jasmin_cis.col_framework import get_colocator
        from jasmin_cis.exceptions import InvalidCommandLineOptionError

        if col_name is None:
            col_name = 'DefaultColocator'
        col_cls = get_colocator(col_name)

        try:
            if col_params is not None:
                col = col_cls(**col_params)
            else:
                col = col_cls()
        except TypeError as e:
            raise InvalidCommandLineOptionError(str(e)+"\nInvalid argument for specified colocator.")
        return col

    @staticmethod
    def _get_valid_constraint_instance(con_name, con_params):
        from jasmin_cis.col_framework import get_constraint
        from jasmin_cis.exceptions import InvalidCommandLineOptionError

        if con_name is None:
            con_name = 'DummyConstraint'
        con_cls = get_constraint(con_name)

        try:
            if con_params is not None:
                con = con_cls(**con_params)
            else:
                con = con_cls()
        except TypeError as e:
            raise InvalidCommandLineOptionError(str(e)+"\nInvalid argument for specified constraint method.")
        return con

    @staticmethod
    def _get_valid_kernel_instance(kern_name, kern_params, cube=False):
        from jasmin_cis.col_framework import get_kernel
        from jasmin_cis.exceptions import InvalidCommandLineOptionError

        if kern_name is None:
            if cube:
                kern_name = 'nn_gridded'
            else:
                kern_name = 'nn_horizontal'
        kern_cls = get_kernel(kern_name)

        try:
            if kern_params is not None:
                kernel = kern_cls(**kern_params)
            else:
                kernel = kern_cls()
        except TypeError as e:
            raise InvalidCommandLineOptionError(str(e)+"\nInvalid argument for specified kernel.")

        return kernel

    def colocate(self, variable, filenames, col_name=None, col_params=None, con_method=None, con_params=None, kern=None, kern_params=None, product = None):
        from jasmin_cis.data_io.read import read_data
        from jasmin_cis.data_io.write_netcdf import add_data_to_file
        from jasmin_cis.exceptions import CoordinateNotFoundError
        from time import time
        from iris import cube
        from jasmin_cis.cis import __version__

        logging.info("Reading data for: "+variable)
        data = read_data(filenames, variable, product)

        # Find colocator, constraint_fn and kernel to use
        col = Colocate._get_valid_colocator_instance(col_name, col_params)
        con = Colocate._get_valid_constraint_instance(con_method, con_params)
        kernel = Colocate._get_valid_kernel_instance(kern, kern_params, isinstance(data, cube.Cube))

        logging.info("Colocator: ", col_name)
        logging.info("Constraints: ", con_method)
        logging.info("kernel: ", kern)

        logging.info("Colocating, this could take a while...")
        t1 = time()
        try:
            new_data = col.colocate(self.sample_points, data, con, kernel)
        except TypeError as e:
            raise CoordinateNotFoundError('Colocator was unable to compare data points, check the dimensions of each '
                                          'data set and the co-location methods chosen. \n'+str(e))

        logging.info("Completed. Total time taken: " + str(time()-t1))

        logging.info("Appending data to "+self.output_file)
        for data in new_data:
            data.metadata.history += "Colocated onto sampling from: " + str(self.sample_files) + " using CIS version " + __version__ + \
                                      "\nvariable: " + str(variable) + \
                                      "\nwith files: " + str(filenames) + \
                                      "\nusing colocator: " + str(col_name) + \
                                      "\ncolocator parameters: " + str(col_params) + \
                                      "\nconstraint method: " + str(con_method) + \
                                      "\nconstraint parameters: " + str(con_params) + \
                                      "\nkernel: " + str(kern) + \
                                      "\nkernel parameters: " + str(kern_params)

            add_data_to_file(data, self.output_file)