"""
Routines for the info command
"""


def info(filenames, variables=None, product=None, type=None):
    """
    Read all the variables from a file, or a specified selection of variables in more detail, and print to stdout.

    :param filenames:   The filenames of the files to read
    :param variables:   The user specified variables of interest
    :param product:   The data reading plugin to use when reading the data
    :param type:   String representing the type of HDF data to read, i.e. 'VD' or 'SD'
    """
    from cis.data_io.products.AProduct import get_variables, get_data

    if variables is not None:
        for user_var in variables:
            print(str(get_data(filenames, user_var, product=product)))
    else:
        for variable in get_variables(filenames, product=product, data_type=type):
            print(variable)
