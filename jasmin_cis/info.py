'''
Routines for the info command
'''
import sys

from jasmin_cis.data_io.products.AProduct import get_variables


def __print_variables(all_variables, user_variables=None, print_err=True):
    '''
        Short routine for printing all variables, or a specified few.

        :param all_variables:   All of the variables to print or search through
        :param user_variables:   The user specified variables of interest
        :param print_err:   Boolean for deciding to print an error if a variable isn't found

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


def _filter_to_valid_variables(valid_vars, variables):
    for variable in variables.keys():
        if variable not in valid_vars:
            del variables[variable]


def info(filename, user_variables=None, data_type=None):
    '''
    Read all the variables from a file and print to stdout.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.

    :param filenames:   The filenames of the files to read
    :param user_variables:   The user specified variables of interest
    :param data_type:   String representing the type of HDF data to read, i.e. 'VD' or 'SD'

    '''
    from jasmin_cis.data_io.hdf import get_hdf4_file_variables
    from jasmin_cis.data_io.netcdf import get_netcdf_file_variables
    from jasmin_cis.data_io.aeronet import get_aeronet_file_variables
    from jasmin_cis.exceptions import InvalidFileExtensionError, CISError
    from os.path import basename

    valid_vars = get_variables([filename])
    if filename.endswith(".nc"):
        try:
            file_variables = get_netcdf_file_variables(filename)
            _filter_to_valid_variables(valid_vars, file_variables)
            __print_variables(file_variables, user_variables)
        except RuntimeError as e:
            raise CISError(e)
    elif filename.endswith(".hdf"):
        if (basename(filename).startswith("CAL_LID") or
        basename(filename).startswith("MISR")) and data_type == None:
            data_type = "SD"
        sd_vars, vd_vars = get_hdf4_file_variables(filename, data_type)

        if sd_vars is not None:
            print "\n====== SD variables:"
            _filter_to_valid_variables(valid_vars, sd_vars)
            if sd_vars is not None:
                __print_variables(sd_vars, user_variables, False)
        if vd_vars is not None:
            print "\n====== VD variables:"
            _filter_to_valid_variables(valid_vars, vd_vars)
            if vd_vars is not None:
                __print_variables(vd_vars, user_variables, False)
    elif filename.endswith(".lev20"):
        file_variables = get_aeronet_file_variables(filename)
        _filter_to_valid_variables(valid_vars, file_variables)
        __print_variables(file_variables, user_variables)
    else:
        raise InvalidFileExtensionError("File extension not recognised. Please use one of .nc, .hdf or .lev20")