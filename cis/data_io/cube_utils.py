from time import gmtime, strftime
import logging

import iris
from iris.cube import Cube
import numpy as np

from cis.data_io.hyperpoint import HyperPoint
from cis.data_io.hyperpoint_view import GriddedHyperPointView
import six


def load_cube(*args, **kwargs):
    """
    Load a single GriddedData object through the iris load interface, but also attempt concatenation if merging fails

    :return GriddedData: A single GriddedData object
    :raises ValueError: If 0 or more than one cube is found
    """
    from iris.exceptions import MergeError, ConcatenateError
    # Removes warnings and prepares for future Iris change
    iris.FUTURE.netcdf_promote = True

    cubes = iris.load(*args, **kwargs)

    try:
        iris_cube = cubes.merge_cube()
    except MergeError as e:
        logging.info("Unable to merge cubes on load: \n {}\nAttempting to concatenate instead.".format(e))
        try:
            iris_cube = cubes.concatenate_cube()
        except ConcatenateError as e:
            logging.error("Unable to concatenate cubes on load: \n {}".format(e))
            raise ValueError("Unable to create a single cube from arguments given: {}".format(args))
    except ValueError as e:
        raise ValueError("No cubes found")
    return iris_cube


def make_new_with_same_coordinates(cube, data=None, var_name=None, standard_name=None,
                                   long_name=None, history=None, units=None, flatten=False):
    """
    Create a new, empty GriddedData object with the same coordinates as this one
    :param data: Data to use (if None then defaults to all zeros)
    :param var_name: Variable name
    :param standard_name: Variable CF standard name
    :param long_name: Variable long name
    :param history: Data history string
    :param units: Variable units
    :param flatten: Whether to flatten the data shape (for ungridded data only)
    :return: GriddedData instance
    """
    if data is None:
        data = np.zeros(cube.shape)
    data = Cube(data=data, standard_name=standard_name, long_name=long_name, var_name=var_name,
                       units=units, dim_coords_and_dims=cube._dim_coords_and_dims,
                       aux_coords_and_dims=cube._aux_coords_and_dims, aux_factories=cube._aux_factories)
    # Add history separately as it is not a constructor argument
    data.add_history(history)
    return data


def get_coordinates_points(cube):
    """Returns a HyperPointView of the points.
    :return: HyperPointView of all the data points
    """
    all_coords = [((c[0].points, c[1]) if c is not None else None) for c in cube.find_standard_coords()]
    return GriddedHyperPointView(all_coords, cube.data)


def get_all_points(cube):
    """Returns a HyperPointView of the points.
    :return: HyperPointView of all the data points
    """
    all_coords = [((c[0].points, c[1]) if c is not None else None) for c in cube.find_standard_coords()]
    return GriddedHyperPointView(all_coords, cube.data)


def get_non_masked_points(cube):
    """Returns a HyperPointView of the points.
    :return: HyperPointView of all the data points
    """
    all_coords = [((c[0].points, c[1]) if c is not None else None) for c in cube.find_standard_coords()]
    return GriddedHyperPointView(all_coords, cube.data, non_masked_iteration=True)


def find_standard_coords(cube):
    """Constructs a list of the standard coordinates.
    The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
    list in this order.
    :return: list of coordinates or None if coordinate not present
    """
    ret_list = []

    coords = cube.coords(dim_coords=True)
    for name in HyperPoint.standard_names:
        coord_and_dim = None
        for idx, coord in enumerate(coords):
            if coord.standard_name == name:
                coord_and_dim = (coord, idx)
                break
        ret_list.append(coord_and_dim)

    return ret_list


def add_history(cube, new_history):
    """Appends to, or creates, the history attribute using the supplied history string.

    The new entry is prefixed with a timestamp.
    :param new_history: history string
    """
    timestamp = strftime("%Y-%m-%dT%H:%M:%SZ ", gmtime())
    if 'history' not in cube.attributes:
        cube.attributes['history'] = timestamp + new_history
    else:
        cube.attributes['history'] += '\n' + timestamp + new_history


