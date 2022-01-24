import collections.abc
import re
import logging
import warnings
import numpy as np
from cis.exceptions import InvalidCommandLineOptionError
import contextlib


# number of bytes in a MB
BYTES_IN_A_MB = 1048576.0


def add_element_to_list_in_dict(my_dict, key, value):
    try:
        my_dict[key].append(value)
    except KeyError:
        my_dict[key] = [value]


def concatenate(arrays, axis=0):
    """
    Concatenate a list of numpy arrays into one larger array along the axis specified (the default axis is zero). If any
    of the arrays are masked arrays then the returned array will be a masked array with the correct mask, otherwise a
    numpy array is returned.

    :param arrays: A list of numpy arrays (masked or not)
    :param axis: The axis along which to concatenate (the default is 0)
    :return: The concatenated array
    """
    from numpy.ma import MaskedArray
    if any(isinstance(array, MaskedArray) for array in arrays):
        from numpy.ma import concatenate
    else:
        from numpy import concatenate

    res = arrays[0]

    if len(arrays) > 1:
        for array in arrays[1:]:
            res = concatenate((res, array), axis)

    return res


def calculate_histogram_bin_edges(data, axis, user_min, user_max, step, log_scale=False):
    """
    :param data: A numpy array
    :param axis: The axis on which the data will be plotted. Set to "x" for histogram2d
    :param user_range: A dictionary containing the min and max values for the edges specified by the user. The data min
     and max is used if the user did not specify
    :param step: The distance between each bin edge/the width of each bin
    :return: An array containing a list of bin edges (i.e. when each bin starts and ends)
    """
    from decimal import Decimal
    from numpy import array, append, logspace, log10
    import logging
    import sys

    min_val = user_min or data.min()
    max_val = user_max or data.max()

    val_range = float(max_val - min_val)

    if step is None:
        step = val_range / 10.0
        user_specified_step = False
    else:
        user_specified_step = True

    x = float(Decimal(str(val_range)) % Decimal(str(step)))

    stop = max_val + step if x < 1.e-7 else max_val  # 1.e-7 is very close to 0

    bin_edges = array([])
    i = min_val
    if not log_scale or user_specified_step:
        while abs(i - stop) >= sys.float_info.min and i < stop:
            if not user_specified_step and len(bin_edges) == 11:
                break
            bin_edges = append(bin_edges, i)

            i += step
    else:
        if min_val < 0 or max_val < 0:
            raise ValueError('Error, log axis specified but data minimum is less than 0. Please either use a linear'
                             'axis or specify an axis minimum greater than 0.')
        bin_edges = logspace(log10(min_val), log10(stop), num=11)

    logging.debug(axis + " axis bin edges: " + str(bin_edges))
    return bin_edges


def expand_1d_to_2d_array(array, length, axis=0):
    """
    General utility routine to 'extend arbitrary dimensional array into a higher dimension
    by duplicating the data along a given 'axis' (default is 0) of size 'length'.

    Examples::

        >>> a = np.array([1, 2, 3, 4])
        >>> expand_1d_to_2d_array(a, 4, axis=0)
        [[1 2 3 4]
         [1 2 3 4]
         [1 2 3 4]
         [1 2 3 4]]

        >>> a = np.array([1, 2, 3, 4])
        >>> expand_1d_to_2d_array(a, 4, axis=1)
        [[1 1 1 1]
         [2 2 2 2]
         [3 3 3 3]
         [4 4 4 4]]

    :param array:
    :param length:
    :param axis:
    :return:
    """
    from numpy.ma import MaskedArray

    if axis == 0:
        new_shape = (length, array.size)
        reshaped = array
    else:
        new_shape = (array.size, length)
        reshaped = array.reshape(array.size, 1)

    array_2d = np.broadcast_to(reshaped, new_shape, subok=True)

    # Broadcast the mask too (this gets lost otherwise)
    if isinstance(array, MaskedArray):
        array_2d.mask = np.broadcast_to(reshaped.mask, new_shape)

    return array_2d


def create_masked_array_for_missing_data(data, missing_val):
    import numpy.ma as ma
    return ma.array(data, mask=data == missing_val, fill_value=missing_val)


def create_masked_array_for_missing_values(data, missing_values):
    import numpy.ma as ma

    mdata = data
    for missing_value in missing_values:
        if missing_value is not None:
            mdata = ma.masked_where(missing_value == mdata, mdata)

    return mdata


