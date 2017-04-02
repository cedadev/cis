#!/bin/env python
"""
Command line interface for the Climate Intercomparison Suite (CIS)
"""
import sys
import traceback
import logging

from cis.data_io.data_reader import DataReader
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
    info(dg['filenames'], dg.get('variables', None), dg.get('product', None), main_arguments.type)


def col_cmd(main_arguments):
    """
    Main routine for handling calls to the collocate ('col') command.

    :param main_arguments:    The command line arguments (minus the col command)
    """
    from cis.collocation.col_framework import get_kernel
    from cis.parse import check_boolean

    # Read the sample data
    missing_data_for_missing_sample = False
    if main_arguments.samplevariable is not None:
        sample_data = DataReader().read_data_list(main_arguments.samplefiles, main_arguments.samplevariable,
                                                  main_arguments.sampleproduct)[0]
        missing_data_for_missing_sample = True
    else:
        sample_data = DataReader().read_coordinates(main_arguments.samplefiles, main_arguments.sampleproduct)

    # Unpack the sample options
    col_name, col_options = main_arguments.samplegroup.get('collocator', ('', {}))
    kern_name, kern_options = main_arguments.samplegroup.get('kernel', ('', {}))

    missing_data_for_missing_sample = check_boolean(col_options.pop('missing_data_for_missing_sample',
                                                                    str(missing_data_for_missing_sample)), logging)

    kernel = get_kernel(kern_name)(**kern_options) if kern_name else None

    for input_group in main_arguments.datagroups:
        # Then collocate each datagroup
        data = DataReader().read_single_datagroup(input_group)
        output = data.collocated_onto(sample_data, how=col_name, kernel=kernel,
                                      missing_data_for_missing_sample=missing_data_for_missing_sample, **col_options)
        output.save_data(main_arguments.output)


def subset_cmd(main_arguments):
    """
    Main routine for handling calls to the subset command.

    :param main_arguments:    The command line arguments (minus the subset command)
    """
    import cis.exceptions as ex

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Subsetting can only be performed on one data group")

    data = DataReader().read_single_datagroup(main_arguments.datagroups[0])

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
    import cis.exceptions as ex
    from cis.data_io.gridded_data import GriddedDataList

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Aggregation can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    data = DataReader().read_single_datagroup(input_group)

    if isinstance(data, GriddedDataList):
        logging.warning("The aggregate command is deprecated for GriddedData and will not be supported in future "
                        "versions of CIS. Please use 'collapse' instead.")
        if any(v is not None for v in main_arguments.grid.values()):
            raise ex.InvalidCommandLineOptionError("Grid specifications are not supported for Gridded aggregation.")
        output = data.collapsed(list(main_arguments.grid.keys()), how=input_group.get("kernel", ''))
    else:
        output = data.aggregate(how=input_group.get("kernel", ''), **main_arguments.grid)

    output.save_data(main_arguments.output)


def collapse_cmd(main_arguments):
    """
    Main routine for handling calls to the collapse command.

    :param main_arguments: The command line arguments (minus the collapse command)
    """
    from cis.data_io.ungridded_data import UngriddedDataList

    if len(main_arguments.datagroups) > 1:
        __error_occurred("Collapse can only be performed on one data group")
    input_group = main_arguments.datagroups[0]

    data = DataReader().read_single_datagroup(input_group)

    if isinstance(data, UngriddedDataList):
        logging.error("The collapse command can only be performed on gridded data. "
                      "Please use 'aggregate' instead.")

    output = data.collapsed(main_arguments.dimensions, how=input_group.get("kernel", ''))

    output.save_data(main_arguments.output)


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
            'collocate': col_cmd,
            'aggregate': aggregate_cmd,
            'subset': subset_cmd,
            'collapse': collapse_cmd,
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
