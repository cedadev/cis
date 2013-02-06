

def add_element_to_list_in_dict(my_dict,key,value):
    try:
        my_dict[key].append(value)
    except KeyError:
        my_dict[key] = [value]


def concatenate(list_of_arrays, get_data):
    import numpy as np
    array = get_data(list_of_arrays[0])
    if len(list_of_arrays) > 1:
        for sds in list_of_arrays[1:]:
            array = np.concatenate((array,get_data(sds)),axis=0)
    return array

