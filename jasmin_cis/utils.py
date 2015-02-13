import collections
import re
import logging
import warnings
import iris
from iris.exceptions import CoordinateNotFoundError
import numpy as np
from jasmin_cis.exceptions import InvalidCommandLineOptionError


def add_element_to_list_in_dict(my_dict,key,value):
    try:
        my_dict[key].append(value)
    except KeyError:
        my_dict[key] = [value]


def concatenate(arrays, axis=0):
    from numpy.ma import MaskedArray
    from numpy import ndarray
    if isinstance(arrays[0], MaskedArray):
        from numpy.ma import concatenate
    elif isinstance(arrays[0], ndarray):
        from numpy import concatenate

    res = arrays[0]

    if len(arrays) > 1:
        for array in arrays[1:]:
            res = concatenate((res,array),axis)

    return res

def calculate_histogram_bin_edges(data, axis, user_range, step, log_scale = False):
    '''
    :param data: A numpy array
    :param axis: The axis on which the data will be plotted. Set to "x" for histogram2d
    :param user_range: A dictionary containing the min and max values for the edges specified by the user. The data min and max is used if the user did not specify
    :param step: The distance between each bin edge/the width of each bin
    :return: An array containing a list of bin edges (i.e. when each bin starts and ends)
    '''
    from decimal import Decimal
    from numpy import array, append, logspace, log10
    import logging
    import sys

    min_val = user_range.get(axis + "min", data.min())
    max_val = user_range.get(axis + "max", data.max())

    val_range = float(max_val - min_val)

    if step is None:
        step = val_range / 10.0
        user_specified_step = False
    else:
        user_specified_step = True

    x = float(Decimal(str(val_range)) % Decimal(str(step)))

    stop = max_val + step if  x < 1.e-7 else max_val # 1.e-7 is very close to 0

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


def expand_1d_to_2d_array(array_1d,length,axis=0):
    """
    General utility routine to 'extend a 1D array into a 2D array
    by duplicating the data along a given 'axis' (default is 0)
    of size 'length'.

    **Examples**

    >>> a = np.array([1,2,3,4])
    >>> expand_1d_to_2d_array(a, 4, axis=0)
    [[1 2 3 4]
     [1 2 3 4]
     [1 2 3 4]
     [1 2 3 4]]

    >>> a = np.array([1,2,3,4])
    >>> expand_1d_to_2d_array(a, 4, axis=1)
    [[1 1 1 1]
     [2 2 2 2]
     [3 3 3 3]
     [4 4 4 4]]

    :param array_1d:
    :param length:
    :param axis:
    :return:
    """
    import numpy as np

    if axis==0:
        array_2d = np.repeat(array_1d[np.newaxis,:],length,0)
    else:
        array_2d = np.repeat(array_1d[:,np.newaxis],length,1)

    return array_2d

def create_masked_array_for_missing_data(data, missing_val):
    import numpy.ma as ma
    return ma.array(data, mask=data==missing_val, fill_value=missing_val)

def create_masked_array_for_missing_values(data, missing_values):
    import numpy.ma as ma

    mdata = data
    for missing_value in missing_values:
        mdata = ma.masked_where(missing_value==mdata,mdata)

    return mdata