def apply_mask_to_numpy_array(in_array, mask):
    """Element-wise ORs the mask with the mask of the array.
    If the mask masks no elements, no change is made. If the array is not masked, it is converted to a masked array.

    :param in_array: input array
    :type in_array: numpy array or masked array
    :param mask: mask
    :type mask: numpy array of boolean
    """
    import numpy as np

    if mask is not np.ma.nomask and np.any(mask):
        out_array = np.ma.asarray(in_array)
        out_array.mask = out_array.mask | mask
    else:
        out_array = in_array
    return out_array


def array_equal_including_nan(array1, array2):
    """
    :param array1: A numpy array
    :param array2: Another numpy array (can be of a different shape)
    :return: True or false if the arrays are equal, including NaNs.
    """
    import numpy

    try:
        if array1.shape != array2.shape:
            return False
        else:
            for i, j in numpy.nditer([array1, array2]):
                if i != i:
                    pass
                elif i != j:
                    return False
    except AttributeError:
        return False

    return True


def get_coord(data_object, variable, data):
    """
    Find a specified coord

    :param data_object:
    :param variable:
    :param data:
    :return:
    """
    from iris.exceptions import CoordinateNotFoundError
    if variable in [data_object.name(), data_object.standard_name, data_object.long_name, 'default']:
        return data
    else:
        if variable.startswith("search:"):
            number_of_points = float(variable.split(":")[1])
            for coord in data_object.coords():
                if coord.shape[0] == number_of_points:
                    break
        else:
            try:
                coord = data_object.coord(variable)
            except CoordinateNotFoundError:
                return None
        return coord


def fix_longitude_range(lons, range_start):
    """Shifts longitude values by +/- 360 to fit within a 360 degree range starting at a specified value.
    It is assumed that a no shifts larger than 360 are needed.

    :param lons: numpy array of longitude values
    :param range_start: longitude at start of 360 degree range into which values are required to fit
    :return: array of fixed longitudes
    """
    from iris.analysis.cartography import wrap_lons
    return wrap_lons(lons, range_start, 360)


def find_longitude_wrap_start(packed_data_item):
    """
    ONLY WORK OUT THE WRAP START OF THE DATA
    :param packed_data_item:
    :return:
    """
    from iris.exceptions import CoordinateNotFoundError
    try:
        x_points_min = packed_data_item.coord(standard_name='longitude').points.min()
    except CoordinateNotFoundError:
        x_wrap_start = None
    else:
        x_wrap_start = -180 if x_points_min < 0 else 0

    return x_wrap_start


def wrap_longitude_coordinate_values(x_min, x_max):
    if x_min > x_max:
        if x_min >= 180:
            x_min -= 360
        else:
            x_max += 360

    return x_min, x_max


def copy_attributes(source, dest):
    """
    Copy all attributes from one object to another

    :param source: Object to copy attributes from
    :param dest: Object to copy attributes to
    :return: None
    """
    if source:
        if isinstance(source, dict):
            dest.__dict__.update(source)
        else:
            dest.__dict__.update(source.__dict__)


def parse_key_val_string(arguments, separator):
    """
    Takes a (comma) separated list of keyword value pairs (separated by =) and returns a dictionary with those keys and
    values

    :param arguments: A string which is a separated list of keyword value pairs
    :param separator: String which is used to split the string into a list
    :return: A dictionary of the keywords and values
    """
    input_list = arguments.split(separator)
    return parse_key_val_list(input_list)


def parse_key_val_list(input_list):
    """
     Takes list of keyword value strings (seperated by =) and returns a dictionary with those keys and values
     **NOTE** if a key has no value, the key is stored and given the value True

    :param input_list: A list of strings which are keyword value pairs separated by =
    :return: A dictionary of the keywords and values
    """
    key_val_dict = {}
    for element in input_list:
        key_value = element.split('=')
        key = key_value[0]
        value = key_value[1] if len(key_value) > 1 else True
        key_val_dict[key] = value

    return key_val_dict


def haversine(lat, lon, lat2, lon2):
    """
    Computes the Haversine distance between two points
    """
    import math
    R_E = 6378  # Radius of the earth in km
    lat1 = math.radians(lat)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon)
    lon2 = math.radians(lon2)
    arclen = 2 * math.asin(math.sqrt(
        (math.sin((lat2 - lat1) / 2)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2 - lon1) / 2)) ** 2))
    return arclen * R_E


