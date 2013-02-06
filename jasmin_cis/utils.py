

def add_element_to_list_in_dict(my_dict,key,value):
    try:
        my_dict[key].append(value)
    except KeyError:
        my_dict[key] = [value]


def concatenate(arrays):
    import numpy as np

    res = arrays[0]

    if len(arrays) > 1:
        for array in arrays[1:]:
            res = np.concatenate((res,array),axis=0)

    return res