def apply_mask_to_numpy_array(in_array, mask):
    """Elementwise ORs the mask with the mask of the array.

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
    :return: True or false if the arrays are equal, inclduing NaNs.
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


def unpack_data_object(data_object, x_variable, y_variable, x_wrap_start):
    '''
    :param data_object    A cube or an UngriddedData object
    :return: A dictionary containing x, y and data as numpy arrays
    '''
    from iris.cube import Cube
    import iris.plot as iplt
    import iris
    import logging
    from mpl_toolkits.basemap import addcyclic

    def __get_coord(data_object, variable, data):

        if variable == data_object.name() or variable == "default" or variable == data_object.standard_name or \
           variable == data_object.long_name:
            return data
        else:
            if variable.startswith("search:"):
                number_of_points = float(variable.split(":")[1])
                for coord in data_object.coords():
                    if coord.shape[0] == number_of_points:
                        break
            else:
                try:
                    coord = data_object.coord(name=variable)
                except CoordinateNotFoundError:
                    return None
            if isinstance(data_object, Cube):
                return coord.points
            else:
                return coord.data

    no_of_dims = len(data_object.shape)

    data = data_object.data #ndarray

    x = __get_coord(data_object, x_variable, data)
    try:
        coord = data_object.coord(name=x_variable)
        x_axis_name = guess_coord_axis(coord)
    except CoordinateNotFoundError:
        x_axis_name = None

    y = __get_coord(data_object, y_variable, data)

    # Must use special function to check equality of array here, so NaNs are returned as equal and False is returned if
    # arrays have a diffent shape
    if array_equal_including_nan(y, data) or array_equal_including_nan(y, x):
        y = None

    if array_equal_including_nan(x, data):
        data = y
        y = None

    if isinstance(data_object, Cube):
        plot_defn = iplt._get_plot_defn(data_object, iris.coords.POINT_MODE, ndims = no_of_dims)
        if plot_defn.transpose:
            data = data.T
            x = x.T
            y = y.T

        # Check for auxillary coordinates.
        aux_coords = False
        for coord in data_object[0].coords(dim_coords=False):
            aux_coords = True

        if no_of_dims == 2:
            # If we have found some auxillary coordinates in the data and the shape of x data or y data is the same as
            # data assume wehave a hybrid coordinate (which is two dimensional b nature. Perhaps need a more robust
            # method for detecting this.
            if aux_coords and (data.shape == x.shape or data.shape == y.shape):
                # Work out which set of data needs expanding to match the coordinates of the others. Note there can only
                # ever be one hybrid coordinate axis.
                if y.shape == data.shape:
                    if y[:, 0].shape == x.shape:
                        x, _y = np.meshgrid(x, y[0, :])
                    elif y[0, :].shape == x.shape:
                        x, _y = np.meshgrid(x, y[:, 0])
                elif x.shape == data.shape:
                    if x[:, 0].shape == y.shape:
                        y, _x = np.meshgrid(y, x[0, :])
                    elif x[0, :].shape == y.shape:
                        y, _x = np.meshgrid(y, x[:, 0])
            else:
                try:
                    data, x = addcyclic(data, x)
                    x, y = np.meshgrid(x, y)
                except:
                    data, y = addcyclic(data, y)
                    y, x = np.meshgrid(y, x)

    if x_axis_name == 'X' and x_wrap_start is not None:
        #x = iris.analysis.cartography.wrap_lons(x, x_wrap_start, 360)
        if isnan(x_wrap_start):
            raise InvalidCommandLineOptionError('Overall range for longitude axis must be within 0 - 360 degrees.')
        x = fix_longitude_range(x, x_wrap_start)

    logging.debug("Shape of x: " + str(x.shape))
    if y is not None: logging.debug("Shape of y: " + str(y.shape))
    logging.debug("Shape of data: " + str(data.shape))

    return { "data": data, "x" : x, "y" : y }


def fix_longitude_range(lons, range_start):
    """Shifts longitude values by +/- 360 to fit within a 360 degree range starting at a specified value.

    It is assumed that a no shifts larger than 360 are needed.
    :param lons: numpy array of longitude values
    :param range_start: longitude at start of 360 degree range into which values are required to fit
    :return: array of fixed longitudes
    """
    range_end = range_start + 360
    fixed_lons = np.ma.array(lons, copy=True)

    fixed_lons[fixed_lons < range_start] += 360
    fixed_lons[fixed_lons >= range_end] -= 360

    return fixed_lons


def find_longitude_wrap_start(x_variable, x_range, packed_data_items):
    if x_range is not None:
        x_min = x_range.get('xmin')
        x_max = x_range.get('xmax')
    else:
        x_min = None
        x_max = None

    x_wrap_start = None
    x_points_mins = []
    x_points_maxs = []
    for data_object in packed_data_items:
        try:
            coord = data_object.coord(name=x_variable)
            x_axis_name = guess_coord_axis(coord)
        except CoordinateNotFoundError:
            x_axis_name = None
        if x_axis_name == 'X':
            x_points_mins.append(np.min(coord.points))
            x_points_maxs.append(np.max(coord.points))

    if len(x_points_mins) > 0:
        x_points_min = min(x_points_mins)
        x_points_max = max(x_points_maxs)

        x_wrap_start = x_points_min
        if x_min is not None or x_max is not None:
            if x_min is not None and x_max is not None:
                if abs(x_max - x_min) > 360:
                    return float('NaN')
            elif x_min is None and x_max < x_points_min:
                raise InvalidCommandLineOptionError(
                    'If specifying xmin only it must be within the original coordinate range. Please specify xmax too.')
            elif x_max is None and x_min > x_points_max:
                raise InvalidCommandLineOptionError(
                    'If specifying xmax only it must be within the original coordinate range. Please specify xmin too.')
            if x_min is not None and x_min < x_points_min:
                x_wrap_start = x_min
            elif x_max is not None and x_max > x_points_max:
                x_wrap_start = x_max - 360
    return x_wrap_start


def wrap_longitude_coordinate_values(x_min, x_max):
    if x_min > x_max:
        if x_min >= 180:
            x_min -= 360
        else:
            x_max += 360

    return x_min, x_max


def copy_attributes(source, dest):
    '''
    Copy all attributes from one object to another

    :param source: Object to copy attributes from
    :param dest: Object to copy attributes to
    :return: None
    '''
    if source:
        if isinstance(source, dict):
            dest.__dict__.update(source)
        else:
            dest.__dict__.update(source.__dict__)


def add_file_prefix(prefix, filepath):
    '''
    Add a prefix to a filename taking into account any path that might be present before that actual filename

    :param prefix: A string to prefix the filename with
    :param filepath: Filename, optionally including path
    :return: A string with the full path to the prefixed file
    '''
    import os.path
    filename = os.path.basename(filepath)
    path = os.path.dirname(filepath)
    return os.path.join(path,prefix+filename)


def remove_file_prefix(prefix, filepath):
    """
    Remove a prefix from a filename, taking into account any path that might be present before that actual filename
    :param prefix: The prefix to remove
    :param filepath: Filename, optionall including path
    :return: A sring with the full path to the unprefixed file
    """
    import os.path

    filename = os.path.basename(filepath)
    path = os.path.dirname(filepath)

    filename = filename.replace(prefix, '', 1)

    return os.path.join(path, filename)


def parse_key_val_string(arguments, separator):
    """
    Takes a (comma) seperated list of keyword value pairs (seperated by =) and returns a dictionary with those keys and
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
    '''
        Computes the Haversine distance between two points
    '''
    import math
    R_E = 6378 # Radius of the earth in km
    lat1 = math.radians(lat)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon)
    lon2 = math.radians(lon2)
    arclen = 2*math.asin(math.sqrt((math.sin((lat2-lat1)/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2-lon1)/2))**2))
    return arclen*R_E

