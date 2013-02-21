'''
    Colocation routines - to be implemented
'''
#from collections import namedtuple

#import numpy as np
import logging

# class Colocator(object):
#
#     def __init__(self, points, data, col_method='nn', constraints=None, fill_value=None):
#         from jasmin_cis.exceptions import InvalidColocationMethodError
#         from iris import cube
#
#         self.points = points
#         self.data = data
#         self.constraints = constraints
#         if fill_value is None:
#             self.fill_value = np.Infinity
#         else:
#             self.fill_value = fill_value
#
#         if isinstance(data, cube.Cube):
#             methods = Colocator.gridded_colocation_methods._asdict()
#         else:
#             methods = Colocator.ungridded_colocation_methods._asdict()
#
#         self.method = methods[col_method]
#
#         if self.method is None:
#             raise InvalidColocationMethodError('This co-location method is invalid for this data type')
#
#     def _update_data(self):
#         from iris import cube
#         from jasmin_cis.data_io.ungridded_data import UngriddedData
#         if isinstance(self.points, cube.Cube):
#             # Return a cube with those points - TODO
#             pass
#         else:
#             return UngriddedData.from_points_array(self.points)
#
#     ColocationTechniques = namedtuple('Techniques',['nn', 'li'])
#     gridded_colocation_methods = ColocationTechniques(find_nn_value_gridded, find_value_by_li)
#     ungridded_colocation_methods = ColocationTechniques(find_nn_value_ungridded, None)

class Colocate(object):

    def __init__(self, sample_file, output_file):
        from data_io.read import read_file_coordinates
        from data_io.write_netcdf import write_coordinates

        coords = read_file_coordinates(sample_file)

        sample_points = coords.get_coordinates_points()
        write_coordinates(coords, output_file)

        self.sample_points = sample_points
        self.output_file = output_file


    def colocate(self, variable, filenames, col='DefaultColocator', con_method=None, con_params=None, kern=None, kern_params=None):
        from data_io.read import read_data
        from data_io.write_netcdf import add_data_to_file
        from col_framework import get_constraint, get_kernel, get_colocator
        from utils import copy_attributes
        from time import time
        from iris import cube

        logging.info("Reading data for: "+variable)
        data = read_data(filenames, variable)

        if con_method is None:
            con_method = 'DefaultConstraint'
        con_fn = get_constraint(con_method)

        if kern is None:
            if isinstance(data, cube.Cube):
                kern = 'nn_gridded'
            else:
                kern = 'nn_ungridded'
        kernel = get_kernel(kern)

        # Find colocator, constraint_fn and kernel to use
        col = get_colocator(col)

        if con_params is not None: copy_attributes(con_params, con_fn)
        if kern_params is not None: copy_attributes(kern_params, kernel)

        logging.info("Colocating, this could take a while...")
        t1 = time()
        new_data = col.colocate(self.sample_points, data, con_fn, kernel)

        logging.info("Completed. Total time taken: " + str(time()-t1))

        add_data_to_file(new_data, self.output_file)