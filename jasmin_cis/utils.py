

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
    for char in string:
        if char in reserved_LaTeX_characters:
            new_string += "\\"
        new_string += char
    return new_string


def create_masked_array_for_missing_data(data, missing_val):
    import numpy.ma as ma
    return ma.array(data, mask=data==missing_val, fill_value=missing_val)


def unpack_data_object(data_object):
    '''
    @param data_object    A cube or an UngriddedData object
    @return A dictionary containing x, y and data as numpy arrays
    '''
    from iris.cube import Cube
    import iris.plot as iplt
    import iris
    from jasmin_cis.exceptions import CoordinateNotFoundError

    def __get_coord(axis, data_object):
        from iris.exceptions import CoordinateNotFoundError
        try:
            coord = data_object.coord(axis=axis)
            return coord.points
        except CoordinateNotFoundError:
            return None

    if type(data_object) is Cube:
        no_of_dims = len(data_object.shape)
        import numpy as np
        from mpl_toolkits.basemap import addcyclic

        plot_defn = iplt._get_plot_defn(data_object, iris.coords.POINT_MODE, ndims = no_of_dims)
        data = data_object.data #ndarray
        if plot_defn.transpose:
            data = data.T

        if no_of_dims == 1:
            x = __get_coord("x", data_object)
            y = __get_coord("y", data_object)

            if x is None and y is not None:
                x = data
                data = y
                y = None

        elif no_of_dims == 2:
            # Obtain U and V coordinates
            v_coord, u_coord = plot_defn.coords
            if u_coord:
                u = u_coord.points
            else:
                u = np.arange(data.shape[1])
            if v_coord:
                v = v_coord.points
            else:
                v = np.arange(data.shape[0])

        if plot_defn.transpose:
            u = u.T
            v = v.T

        if no_of_dims == 2:
            data, u = addcyclic(data, u)
            x, y = np.meshgrid(u, v)

        return { "data": data, "x" : x, "y" : y }
    else:
        try:
            return { "data": data_object.data, "x" : data_object.x.data, "y" : data_object.y.data }
        except CoordinateNotFoundError:
            return { "data": data_object.data, "x" : data_object.x.data}


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


def apply_intersection_mask_to_two_arrays(maskedarray1, maskedarray2):
    import numpy.ma as ma
    intersection_mask = ma.mask_or(maskedarray1.mask, maskedarray2.mask)
    maskedarray1 = ma.array(maskedarray1, mask = intersection_mask)
    maskedarray2 = ma.array(maskedarray2, mask = intersection_mask)

    return maskedarray1, maskedarray2