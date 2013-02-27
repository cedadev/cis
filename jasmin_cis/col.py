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
        from jasmin_cis.utils import copy_attributes
        from timeUtil import time
        from iris import cube

        logging.info("Reading data for: "+variable)
        data = read_data(filenames, variable)

        if con_method is None:
            con_method = 'DummyConstraint'
        con_fn = get_constraint(con_method)

        if kern is None:
            if isinstance(data, cube.Cube):
                kern = 'nn_gridded'
            else:
                kern = 'nn_horizontal'
        kernel = get_kernel(kern)

        # Find colocator, constraint_fn and kernel to use
        if col is None:
            col = 'DefaultColocator'
        col = get_colocator(col)

        if con_params is not None: copy_attributes(con_params, con_fn)
        if kern_params is not None: copy_attributes(kern_params, kernel)

        logging.info("Colocating, this could take a while...")
        t1 = time()
        new_data = col.colocate(self.sample_points, data, con_fn, kernel)

        logging.info("Completed. Total time taken: " + str(time()-t1))

        logging.info("Appending data to "+self.output_file)
        for data in new_data:
            add_data_to_file(data, self.output_file)