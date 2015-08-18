'''
Routines for the info command
'''


def info(filenames, user_variables=None, product=None, data_type=None):
    '''
    Read all the variables from a file and print to stdout.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.

    :param filenames:   The filenames of the files to read
    :param user_variables:   The user specified variables of interest
    :param data_type:   String representing the type of HDF data to read, i.e. 'VD' or 'SD'

    '''
    from cis.data_io.products.AProduct import get_variables, get_data

    if user_variables is not None:
        for user_var in user_variables:
            print str(get_data(filenames, user_var, product=product))
    else:
        for variable in get_variables(filenames, product=product, data_type=data_type):
            print variable