class OrderedSet(collections.abc.MutableSet):
    """
    From http://code.activestate.com/recipes/576694/
    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]  # sentinel node for doubly linked list
        self.map = {}  # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


def apply_intersection_mask_to_two_arrays(array1, array2):
    """
    Ensure two (optionally) masked arrays have the same mask.
    If both arrays are masked the intersection of the masks is used.
    If one array is masked and the other is not, the mask from the masked array is applied to the unmasked array.
    If neither array is masked then both arrays are returned as masked arrays with an empty mask.

    :param array1: An (optionally masked) array
    :param array2: Another (optionally masked) array
    :return: Two masked arrays with a common mask
    """
    import numpy.ma as ma
    mask1 = ma.getmaskarray(array1)
    mask2 = ma.getmaskarray(array2)
    # a new masked array combines the masks and preserves the originals
    return ma.masked_array(array1, mask2), ma.masked_array(array2, mask1)


def index_iterator_nditer(shape, points):
    """Iterates over the indexes of a multi-dimensional array of a specified shape.
    The last index changes most rapidly.

    :param shape: sequence of array dimensions
    :return: yields tuples of array indexes
    """

    num_cells = np.product(shape)
    cell_count = 0
    cell_total = 0

    it = np.nditer(points, flags=['multi_index'])
    while not it.finished:
        yield it.multi_index

        # Log progress periodically.
        if cell_count == 10000:
            cell_total += 1
            number_cells_processed = cell_total * 10000
            logging.info("    Processed %d points of %d (%d%%)", number_cells_processed, num_cells,
                         int(number_cells_processed * 100 / num_cells))
            cell_count = 0
        cell_count += 1

        it.iternext()


def index_iterator(shape):
    """Iterates over the indexes of a multi-dimensional array of a specified shape.
    The last index changes most rapidly.

    :param shape: sequence of array dimensions
    :return: yields tuples of array indexes
    """
    dim = len(shape)
    idx = [0] * dim
    num_iterations = 1
    for j in range(0, dim):
        num_iterations *= shape[j]

    for iterations in range(num_iterations):
        yield tuple(idx)
        for j in range(dim - 1, -1, -1):
            idx[j] += 1
            if idx[j] < shape[j]:
                break
            idx[j] = 0


def index_iterator_for_non_masked_data(shape, points):
    """Iterates over the indexes of a multi-dimensional array of a specified shape.
    The last index changes most rapidly.

    :param shape: sequence of array dimensions
    :return: yields tuples of array indexes
    """

    # dim = len(shape)
    # idx = [0] * dim
    # num_iterations = 1
    # for j in range(0, dim):
    #     num_iterations *= shape[j]
    num_cells = np.product(shape)
    cell_count = 0
    cell_total = 0

    it = np.nditer(points.data, flags=['multi_index'])
    while not it.finished:
        if it[0] is not np.ma.masked:
            yield it.multi_index

        it.iternext()

        # Log progress periodically.
        if cell_count == 10000:
            cell_total += 1
            number_cells_processed = cell_total * 10000
            logging.info("    Processed %d points of %d (%d%%)", number_cells_processed, num_cells,
                         int(number_cells_processed * 100 / num_cells))
            cell_count = 0
        cell_count += 1


def parse_distance_with_units_to_float_km(distance):
    """Parse a string such as '10km' or '1.0e3m' to a distance in km

    :param distance: string to parse
    :return: A distance in km
    """
    measurement = split_into_float_and_units(distance)
    distance_in_km = measurement['value']
    if measurement['units'] == 'm':
        distance_in_km /= 1000.0
    elif measurement['units'] == 'km' or measurement['units'] is None:
        pass
    else:
        raise InvalidCommandLineOptionError("Units not recognised", measurement['units'])

    return distance_in_km


def parse_distance_with_units_to_float_m(distance):
    """Parse a string such as '10km' or '1.0e3m' to a distance in m

    :param distance: string to parse
    :return: A distance in m
    """
    measurement = split_into_float_and_units(distance)
    if measurement['units'] is None:
        return measurement['value']
    else:
        return parse_distance_with_units_to_float_km(distance) * 1000.0


def split_into_float_and_units(measurement):
    """Split a string such as '1000m' or '1.0e3' to a value and, optionally, units

    :param distance: string to parse
    :return: A distance in m
    """

    # Convert to a string, just in case the number comes in as something else
    measurement = str(measurement)

    # First find any numbers that match the float type, e.g. 1, 1.2, 12e3
    measurement_value = re.findall(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?', measurement)

    # Check for 1 and only 1 value found
    if len(measurement_value) > 1:
        raise InvalidCommandLineOptionError("More than one number found")
    elif len(measurement_value) == 0:
        raise InvalidCommandLineOptionError("No numbers found")

    # Remove number from string, so floats such as 1e3 do not have the e confused for a unit
    measurement = measurement.replace(measurement_value[0], " ")

    # Match any strings of characters, which should be units
    measurement_units = re.findall(r'[a-zA-z]+', measurement)

    if len(measurement_units) > 1:
        raise InvalidCommandLineOptionError("More than one unit found")
    elif len(measurement_units) == 0:
        measurement_units = [None]

    return {'value': float(measurement_value[0]), 'units': measurement_units[0]}


def get_class_name(cls):
    """Returns the qualified class name of a class.

    :param cls: class
    :return: class name
    """
    return cls.__module__ + '.' + cls.__name__


def isnan(number):
    return number != number

standard_names = {'longitude': 'X', 'grid_longitude': 'X', 'projection_x_coordinate': 'X',
                  'latitude': 'Y', 'grid_latitude': 'Y', 'projection_y_coordinate': 'Y',
                  'altitude': 'Z', 'time': 'T', 'air_pressure': 'P'}

# The standard axes lookup is just the inverse of the standard names with the less likely options removed to preserve
# a one to one mapping
standard_axes = {'X': 'longitude', 'Y': 'latitude', 'Z': 'altitude', 'T': 'time', 'P': 'air_pressure'}


def guess_coord_axis(coord):
    """Returns X, Y, Z or T corresponding to longitude, latitude,
    altitude or time respectively if the coordinate can be determined
    to be one of these (based on the standard name only, in this implementation).

    This is intended to be similar to iris.util.guess_coord_axis.
    """
    import iris
    # TODO Can more be done for ungridded based on units, as with iris.util.guess_coord_axis?
    guessed_axis = None
    if isinstance(coord, iris.coords.Coord):
        guessed_axis = iris.util.guess_coord_axis(coord)
    elif coord.standard_name is not None:
        guessed_axis = standard_names.get(coord.standard_name.lower())
    return guessed_axis


def add_to_list_if_not_none(item, list):
    """
    Add a value to a list if it is not None

    :param item: the item to add
    :param list: the list to append it to
    :return: nothing
    """
    if item is not None:
        list.append(item)


def dimensions_compatible(dimensions, other_dimensions):
    """
    Check to see if two dimensions share the same common coordinates. Note that this will only compare the dimensions
    up to the length of the shortest list.

    :param dimensions: dimension list
    :param other_dimensions: other dimension list
    """

    for dim, other_dim in zip(dimensions, other_dimensions):
        if not dim == other_dim:
            return False
    return True


def set_standard_name_if_valid(data, standard_name):
    """
    Set a data object's standard name if it is a valid CF compliant name, otherwise set it to None

    :param CommonData or Metadata data: Data to set standard name on
    :param standard_name: Standard name to set
    :return:
    """
    try:
        data.standard_name = standard_name
    except ValueError:
        logging.info("Not setting standard name '{}' as it is not CF compliant.".format(standard_name))
        data.standard_name = None


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Taken from http://code.activestate.com/recipes/391367-deprecated/
    """

    def newFunc(*args, **kwargs):
        def log_warning(message, category, filename, lineno, file=None):
            logging.warning('%s:%s %s:%s' % (category.__name__, message, filename, lineno))

        warnings.showwarning = log_warning
        warnings.simplefilter('once', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


def listify(item):
    """
    If item is not a list, return it as a list

    :param item: Item which may or may not be a list
    :return: List
    """
    from types import GeneratorType
    if isinstance(item, (tuple, GeneratorType)):
        return list(item)
    if not isinstance(item, list):
        return [item]
    return item


def log_memory_profile(location):
    """
    Write the total memory to the log as debug message

    :param location: location in the program where the memory measurement was taken
    :return: nothing
    """
    try:
        import psutil
        mem = psutil.Process().memory_info().rss / BYTES_IN_A_MB
        logging.debug("App Memory MB ({}): {}".format(location, mem))
    except ImportError:
        pass


def move_item_to_end(iter, item):
    """
    Move an item in an iterable to the end of a list
    :param iterable iter: iterable container (list or tuple) contianing item
    :param item: item to move to end
    :return list: rearranged list
    """
    if not isinstance(iter, list):
        iter = list(iter)
    dim = iter.pop(iter.index(item))
    iter.append(dim)
    return iter


@contextlib.contextmanager
def demote_warnings(level=logging.INFO):
    import warnings
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        yield
        for w in ws:
            logging.log(level, w.message)


@contextlib.contextmanager
def single_warnings_only():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("once")
        yield


def squeeze(data):
    from iris.cube import Cube
    from iris.util import squeeze
    from cis.data_io.gridded_data import make_from_cube
    if isinstance(data, Cube):
        return make_from_cube(squeeze(data))
    else:
        return data


@contextlib.contextmanager
def no_autoscale(ax):
    # Turn the scaling off so that we don't change the limits by doing whatever we do next
    ax.set_autoscale_on(False)
    yield
    # Turn scaling back on
    ax.set_autoscale_on(True)
