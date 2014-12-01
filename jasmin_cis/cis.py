#!/bin/env python2.7
'''
Command line interface for the Climate Intercomparison Suite (CIS)
'''
import sys
import logging

from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
from jasmin_cis.exceptions import CISError, NoDataInSubsetError
from jasmin_cis.utils import add_file_prefix
from jasmin_cis import __author__, __version__, __status__, __website__

logger = logging.getLogger(__name__)

def __error_occurred(e):
    '''
    Wrapper method used to print error messages and exit the program.

    :param e: An error object or any string
    '''
    sys.stderr.write(str(e) + "\n")
    exit(1)

def __check_variable_is_valid(main_arguments, data, axis):
    '''
    Used for creating or appending to a dictionary of the format { variable_name : axis } which will later be used to assign
    the variable to the specified axis
    :param main_arguments: The arguments received from the parser
    :param data: A list of packed data objects
    :param var_axis_dict: A dictionary where the key will be the name of a variable and the value will be the axis it will be plotted on.
    :param axis: The axis on which to plot the variable on
    '''
    from jasmin_cis.exceptions import InvalidVariableError

    user_specified_variable = main_arguments.pop(axis + "axis")

    for data_item in data:
        if len(data_item.coords(name=user_specified_variable)) == 0 and len(data_item.coords(standard_name=user_specified_variable)) == 0 and data_item.name() != user_specified_variable and data_item.standard_name != user_specified_variable and data_item.long_name != user_specified_variable:
            raise InvalidVariableError(user_specified_variable + " is not a valid variable")

    return user_specified_variable

def plot_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'plot' command.
    Reads in the data files specified and passes the rest of the arguments to the plot function.

    :param main_arguments:    The command line arguments
    '''
    from plotting.plot import Plotter
    from jasmin_cis.data_io.read import read_data
    import jasmin_cis.exceptions as ex
    from iris.exceptions import IrisError

    # create a list of data object (ungridded or gridded(in that case, a Iris cube)), concatenating data from various files
    data = []
    for datagroup in main_arguments.datagroups:
        try:
            data.append(read_data(datagroup['filenames'], datagroup['variable'], datagroup['product']))
        except (IrisError, ex.InvalidVariableError, ex.ClassNotFoundError, IOError) as e:
            __error_occurred('Error when trying to read variable {} in file(s) {} using requested product {}.\nError '
                             'was: {}'.format(datagroup['variable'], datagroup['filenames'], datagroup['product'], e))
        except MemoryError as e:
         __error_occurred("Not enough memory to read the data for the requested plot. Please either reduce the amount "
                          "of data to be plotted, increase the swap space available on your machine or use a machine "
                          "with more memory (for example the JASMIN facility).")

    main_arguments = vars(main_arguments)
    main_arguments.pop('command') # Remove the command argument now it is not needed
    plot_type = main_arguments.pop("type")
    output = main_arguments.pop("output")

    main_arguments["x_variable"] = __check_variable_is_valid(main_arguments, data, "x")
    main_arguments["y_variable"] = __check_variable_is_valid(main_arguments, data, "y")

    try:
        Plotter(data, plot_type, output, **main_arguments)
    except (ex.CISError, ValueError) as e:
        __error_occurred(e)
    except MemoryError:
        __error_occurred("Not enough memory to plot the data after reading it in. Please either reduce the amount "
                         "of data to be plotted, increase the swap space available on your machine or use a machine "
                         "with more memory (for example the JASMIN facility).")

def info_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'info' command.
    Reads in the variables from the data file specified and lists them to stdout if no
    particular variable was specified, otherwise prints detailed information about each
    variable specified

    :param main_arguments:    The command line arguments (minus the info command)
    '''
    variables = main_arguments.variables
    filename = main_arguments.filename
    data_type = main_arguments.type

    from jasmin_cis.info import info

    try:
        info(filename, variables, data_type)
    except CISError as e:
        __error_occurred(e)