def is_gridded(cube, coords):
    """Are all the coordinates specified orthogonal in this cube? (Are they all dim coords?)

    :param cube: Cube to test
    :param coords list: list of Coord or str objects to check for orthogonality
    :raises ValueError: If some of the coordinates aren't present as this would lead to a false negative.
    """
    if not all(cube.coords(c) for c in coords):
        raise ValueError("Not all coordinates are present in cube")
    return all(cube.coords(c, dim_coords=True) for c in coords)


def set_longitude_range(cube, range_start):
    """Rotates the longitude coordinate array and changes its values by
    360 as necessary to force the values to be within a 360 range starting
    at the specified value, i.e.,
    range_start <= longitude < range_start + 360

    The data array is rotated correspondingly around the dimension
    corresponding to the longitude coordinate.

    :param range_start: starting value of required longitude range
    """
    lon_coord = cube.coords(standard_name="longitude")
    if len(lon_coord) == 0:
        return
    lon_coord = lon_coord[0]
    lon_idx = cube.dim_coords.index(lon_coord)
    # Check if there are bounds which we will need to wrap as well
    roll_bounds = (lon_coord.bounds is not None) and (lon_coord.bounds.size != 0)
    idx1 = np.searchsorted(lon_coord.points, range_start)
    idx2 = np.searchsorted(lon_coord.points, range_start + 360.)
    shift = 0
    new_lon_points = None
    new_lon_bounds = None
    if 0 < idx1 < len(lon_coord.points):
        shift = -idx1
        lon_min = lon_coord.points[idx1]
        new_lon_points = np.roll(lon_coord.points, shift, 0)
        # Calculate which indices need 360 adding to them...
        indices_to_shift_value_of = new_lon_points < lon_min
        # ... then, add 360 to all those longitude values
        new_lon_points[indices_to_shift_value_of] += 360.0
        if roll_bounds:
            # If the coordinate has bounds then roll those as well
            new_lon_bounds = np.roll(lon_coord.bounds, shift, 0)
            # And shift all of the bounds (upper and lower) for those points which we had to shift. We can't do the
            # check independently because there may be cases where an upper or lower bound falls outside of the
            # 360 range, we leave those as they are to preserve monotonicity. See e.g.
            # test_set_longitude_bounds_wrap_at_360
            new_lon_bounds[indices_to_shift_value_of] += 360.0
    elif 0 < idx2 < len(lon_coord.points):
        shift = len(lon_coord.points) - idx2
        lon_max = lon_coord.points[idx2]
        new_lon_points = np.roll(lon_coord.points, shift, 0)
        indices_to_shift_value_of = new_lon_points >= lon_max
        new_lon_points[indices_to_shift_value_of] -= 360.0
        if roll_bounds:
            new_lon_bounds = np.roll(lon_coord.bounds, shift, 0)
            # See comment above re preserving monotinicity.
            new_lon_bounds[indices_to_shift_value_of] -= 360.0
    if shift != 0:
        # Ensure we also roll any auxilliary coordinates
        for aux_coord in cube.aux_coords:
            # Find all of the data dimensions which the auxiliary coordinate spans...
            dims = cube.coord_dims(aux_coord)
            # .. and check if longitude is one of those dimensions
            if lon_idx in dims:
                # Now roll the axis of the auxiliary coordinate which is associated with the longitude data
                # dimension: dims.index(lon_idx)
                new_points = np.roll(aux_coord.points, shift, dims.index(lon_idx))
                aux_coord.points = new_points
        # Now roll the data itcube
        new_data = np.roll(cube.data, shift, lon_idx)
        cube.data = new_data
        # Put the new coordinates back in their relevant places
        cube.dim_coords[lon_idx].points = new_lon_points
        if roll_bounds:
            cube.dim_coords[lon_idx].bounds = new_lon_bounds


