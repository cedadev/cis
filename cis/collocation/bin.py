import logging

import numpy as np
from iris.cube import Cube

import cis.exceptions
from cis.collocation import data_index as data_index
from cis.collocation.col_implementations import make_coord_map, _fix_longitude_range
from cis.data_io.cube_utils import get_non_masked_points
from cis.data_io.datalist import DataList
from cis.utils import log_memory_profile, set_standard_name_if_valid
from cis.collocation.data_index import GridCellBinIndexInSlices


index = GridCellBinIndexInSlices()


def collocate(points, data, kernel=None, fill_value=None, missing_data_for_missing_sample=True):
    """
    :param points: cube defining the sample points
    :param data: CommonData object providing data to be collocated (or list of Data)
    :param constraint: instance of a Constraint subclass, which takes a data object and returns a subset of that
                       data based on it's internal parameters
    :param kernel: instance of a Kernel subclass which takes a number of points and returns a single value
    :return: DataList of collocated data
    """
    log_memory_profile("GeneralGriddedCollocator Initial")

    # TODO All this ---->>

    if isinstance(data, list):
        # If data is a list then call this method recursively over each element
        output_list = []
        for variable in data:
            collocated = collocate(points, variable, kernel)
            output_list.extend(collocated)
        return DataList(output_list)

    data_points = get_non_masked_points(data)

    log_memory_profile("GeneralGriddedCollocator Created data hyperpoint list view")

    # Work out how to iterate over the cube and map HyperPoint coordinates to cube coordinates.
    coord_map = make_coord_map(points, data)
    if missing_data_for_missing_sample and len(coord_map) is not len(points.coords()):
        raise cis.exceptions.UserPrintableException(
            "A sample variable has been specified but not all coordinates in the data appear in the sample so "
            "there are multiple points in the sample data so whether the data is missing or not can not be "
            "determined")

    coords = points.coords()
    shape = []
    output_coords = []

    # Find shape of coordinates to be iterated over.
    for (hpi, ci, shi) in coord_map:
        coord = coords[ci]
        if coord.ndim > 1:
            raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                      " than one is not supported (coordinate %s)", coord.name())
        # Ensure that bounds exist.
        if not coord.has_bounds():
            logging.warning("Creating guessed bounds as none exist in file")
            coord.guess_bounds()
        shape.append(coord.shape[0])
        output_coords.append(coord)

    _fix_longitude_range(coords, data_points)

    log_memory_profile("GeneralGriddedCollocator Created output coord map")

    # TODO <<___ probably belongs one layer up and should be iris specific

    index.index_data(coords, data_points, coord_map)
    data_index.create_indexes(kernel, points, data_points, coord_map)

    log_memory_profile("GeneralGriddedCollocator Created indexes")

    # Initialise output array as initially all masked, and set the appropriate fill value.
    values = []
    for i in range(kernel.return_size):
        val = np.ma.zeros(shape)
        val.mask = True
        val.fill_value = fill_value
        values.append(val)

    if kernel.return_size == 1:
        set_value_kernel = _set_single_value_kernel
    else:
        set_value_kernel = _set_multi_value_kernel

    logging.info("--> Co-locating...")

    # Iterate over constrained cells
    iterator = index.get_data_iterator(missing_data_for_missing_sample, data_points, points)
    for out_indices, data_values in iterator:
        try:
            kernel_val = kernel.get_value_for_data_only(data_values)
            set_value_kernel(kernel_val, values, out_indices)
        except ValueError:
            # ValueErrors are raised by Kernel when there are no points to operate on.
            # We don't need to do anything.
            pass

    log_memory_profile("GeneralGriddedCollocator Completed collocation")

    # Construct an output cube containing the collocated data.
    kernel_var_details = kernel.get_variable_details(data.var_name, data.long_name, data.standard_name, data.units)

    output = DataList([])
    for idx, val in enumerate(values):
        cube = _create_collocated_cube(data, val, output_coords)
        data_with_nan_and_inf_removed = np.ma.masked_invalid(cube.data)
        data_with_nan_and_inf_removed.set_fill_value(fill_value)
        cube.data = data_with_nan_and_inf_removed
        cube.var_name = kernel_var_details[idx][0]
        cube.long_name = kernel_var_details[idx][1]
        set_standard_name_if_valid(cube, kernel_var_details[idx][2])
        try:
            cube.units = kernel_var_details[idx][3]
        except ValueError:
            logging.warn("Units are not cf compliant, not setting them. Units {}".format(kernel_var_details[idx][3]))

        # Sort the cube into the correct shape, so that the order of coordinates
        # is the same as in the source data
        coord_map = sorted(coord_map, key=lambda x: x[1])
        transpose_order = [coord[2] for coord in coord_map]
        cube.transpose(transpose_order)
        output.append(cube)

    log_memory_profile("GeneralGriddedCollocator Finished")

    return output


def _set_multi_value_kernel(kernel_val, values, indices):
    # This kernel returns multiple values:
    for idx, val in enumerate(kernel_val):
        values[idx][indices] = val


def _set_single_value_kernel(kernel_val, values, indices):
    values[0][indices] = kernel_val


def _create_collocated_cube(src_data, data, coords):
    """Creates a cube using the metadata from the source cube and supplied data.

    :param src_data: ungridded data that was to be collocated
    :param data: collocated data values
    :param coords: coordinates for output cube
    :return: cube of collocated data
    """
    dim_coords_and_dims = []
    for idx, coord in enumerate(coords):
        dim_coords_and_dims.append((coord, idx))
    cube = Cube(data, standard_name=src_data.standard_name,
                       long_name=src_data.long_name,
                       var_name=src_data.var_name,
                       units=src_data.units,
                       dim_coords_and_dims=dim_coords_and_dims)
    return cube
