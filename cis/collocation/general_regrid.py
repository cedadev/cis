import iris
import numpy as np

from cis.collocation.col_implementations import _fix_longitude_range
from cis.data_io.datalist import DataList
from cis.utils import apply_mask_to_numpy_array


def collocate(points, data, kernel='', extrapolate='mask', missing_data_for_missing_sample=True):
    """
    This collocator takes two Iris cubes, and collocates from the data cube onto the grid of the 'points' cube. The
    collocator then returns another Iris cube.
    :param points: An Iris cube with the sampling grid to collocate onto.
    :param data: The Iris cube with the data to be collocated.
    :param kernel: The kernel to use, current options are gridded_gridded_nn and gridded_gridded_li.
    :return: An Iris cube with the collocated data.
    """
    from iris.analysis import Nearest, Linear
    # Lin is the default for gridded -> gridded
    if kernel == '' or kernel == 'lin':
        kernel = Linear
    elif kernel == 'nn':
        kernel = Nearest
    else:
        raise ValueError("Invalid method specified for gridded -> gridded collocation: " + kernel)

    # Force the data longitude range to be the same as that of the sample grid.
    _fix_longitude_range(points.coords(), data)

    # Initialise variables used to create an output mask based on the sample data mask.
    sample_coord_lookup = {}  # Maps coordinate in sample data -> location in dimension order
    for idx, coord in enumerate(points.coords()):
        sample_coord_lookup[coord] = idx
    sample_coord_transpose_map = []  # For coords in both sample and data, contains the position in the sample
    other_coord_transpose_map = []  # For coords in data but not in sample, records that coord's position in data.
    repeat_size = 1
    output_mask = np.ma.nomask

    # Make a list of the coordinates we have, with each entry containing a list with the name of the coordinate and
    # the number of points along its axis. One is for the sample grid, which contains the points where we
    # interpolate too, and one is for the output grid, which will additionally contain any dimensions missing in the
    # sample grid.
    coord_names_and_sizes_for_sample_grid = []
    coord_names_and_sizes_for_output_grid = []
    for idx, coord in enumerate(data.coords(dim_coords=True)):
        # First try and find the coordinate in points, the sample grid. If an exception is thrown, it means that
        # name does not appear in the sample grid, and instead take the coordinate name and length from the original
        # data, as this is what we will be keeping.
        try:
            sample_coord = points.coords(coord.name())[0]
            coord_names_and_sizes_for_sample_grid.append([coord.name(), len(sample_coord.points)])
            # Find the index of the sample coordinate corresponding to the data coordinate.
            sample_coord_transpose_map.append(sample_coord_lookup[sample_coord])
        except IndexError:
            coord_names_and_sizes_for_output_grid.append([coord.name(), len(coord.points)])
            repeat_size *= len(coord.points)
            other_coord_transpose_map.append(idx)

    # Now we sort the sample coordinates so that they are in the same order as in the sample file,
    # rather than the order of the data file (that's the order we want the output dimensions).
    coord_names_and_sizes_for_sample_grid = [x[0] for x in sorted(zip(coord_names_and_sizes_for_sample_grid,
                                                                      sample_coord_transpose_map),
                                                                  key=lambda t: t[1])]

    # Adding the lists together in this way ensures that the coordinates not in the sample grid appear in the final
    # position, which is important for adding the points from the Iris interpolater to the new array. The data
    # returned from the Iris interpolater method will have dimensions of these missing coordinates, which needs
    # to be the final dimensions in the numpy array, as the iterator will give the position of the other dimensions.
    coord_names_and_sizes_for_output_grid = coord_names_and_sizes_for_sample_grid + \
                                            coord_names_and_sizes_for_output_grid

    # An array for the collocated data, with the correct shape
    output_shape = tuple(i[1] for i in coord_names_and_sizes_for_output_grid)
    new_data = np.zeros(output_shape)

    if missing_data_for_missing_sample:
        output_mask = _make_output_mask(coord_names_and_sizes_for_sample_grid, output_shape,
                                             points, repeat_size)

    # Now recreate the points cube, while ignoring any DimCoords in points that are not in the data cube
    new_dim_coord_list = []
    new_points_array_shape = []
    for i in range(0, len(coord_names_and_sizes_for_output_grid)):
        # Try and find the coordinate in the sample grid
        coord_found = points.coords(coord_names_and_sizes_for_output_grid[i][0])

        # If the coordinate exists in the sample grid then append the new coordinate to the list. Iris requires
        # this be given as a DimCoord object, along with a axis number, in a tuple pair.
        if len(coord_found) != 0:
            new_dim_coord_list.append((coord_found[0], len(new_dim_coord_list)))
            new_points_array_shape.append(coord_found[0].points.size)

    new_points_array = np.zeros(tuple(new_points_array_shape))

    # Use the new_data array to recreate points, without the DimCoords not in the data cube
    points = iris.cube.Cube(new_points_array, dim_coords_and_dims=new_dim_coord_list)

    output_cube = _iris_interpolate(coord_names_and_sizes_for_output_grid,
                                         coord_names_and_sizes_for_sample_grid, data,
                                         kernel, output_mask, points, extrapolate)

    if not isinstance(output_cube, list):
        return DataList([output_cube])
    else:
        return output_cube