class OrderedSet(collections.MutableSet):
    '''
    From http://code.activestate.com/recipes/576694/
    '''

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
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
    If one array is masked and the other is not, the mask from the masked array is applied to the unmasked array
    If neither array is masked then both arrays are returned as masked arrays with an empty mask

    :param array1: An (optionally masked) array
    :param array2: Another (optionally masked) array
    :return: Two masked arrays with a common mask
    """

    import numpy.ma as ma
    if isinstance(array1, ma.MaskedArray):
        if isinstance(array2, ma.MaskedArray):
            intersection_mask = ma.mask_or(array1.mask, array2.mask)
        else:
            intersection_mask = array1.mask
    else:
        if isinstance(array2, ma.MaskedArray):
            intersection_mask = array2.mask
        else:
            intersection_mask = False

    array1 = ma.array(array1, mask=intersection_mask)
    array2 = ma.array(array2, mask=intersection_mask)

    return array1, array2


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
        return parse_distance_with_units_to_float_km(distance)*1000.0


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


def guess_coord_axis(coord):
    """Returns X, Y, Z or T corresponding to longitude, latitude,
    altitude or time respectively if the coordinate can be determined
    to be one of these (based on the standard name only, in this implementation).

    This is intended to be similar to iris.util.guess_coord_axis.
    """
    #TODO Can more be done for ungridded based on units, as with iris.util.guess_coord_axis?
    standard_names = {'longitude': 'X', 'grid_longitude': 'X', 'projection_x_coordinate': 'X',
                      'latitude': 'Y', 'grid_latitude': 'Y', 'projection_y_coordinate': 'Y',
                      'altitude': 'Z', 'time': 'T', 'air_pressure': 'P'}
    if isinstance(coord, iris.coords.Coord):
        guessed_axis = iris.util.guess_coord_axis(coord)
    else:
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


def dimensions_equal(dimensions, other_dimensions):
    """
    Check to see if two dimensions are the same (contain the same variables in the same order)
    :param dimensions: dimension list
    :param other_dimensions: other dimension list
    """

    if len(dimensions) is not len(other_dimensions):
        return False
    for dim, other_dim in zip(dimensions, other_dimensions):
        if not dim == other_dim:
            return False
    return True


def set_cube_standard_name_if_valid(cube, standard_name):
    """
    Set a cube's standard name if it is a valid CF compliant name, otherwise set it to None
    :param cube: Cube to set standard name on
    :param standard_name: Standard name to set
    :return:
    """
    try:
        cube.standard_name = standard_name
    except ValueError:
        # If the standard name is not valid CF compliant standard name
        cube.standard_name = None


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
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
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
    if not isinstance(item, list):
        return [item]
    return item