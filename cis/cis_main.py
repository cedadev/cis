#!/bin/env python2.7
"""
Command line interface for the Climate Intercomparison Suite (CIS)
"""
import sys
import traceback
import logging

from cis.data_io.data_reader import DataReader
from cis.data_io.data_writer import DataWriter
from cis import __version__, __status__

logger = logging.getLogger(__name__)


def __error_occurred(e):
    """
    Wrapper method used to print error messages and exit the program.

    :param e: An error object or any string
    """
    sys.stderr.write(str(e) + "\n")
    logging.debug(str(e) + "\n")
    logging.debug(traceback.format_exc())
    logging.error(str(e) + " - check cis.log for details\n")
    exit(1)


def __check_variable_is_valid(main_arguments, data, axis):
    """
    Used for creating or appending to a dictionary of the format { variable_name : axis } which will later be used to
    assign the variable to the specified axis

    :param main_arguments: The arguments received from the parser
    :param data: A list of packed data objects
    :param var_axis_dict: A dictionary where the key will be the name of a variable and the value will be the axis it
     will be plotted on.
    :param axis: The axis on which to plot the variable on
    """
    from cis.exceptions import InvalidVariableError

    user_specified_variable = main_arguments.pop(axis + "axis")

    for data_item in data:
        if len(data_item.coords(user_specified_variable)) == 0 \
                and len(data_item.coords(standard_name=user_specified_variable)) == 0 \
                and data_item.name() != user_specified_variable \
                and data_item.standard_name != user_specified_variable \
                and data_item.long_name != user_specified_variable:
            raise InvalidVariableError("{} is not a valid variable".format(user_specified_variable))

    return user_specified_variable


def plot_cmd(main_arguments):
    """
    Main routine for handling calls to the 'plot' command.
    Reads in the data files specified and passes the rest of the arguments to the plot function.

    :param main_arguments:    The command line arguments
    """
    from cis.plotting.formatted_plot import Plotter
    from cis.data_io.data_reader import DataReader

    data = DataReader().read_datagroups(main_arguments.datagroups)

    # We have to pop off the arguments which plot isn't expecting so that it treats everything else as an mpl kwarg
    main_arguments = vars(main_arguments)
    _ = main_arguments.pop('command')
    _ = main_arguments.pop("quiet")
    _ = main_arguments.pop("verbose")
    _ = main_arguments.pop("force_overwrite")
    _ = main_arguments.pop("output_var", None)

    layer_opts = [{k: v for k, v in d.items() if k not in ['variables', 'filenames', 'product']}
                  for d in main_arguments.pop('datagroups')]
    Plotter(data, layer_opts=layer_opts, **main_arguments)


def info_cmd(main_arguments):
    """
    Main routine for handling calls to the 'info' command.
    Reads in the variables from the data files specified and lists them to stdout if no
    particular variable was specified, otherwise prints detailed information about each
    variable specified

    :param main_arguments:    The command line arguments (minus the info command)
    """
    from cis.info import info
    dg = main_arguments.datagroups[0]
    info(dg['filenames'], dg['variables'], dg['product'], main_arguments.type)


def col_cmd(main_arguments):
    """
    Main routine for handling calls to the collocate ('col') command.

    :param main_arguments:    The command line arguments (minus the col command)
    """
    from cis.collocation.col_framework import get_kernel

    # TODO: Try and factor this out somehow
    output_file = main_arguments.output
    data_reader = DataReader()
    missing_data_for_missing_samples = False
    if main_arguments.samplevariable is not None:
        sample_data = data_reader.read_data_list(main_arguments.samplefiles, main_arguments.samplevariable,
                                                 main_arguments.sampleproduct)[0]
        missing_data_for_missing_samples = True
    else:
        sample_data = data_reader.read_coordinates(main_arguments.samplefiles, main_arguments.sampleproduct)

    col_name = main_arguments.samplegroup['collocator'][0] if main_arguments.samplegroup.get('collocator', None) is not None else ''
    col_options = main_arguments.samplegroup['collocator'][1] if main_arguments.samplegroup.get('collocator', None) is not None else {}
    kern_name = main_arguments.samplegroup['kernel'][0] if main_arguments.samplegroup.get('kernel', None) is not None else None
    kern_options = main_arguments.samplegroup['kernel'][1] if main_arguments.samplegroup.get('kernel', None) is not None else {}

    for input_group in main_arguments.datagroups:
        variables = input_group['variables']
        filenames = input_group['filenames']
        product = input_group.get("product", None)

        data = data_reader.read_data_list(filenames, variables, product)
        data_writer = DataWriter()

        kernel = get_kernel(kern_name)(**kern_options) if kern_name is not None else None

        output = data.collocated_onto(sample_data, how=col_name, kernel=kernel,
                                      missing_data_for_missing_samples=missing_data_for_missing_samples, **col_options)

        data_writer.write_data(output, output_file)


