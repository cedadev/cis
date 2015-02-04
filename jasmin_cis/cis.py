#!/bin/env python2.7
'''
Command line interface for the Climate Intercomparison Suite (CIS)
'''
import sys
import traceback
import logging

from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
from jasmin_cis.exceptions import CISError, NoDataInSubsetError
from jasmin_cis import __version__, __status__


logger = logging.getLogger(__name__)


def __error_occurred(e):
    '''
    Wrapper method used to print error messages and exit the program.

    :param e: An error object or any string
    '''
    sys.stderr.write(str(e) + "\n")
    logging.debug(str(e) + "\n")
    logging.debug(traceback.format_exc())
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
            raise InvalidVariableError("{} is not a valid variable".format(user_specified_variable))

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
            data.append(read_data(datagroup['filenames'], datagroup['variables'], datagroup['product']))
        except (IrisError, ex.InvalidVariableError, ex.ClassNotFoundError, IOError) as e:
            __error_occurred('Error when trying to read variable {} in file(s) {} using requested product {}.\nError '
                             'was: {}'.format(datagroup['variables'], datagroup['filenames'], datagroup['product'], e))
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
    except (ex.CISError) as e:
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

    output_file = main_arguments.output
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
        variables = input_group['variables']
        filenames = input_group['filenames']
        product = input_group["product"] if input_group["product"] is not None else None

        data = data_reader.read_data(filenames, variables, product)
        data_writer = DataWriter()
        try:
            output = col.colocate(data, col_name, col_options, kern_name, kern_options)
            data_writer.write_data(output, output_file)
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

    variables = input_group['variables']
    filenames = input_group['filenames']
    product = input_group["product"] if input_group["product"] is not None else None

    subset = Subset(main_arguments.limits, main_arguments.output)
    try:
        subset.subset(variables, filenames, product)
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

    variables = input_group['variables']
    filenames = input_group['filenames']
    product = input_group["product"] if input_group["product"] is not None else None
    kernel = input_group["kernel"] if input_group["kernel"] is not None else 'moments'

    aggregate = Aggregate(main_arguments.grid, main_arguments.output)
    aggregate.aggregate(variables, filenames, product, kernel)


def evaluate_cmd(main_arguments):
    """
    Main routine for handling calls to the evaluation command

    :param main_arguments: The command line arguments (minus the eval command)
    """
    from evaluate import Calculator
    data_reader = DataReader()
    data_list = data_reader.read_datagroups(main_arguments.datagroups)
    calculator = Calculator()
    if main_arguments.output_var is not None:
        result = calculator.evaluate(data_list, main_arguments.expr, main_arguments.output_var)
    else:
        result = calculator.evaluate(data_list, main_arguments.expr)
    result.save_data(main_arguments.output)


def stats_cmd(main_arguments):
    """
    Main routine for handling calls to the statistics command.

    :param main_arguments: The command line arguments (minus the stats command)
    """
    from stats import StatsAnalyzer
    from jasmin_cis.data_io.gridded_data import GriddedDataList
    data_reader = DataReader()
    data_list = data_reader.read_datagroups(main_arguments.datagroups)
    analyzer = StatsAnalyzer(*data_list)
    results = analyzer.analyze()
    header = "RESULTS OF STATISTICAL COMPARISON:"
    print(len(header) * '=')
    print(header)
    print(len(header) * '=')
    for result in results:
        print(result.pprint())
    if main_arguments.output:
        cubes = GriddedDataList([result.as_cube() for result in results])
        variables = []
        filenames = []
        for datagroup in main_arguments.datagroups:
            variables.extend(datagroup['variables'])
            filenames.extend(datagroup['filenames'])
        history = "Statistical comparison performed using CIS version " + __version__ + \
                  "\n variables: " + str(variables) + \
                  "\n from files: " + str(set(filenames))
        cubes.add_history(history)
        cubes.save_data(main_arguments.output)


def version_cmd(_main_arguments):
    print "Using CIS version:", __version__, "("+__status__+")"


commands = {'plot': plot_cmd,
            'info': info_cmd,
            'col': col_cmd,
            'aggregate': aggregate_cmd,
            'subset': subset_cmd,
            'eval': evaluate_cmd,
            'stats': stats_cmd,
            'version': version_cmd}


def parse_and_run_arguments(arguments=None):
    """
    Parse and run the arguments
    :param arguments: an arguments list or None to parse all
    """
    from datetime import datetime

    from parse import parse_args

    # parse command line arguments
    arguments = parse_args(arguments)
    command = arguments.command
    logging.debug("CIS started at: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    logging.debug("Running command: " + command)
    logging.debug("With the following arguments: " + str(arguments))

    # execute command
    cmd = commands[command]
    cmd(arguments)


def main():
    """
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    """
    import os
    import logging
    from logging import config

    # configure logging
    try:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
    except IOError as e:
        # If we don't have permission to write to the log file, all we can do is inform the user
        # All future calls to the logging module will be ignored (?)
        print("WARNING: Unable to write to the log: %s" % e)
    logging.captureWarnings(True)  # to catch warning from 3rd party libraries

    parse_and_run_arguments()


if __name__ == '__main__':
    main()
