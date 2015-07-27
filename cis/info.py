'''
Routines for the info command
'''


def __print_variables(all_variables, user_variables=None):
    '''
        Short routine for printing all variables, or a specified few.

        :param all_variables:   All of the variables to print or search through
        :param user_variables:   The user specified variables of interest
    '''
    import sys
    if user_variables is not None:
        for user_var in user_variables:
            try:
                print user_var+": "+str(all_variables[user_var])
            except KeyError:
                sys.stderr.write("Variable '" + user_var +  "' not found \n")
    else:
        for item in all_variables:
            print item


def info(filename, user_variables=None, data_type=None):
    '''
    Read all the variables from a file and print to stdout.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.

    :param filenames:   The filenames of the files to read
    :param user_variables:   The user specified variables of interest
    :param data_type:   String representing the type of HDF data to read, i.e. 'VD' or 'SD'

    '''
    from cis.data_io.products.AProduct import get_variables

    variables = get_variables([filename], data_type)
    __print_variables(variables, user_variables)
