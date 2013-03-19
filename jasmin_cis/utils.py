import collections

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

def calculate_histogram_bin_edges(data, axis, user_range, step):
    '''
    @param data: A numpy array
    @param axis: The axis on which the data will be plotted. Set to "x" for histogram2d
    @param user_range: A dictionary containing the min and max values for the edges specified by the user. The data min and max is used if the user did not specify
    @param step: The distance between each bin edge/the width of each bin
    @return: An array containing a list of bin edges (i.e. when each bin starts and ends)
    '''
    from decimal import Decimal
    from numpy import array, append

    min_val = user_range.get(axis + "min", data.min())
    max_val = user_range.get(axis + "max", data.max())

    val_range = float(max_val - min_val)

    if step is None: step = val_range / 10.0

    x = float(Decimal(str(val_range)) % Decimal(str(step)))

    stop = max_val + step if  x < 1.e-7 else max_val # 1.e-7 is very close to 0

    bin_edges = array([])
    i = min_val
    while abs(i - stop) >= 1.e-7 and i < stop:
        bin_edges = append(bin_edges, (i))
        i += step

    return bin_edges

def expand_1d_to_2d_array(array_1d,length,axis=0):
    '''
    General utility routine to 'extend a 1D array into a 2D array
    by duplicating the data along a given 'axis' (default is 0)
    of size 'length'.

    Examples
    --------
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

    @param array_1d:
    @param length:
    @param axis:
    @return:
    '''
    import numpy as np

    if axis==0:
        array_2d = np.repeat(array_1d[np.newaxis,:],length,0)
    else:
        array_2d = np.repeat(array_1d[:,np.newaxis],length,1)

    return array_2d

def escape_latex_characters(string):
    reserved_LaTeX_characters = ["#", "$", "%", "^", "&", "_", "{", "}", "~", "\\"]
    new_string = ""
    if string is not None:
        for char in string:
            if char in reserved_LaTeX_characters:
                new_string += "\\"
            new_string += char
    return new_string


def create_masked_array_for_missing_data(data, missing_val):
    import numpy.ma as ma
    return ma.array(data, mask=data==missing_val, fill_value=missing_val)

def create_masked_array_for_missing_values(data, missing_values):
    import numpy.ma as ma

    mdata = data
    for missing_value in missing_values:
        mdata = ma.masked_where(missing_value==mdata,mdata)

    return mdata

def unpack_data_object(data_object, x_variable, y_variable):
    '''
    @param data_object    A cube or an UngriddedData object
    @return A dictionary containing x, y and data as numpy arrays
    '''
    from iris.cube import Cube
    import iris.plot as iplt
    import iris
    from jasmin_cis.exceptions import CoordinateNotFoundError

    def __get_coord(data_object, variable):
        from iris.exceptions import CoordinateNotFoundError
        try:
            coord = data_object.coord(name=variable)
            return coord.points
        except CoordinateNotFoundError:
            return None

    data = data_object.data #ndarray

    if type(data_object) is Cube:
        no_of_dims = len(data_object.shape)
        import numpy as np
        from mpl_toolkits.basemap import addcyclic

        plot_defn = iplt._get_plot_defn(data_object, iris.coords.POINT_MODE, ndims = no_of_dims)
        if plot_defn.transpose:
            data = data.T

        if x_variable != data_object.name():
            x = __get_coord(data_object, x_variable)
            y = __get_coord(data_object, y_variable)
        else:
            x = data
            data = __get_coord(data_object, y_variable)
            y = None



        if plot_defn.transpose:
            x = x.T
            y = y.T

        if no_of_dims == 2:
            try:
                data, x = addcyclic(data, x)
                x, y = np.meshgrid(x, y)
            except:
                data, y = addcyclic(data, y)
                y, x = np.meshgrid(y, x)

        return { "data": data, "x" : x, "y" : y }
    else:
        if x_variable == data_object.name():
            return {"data" : data_object.coord(name=y_variable).data, "x" : data}
        else:
            try:
                x = data_object.coord(name=x_variable)
                y = data_object.coord(name=y_variable)
                return { "data": data, "x" : data_object.coord(name=x_variable).data, "y" : data_object.coord(name=y_variable).data }
            except CoordinateNotFoundError:
                return { "data": data, "x" : data_object.coord(name=x_variable).data }


def copy_attributes(source, dest):
    '''
     Copy all attributes from one object to another
    @param source: Object to copy attributes from
    @param dest: Object to copy attributes to
    @return: None
    '''
    if source:
        if isinstance(source, dict):
            dest.__dict__.update(source)
        else:
            dest.__dict__.update(source.__dict__)


def add_file_prefix(prefix, filepath):
    '''
        Add a prefix to a filename taking into account any path that might be present before that actual filename
    @param prefix: A string to prefix the filename with
    @param filepath: Filename, optionally including path
    @return: A string with the full path to the prefixed file
    '''
    import os.path
    filename = os.path.basename(filepath)
    path = os.path.dirname(filepath)
    return os.path.join(path,prefix+filename)


def parse_key_val_string(arguments, seperator):
    '''
        Takes a (comma) seperated list of keyword value pairs (seperated by =) and returns a dictionary with those keys and values
    @param arguments: A string which is a seperated list of keyword value pairs
    @param seperator: String which is used to split the string into a list
    @return: A dictionary of the keywords and values
    '''
    input_list = arguments.split(seperator)
    return parse_key_val_list(input_list)


def parse_key_val_list(input_list):
    '''
     Takes list of keyword value strings (seperated by =) and returns a dictionary with those keys and values
        NOTE - if a key has no value, the key is stored and given the value True
    @param input_list: A list of strings which are keyword value pairs seperated by =
    @return: A dictionary of the keywords and values
    '''
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
    '''
        Ensure two (optionally) masked arrays have the same mask.
        If both arrays are masked the intersection of the masks is used.
        If one array is masked and the other is not, the mask from the masked array is applied
          to the unmasked array
        If neither array is masked then both arrays are returned as masked arrays with an empty mask
    @param array1: An (optionally masked) array
    @param array2: Another (optionally masked) array
    @return: Two masked arrays with a common mask
    '''
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

    array1 = ma.array(array1, mask = intersection_mask)
    array2 = ma.array(array2, mask = intersection_mask)

    return array1, array2
