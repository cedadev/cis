'''
    Colocation routines - to be implemented
'''
from collections import namedtuple

import numpy as np
from time import time
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
from utils import copy_attributes


def colocate(filenames, con_method, kern, col, variable, sample_points, output_file, con_params=None, kern_params=None):
    from data_io.read import read_data
    from data_io.write_netcdf import add_data_to_file
    from col_framework import get_constraint, get_kernel, get_colocator

    logging.info("Reading data for: "+variable)
    data = read_data(filenames, variable)

    # Find colocator, constraint_fn and kernel to use
    con_fn = get_constraint(con_method)
    kernel = get_kernel(kern)
    col = get_colocator(col)

    if con_params is not None: copy_attributes(con_params, con_fn)
    if kern_params is not None: copy_attributes(kern_params, kernel)

    logging.info("Colocating, this could take a while...")
    t1 = time()
    new_data = col.colocate(sample_points, data, con_fn, kernel)

    logging.info("Completed. Total time taken: " + str(time()-t1))

    add_data_to_file(new_data, output_file)