def add_attributes(cube, attributes):
    """
    Add a variable attribute to this data
    :param attributes: Dictionary of attribute names (keys) and values.
    :return:
    """
    for key, value in list(attributes.items()):
        try:
            cube.attributes[key] = value
        except ValueError:
            try:
                setattr(cube, key, value)
            except ValueError as e:
                logging.warning("Could not set NetCDF attribute '%s' because %s" % (key, e.args[0]))
    # Record that this is a local (variable) attribute, not a global attribute
    cube._local_attributes.extend(list(attributes.keys()))


def remove_attribute(cube, key):
    """
    Remove a variable attribute to this data
    :param key: Attribute key to remove
    :return:
    """
    cube.attributes.pop(key, None)
    try:
        cube._local_attributes.remove(key)
    except ValueError:
        pass


def save_data(cube, output_file):
    """
    Save this data object to a given output file
    :param output_file: Output file to save to.
    """
    logging.info('Saving data to %s' % output_file)
    save_args = {'local_keys': cube._local_attributes}
    # If we have a time coordinate then use that as the unlimited dimension, otherwise don't have any
    if cube.coords('time'):
        save_args['unlimited_dimensions'] = ['time']
    else:
        iris.FUTURE.netcdf_no_unlimited = True
    iris.save(cube, output_file, **save_args)


def _get_default_plot_type(cube, lat_lon=False):
    if cube.ndim == 1:
        return 'line'
    elif cube.ndim ==2:
        return 'heatmap'
    else:
        raise ValueError("Unable to determine plot type for data with {} dimensions".format(cube.ndim))


def _collapse_gridded(data, coords, kernel):
    """
    Collapse a GriddedData or GriddedDataList based on the specified grids (currently only collapsing is available)
    :param GriddedData or GriddedDataList data: The data object to aggregate
    :param list of iris.coords.Coord or str coords: The coords to collapse
    :param str or iris.analysis.Aggregator kernel: The kernel to use in the aggregation
    :return:
    """
    from cis.aggregation.collapse_kernels import aggregation_kernels, MultiKernel
    from iris.analysis import Aggregator as IrisAggregator
    from cis.aggregation.gridded_collapsor import GriddedCollapsor
    from cis import __version__
    from cis.utils import listify

    # Ensure the coords are all Coord instances
    coords = [data._get_coord(c) for c in listify(coords)]

    # The kernel can be a string or object, so catch both defaults
    if kernel is None or kernel == '':
        kernel = 'moments'

    if isinstance(kernel, six.string_types):
        kernel_inst = aggregation_kernels[kernel]
    elif isinstance(kernel, (IrisAggregator, MultiKernel)):
        kernel_inst = kernel
    else:
        raise ValueError("Invalid kernel specified: " + str(kernel))

    aggregator = GriddedCollapsor(data, coords)
    data = aggregator(kernel_inst)

    history = "Collapsed using CIS version " + __version__ + \
              "\n variables: " + str(getattr(data, "var_name", "Unknown")) + \
              "\n from files: " + str(getattr(data, "filenames", "Unknown")) + \
              "\n over coordinates: " + ", ".join(c.name() for c in coords) + \
              "\n with kernel: " + str(kernel_inst) + "."
    data.add_history(history)

    return data


def _get_coord(cube, name):
    from cis.utils import standard_axes
    import cis.exceptions as cis_ex
    import iris.exceptions as iris_ex

    def _try_coord(data, coord_dict):
        try:
            coord = data.coord(**coord_dict)
        except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
            coord = None
        return coord

    coord = _try_coord(cube, dict(name_or_coord=name)) or _try_coord(cube, dict(standard_name=name)) \
        or _try_coord(cube, dict(standard_name=standard_axes.get(name.upper(), None))) or \
            _try_coord(cube, dict(var_name=name)) or _try_coord(cube, dict(axis=name))

    return coord