def col_cmd(main_arguments):
    '''
    Main routine for handling calls to the co-locate ('col') command.

    :param main_arguments:    The command line arguments (minus the col command)
    '''
    from jasmin_cis.exceptions import ClassNotFoundError, CISError
    from jasmin_cis.col import Colocate

    # Add a prefix to the output file so that we have a signature to use when we read it in again
    output_file = add_file_prefix("cis-", main_arguments.output + ".nc")
    data_reader = DataReader()
    missing_data_for_missing_samples = False
    if main_arguments.samplevariable is not None:
        sample_data = data_reader.read_data(main_arguments.samplefiles, main_arguments.samplevariable,
                                            main_arguments.sampleproduct)
    else:
        sample_data = data_reader.read_coordinates(main_arguments.samplefiles, main_arguments.sampleproduct)
        missing_data_for_missing_samples = True

    try:
        col = Colocate(sample_data, output_file, missing_data_for_missing_samples)
    except IOError as e:
        __error_occurred("There was an error reading one of the files: \n" + str(e))

    col_name = main_arguments.samplegroup['colocator'][0] if main_arguments.samplegroup['colocator'] is not None else None
    col_options = main_arguments.samplegroup['colocator'][1] if main_arguments.samplegroup['colocator'] is not None else None
    kern_name = main_arguments.samplegroup['kernel'][0] if main_arguments.samplegroup['kernel'] is not None else None
    kern_options = main_arguments.samplegroup['kernel'][1] if main_arguments.samplegroup['kernel'] is not None else None

    for input_group in main_arguments.datagroups:
        variable = input_group['variable']
        filenames = input_group['filenames']
        product = input_group["product"] if input_group["product"] is not None else None

        data = data_reader.read_data(filenames, variable, product)
        data_writer = DataWriter()
        try:
            output = col.colocate(data, col_name, col_options, kern_name, kern_options)
            data_writer.write_data(output, output_file, sample_data, True)
        except ClassNotFoundError as e:
            __error_occurred(str(e) + "\nInvalid co-location option.")
        except (CISError, IOError) as e:
            __error_occurred(e)


def subset_cmd(main_arguments):
    '''
    Main routine for handling calls to the subset command.

    :param main_arguments:    The command line arguments (minus the subset command)
    '''
    from jasmin_cis.subsetting.subset import Subset

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Subsetting can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    variable = input_group['variable']
    filenames = input_group['filenames']
    product = input_group["product"] if input_group["product"] is not None else None

    # Add a prefix to the output file so that we have a signature to use when we read it in again
    output_file = add_file_prefix("cis-", main_arguments.output + ".nc")
    subset = Subset(main_arguments.limits, output_file)
    try:
        subset.subset(variable, filenames, product)
    except (NoDataInSubsetError, CISError) as exc:
         __error_occurred(exc)


def aggregate_cmd(main_arguments):
    """
    Main routine for handling calls to the aggregation command.

    :param main_arguments: The command line arguments (minus the aggregate command)
    """
    from jasmin_cis.aggregation.aggregate import Aggregate

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Aggregation can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    variable = input_group['variable']
    filenames = input_group['filenames']
    product = input_group["product"] if input_group["product"] is not None else None
    kernel = input_group["kernel"] if input_group["kernel"] is not None else 'mean'

    # Add a prefix to the output file so that we have a signature to use when we read it in again
    output_file = add_file_prefix("cis-", main_arguments.output + ".nc")
    aggregate = Aggregate(main_arguments.grid, output_file)
    aggregate.aggregate(variable, filenames, product, kernel)


def version_cmd(_main_arguments):
    print "Using CIS version:", __version__, "("+__status__+")"


commands = {'plot': plot_cmd,
            'info': info_cmd,
            'col': col_cmd,
            'aggregate' : aggregate_cmd,
            'subset': subset_cmd,
            'version': version_cmd}


def main():
    """
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    """
    import os
    import logging
    from logging import config
    from datetime import datetime

    from parse import parse_args

    # configure logging
    try:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
    except IOError as e:
        # If we don't have permission to write to the log file, all we can do is inform the user
        # All future calls to the logging module will be ignored (?)
        print("WARNING: Unable to write to the log: %s" % e)
    logging.captureWarnings(True)  # to catch warning from 3rd party libraries

    # parse command line arguments
    arguments = parse_args()
    command = arguments.command

    logging.debug("CIS started at: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    logging.debug("Running command: " + command)
    logging.debug("With the following arguments: " + str(arguments))

    # execute command
    commands[command](arguments)


if __name__ == '__main__':
    main()