def _make_output_mask(coord_names_and_sizes_for_sample_grid, output_shape, points, repeat_size):
    """ Creates a mask to apply to the output data based on the sample data mask. If there are coordinates in
    the data grid that are not in the sample grid, the same mask value is repeated for all values of the
    extra coordinates. If there are coordinates in the sample grid that are not in the data grid, a mask
    is not created since there is many to one correspondence between sample and output grid points.
    """
    output_mask = None

    # Construct the missing value mask from the sample data, if applicable.
    if len(coord_names_and_sizes_for_sample_grid) < len(points.dim_coords):
        # One or more axes collapsed so many sample points correspond to each output point.
        pass
    else:
        input_mask = np.ma.getmask(points.data)
        if input_mask is np.ma.nomask:
            # No sample data missing-value mask.
            pass
        else:
            # Fill in the remaining coordinates (those from the data which are not in the sample) by repeating
            # the constructed mask for each value of those coordinates
            output_mask = np.reshape(np.repeat(points.data.mask, repeat_size), output_shape)
    return output_mask


def _iris_interpolate(coord_names_and_sizes_for_output_grid, coord_names_and_sizes_for_sample_grid, data, kernel,
                      output_mask, points, extrapolate):
    """ Collocates using iris.analysis.interpolate
    """
    coordinate_point_pairs = []
    for j in range(0, len(coord_names_and_sizes_for_sample_grid)):
        # For each coordinate make the list of tuple pair Iris requires, for example
        # [('latitude', -90), ('longitude, 0')]
        coordinate_point_pairs.append((coord_names_and_sizes_for_sample_grid[j][0],
                                       points.dim_coords[j].points))

    # The result here will be a cube with the correct dimensions for the output, so interpolated over all points
    # in coord_names_and_sizes_for_output_grid.
    output_cube = data.interpolate(coordinate_point_pairs, kernel.interpolater(extrapolation_mode=extrapolate))

    # Iris outputs interpolated cubes with the dimensions in the order of the data grid, not the sample grid,
    # so we need to rearrange the order of the dimensions.
    output_coord_lookup = {}
    for idx, coord in enumerate(output_cube.dim_coords):
        output_coord_lookup[coord.name()] = idx
    transpose_map = [output_coord_lookup[coord[0]] for coord in coord_names_and_sizes_for_output_grid]
    output_cube.transpose(transpose_map)

    if isinstance(output_cube, list):
        for idx, data in enumerate(output_cube):
            output_cube[idx].data = apply_mask_to_numpy_array(data.data, output_mask)
    else:
        output_cube.data = apply_mask_to_numpy_array(output_cube.data, output_mask)
    return output_cube