def subset_cmd(main_arguments):
    """
    Main routine for handling calls to the subset command.

    :param main_arguments:    The command line arguments (minus the subset command)
    """
    from cis import read_data_list
    from iris.exceptions import IrisError
    import cis.exceptions as ex

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Subsetting can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    variables = input_group['variables']
    filenames = input_group['filenames']
    product = input_group.get("product", None)

    # Read the input data - the parser limits the number of data groups to one for this command.
    try:
        # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
        # the specified files.
        logging.info("Reading data for variables: %s", variables)
        data = read_data_list(filenames, variables, product)
    except (IrisError, ex.InvalidVariableError) as e:
        raise ex.CISError("There was an error reading in data: \n" + str(e))
    except IOError as e:
        raise ex.CISError("There was an error reading one of the files: \n" + str(e))

    subset = data.subset(**main_arguments.limits)

    if subset is None:
        # Constraints exclude all data.
        raise ex.NoDataInSubsetError("No output created - constraints exclude all data")

    subset.save_data(main_arguments.output)


def aggregate_cmd(main_arguments):
    """
    Main routine for handling calls to the aggregation command.

    :param main_arguments: The command line arguments (minus the aggregate command)
    """
    from cis import read_data_list
    from iris.exceptions import IrisError
    import cis.exceptions as ex
    from cis.data_io.gridded_data import GriddedDataList

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Aggregation can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    variables = input_group['variables']
    filenames = input_group['filenames']

    # Read the input data - the parser limits the number of data groups to one for this command.
    try:
        # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
        # the specified files.
        logging.info("Reading data for variables: %s", variables)
        data = read_data_list(filenames, variables, input_group.get("product", None))
    except (IrisError, ex.InvalidVariableError) as e:
        raise ex.CISError("There was an error reading in data: \n" + str(e))
    except IOError as e:
        raise ex.CISError("There was an error reading one of the files: \n" + str(e))

    if isinstance(data, GriddedDataList):
        logging.warning("The aggregate command will not be supported in future versions of CIS. "
                        "Please use 'collapse' instead.")
        if any(v is not None for v in main_arguments.grid.values()):
            raise ex.InvalidCommandLineOptionError("Grid specifications are not supported for Gridded aggregation.")
        output = data.collapsed(main_arguments.grid.keys(), how=input_group.get("kernel", ''))
    else:
        output = data.aggregate(how=input_group.get("kernel", ''), **main_arguments.grid)

    output.save_data(main_arguments.output)


def collapse_cmd(main_arguments):
    # TODO: finish me!
    pass


def evaluate_cmd(main_arguments):
    """
    Main routine for handling calls to the evaluation command

    :param main_arguments: The command line arguments (minus the eval command)
    """
    from cis.evaluate import Calculator
    data_reader = DataReader()
    data_list = data_reader.read_datagroups(main_arguments.datagroups)
    calculator = Calculator()
    result = calculator.evaluate(data_list, main_arguments.expr, main_arguments.output_var,
                                 main_arguments.units, main_arguments.attributes)
    result.save_data(main_arguments.output)


def stats_cmd(main_arguments):
    """
    Main routine for handling calls to the statistics command.

    :param main_arguments: The command line arguments (minus the stats command)
    """
    from cis.stats import StatsAnalyzer
    from cis.data_io.gridded_data import GriddedDataList
    data_reader = DataReader()
    data_list = data_reader.read_datagroups(main_arguments.datagroups)
    analyzer = StatsAnalyzer(*data_list)
    results = analyzer.analyze()
    header = "RESULTS OF STATISTICAL COMPARISON:"
    note = "Compared all points which have non-missing values in both variables"
    header_length = max(len(header), len(note))
    print(header_length * '=')
    print(header)
    print(header_length * '-')
    print(note)
    print(header_length * '=')
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
    print("Using CIS version: {ver} ({stat})".format(ver=__version__, stat=__status__ ))


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

    from cis.parse import parse_args

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

    try:
        parse_and_run_arguments()
    except MemoryError:
        __error_occurred("Not enough memory. Please either reduce the amount "
                         "of data, increase the swap space available on your machine or use a machine "
                         "with more memory (for example the JASMIN facility).")
    except Exception as e:
        __error_occurred(e)


if __name__ == '__main__':
    main()
