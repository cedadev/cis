

def add_element_to_list_in_dict(my_dict,key,value):
    try:
        my_dict[key].append(value)
    except KeyError:
        my_dict[key] = [value]


def concatenate(arrays, axis=0):
    import numpy as np

    res = arrays[0]

    if len(arrays) > 1:
        for array in arrays[1:]:
            res = np.concatenate((res,array),axis)

    return res

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

    if type(data_object) is Cube:
        no_of_dims = len(data_object.shape)
        import numpy as np
        from mpl_toolkits.basemap import addcyclic

        plot_defn = iplt._get_plot_defn(data_object, iris.coords.POINT_MODE, ndims = no_of_dims)
        data = data_object.data #ndarray
        if plot_defn.transpose:
            data = data.T

        if no_of_dims == 1:
            u_coord, = plot_defn.coords
            if u_coord:
                x = u_coord.points
            else:
                x = np.arange(data.shape[0])
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
        return { "data": data_object.data, "x" : data_object.x, "y" : data_object.y }