'''
    Top level colocation object
'''
import logging


class Colocate(object):

    def __init__(self, sample_file, output_file):
        from jasmin_cis.data_io.read import read_coordinates
        from jasmin_cis.data_io.write_netcdf import write_coordinates

        coords = read_coordinates(sample_file)

        sample_points = coords.get_coordinates_points()
        write_coordinates(coords, output_file)

        self.sample_points = sample_points
        self.output_file = output_file

    def colocate(self, variable, filenames, col=None, con_method=None, con_params=None, kern=None, kern_params=None):
        from jasmin_cis.data_io.read import read_data
        from jasmin_cis.data_io.write_netcdf import add_data_to_file
        from jasmin_cis.col_framework import get_constraint, get_kernel, get_colocator
        from jasmin_cis.exceptions import CoordinateNotFoundError, InvalidCommandLineOptionError
        from time import time
        from iris import cube

        logging.info("Reading data for: "+variable)
        data = read_data(filenames, variable)

        if con_method is None:
            con_method = 'DummyConstraint'
        con_cls = get_constraint(con_method)

        try:
            con = con_cls(**con_params)
        except TypeError as e:
            raise InvalidCommandLineOptionError(str(e)+"\nInvalid argument for specified constraint method.")

        if kern is None:
            if isinstance(data, cube.Cube):
                kern = 'nn_gridded'
            else:
                kern = 'nn_horizontal'
        kern_cls = get_kernel(kern)

        try:
            kernel = kern_cls(**kern_params)
        except TypeError as e:
            raise InvalidCommandLineOptionError(str(e)+"\nInvalid argument for specified kernel.")

        # Find colocator, constraint_fn and kernel to use
        if col is None:
            col = 'DefaultColocator'
        col = get_colocator(col)

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
            add_data_to_file(data, self.output_file)