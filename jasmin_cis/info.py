'''
Routines for the info command
'''
import sys
import jasmin_cis.data_io.read_gridded
import jasmin_cis.data_io.read_ungridded

def print_variables(all_variables, user_variables=None, print_err=True):
    '''
        Short routine for printing all variables, or a specified few.

        args:
        all_variables:   All of the variables to print or search through
        user_variables:   The user specified variables of interest
        print_err:   Boolean for deciding to print an error if a variable isn't found

    '''
    if user_variables is not None:
        for user_var in user_variables:
            try:
                print user_var+": "+str(all_variables[user_var])
            except KeyError:
                if print_err: sys.stderr.write("Variable '" + user_var +  "' not found \n")
    else:
        for item in all_variables:
            print item


def info(filename, user_variables=None):
    '''
    Read all the variables from a file and print to stdout.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.

    args:
        filenames:   The filenames of the files to read
        user_variables:   The user specified variables of interest

    '''
    from jasmin_cis.exceptions import CISError
    import data_io.read_gridded, data_io.read_ungridded
    from pyhdf.error import HDF4Error
    try:
        file_variables = data_io.read_gridded.get_file_variables(filename)
        print_variables(file_variables, user_variables)
    except RuntimeError:
        try:
            sd_vars, vd_vars = data_io.read_ungridded.get_file_variables(filename)
            print "\n====== SD variables:"
            print_variables(sd_vars, user_variables, False)
            print "\n====== VD variables:"
            print_variables(vd_vars, user_variables, False)
        except HDF4Error as e:
            raise CISError(e)