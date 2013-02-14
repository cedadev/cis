#!/bin/env python2.7
'''
Command line interface for the Climate Intercomparison Suite (CIS)
'''
import sys
from jasmin_cis.exceptions import CISError
from jasmin_cis.info import  info

import logging
logger = logging.getLogger(__name__)

__author__ = "David Michel, Daniel Wallis and Duncan Watson-Parris"
__version__ = "x"
__status__ = "Development"
__website__ = "http://proj.badc.rl.ac.uk/cedaservices/wiki/JASMIN/CommunityIntercomparisonSuite"

def __setup_logging(log_file, log_level):
    '''
    Set up the logging used throughout cis
    
    @param log_file:    The filename of the file to store the logs
    @param log_level:   The level at which to log 
    '''

    logging.basicConfig(format='%(levelname)s: %(message)s',filename=log_file, level=log_level)

    # This sends warnings straight to the logger, this is used as iris can throw a lot of warnings
    #  that we don't want bubbling up. We may change this in the future as it's a bit overkill.
    logging.captureWarnings(True)

def __error_occurred(e):
    '''
    Wrapper method used to print error messages.
    
    @param e: An error object or any string
    '''
    sys.stderr.write(str(e) + "\n")
    exit(1)


def plot_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'plot' command. 
    Reads in the data files specified and passes the rest of the arguments to the plot function.
        

    @param main_arguments:    The command line arguments (minus the plot command)        
    '''
    from plot import Plotter
    from data_io.read import read_data
    import jasmin_cis.exceptions as ex
    from iris.exceptions import IrisError
    import utils
    from collections import OrderedDict
    
    main_arguments.pop("variable") # Pop off default variable as will have already been assigned where necessary
    
    try:
        # create a dictionary of [key=variable, value=list of filename]
        dict_of_var_and_filename = OrderedDict() # Cannot use dict, as unordered and need order for scatter overlay
        for datafile in main_arguments["datafiles"]:
            utils.add_element_to_list_in_dict(dict_of_var_and_filename, datafile["variable"], datafile["filename"])

        # create a list of data object (ungridded or gridded(in that case, a Iris cube)), concatenating data from various files
        data = [ read_data(files,var) for var, files in dict_of_var_and_filename.iteritems() ]

    except (IrisError, ex.InvalidVariableError, ex.FileIOError) as e:
        __error_occurred(e)
    except IOError as e:
        __error_occurred("There was an error reading one of the files: \n" + e)
        
    plot_type = main_arguments.pop("type")
    output = main_arguments.pop("output")
    
    try:
        Plotter(data, plot_type, output, **main_arguments)
    except (ex.InvalidPlotTypeError, ex.InvalidPlotFormatError, ex.InconsistentDimensionsError, ex.InvalidFileExtensionError, ValueError) as e:
        __error_occurred(e)


def info_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'info' command.
    Reads in the variables from the data file specified and lists them to stdout if no
    particular variable was specified, otherwise prints detailed information about each
    variable specified
        
    @param main_arguments:    The command line arguments (minus the info command)
    '''    
    variables = main_arguments.pop('variables', None)
    filename = main_arguments.pop('filename')
    
    try:
        info(filename, variables)
    except CISError as e:
        __error_occurred(e)


def col_cmd(main_arguments):
    '''
    Main routine for handling calls to the co-locate ('col') command. 
        
    @param main_arguments:    The command line arguments (minus the col command)         
    '''
    from jasmin_cis.exceptions import InvalidColocationMethodError, CISError
    from data_io.read import read_file_coordinates, read_data
    from col import Colocator
    from data_io.write_netcdf import write_coordinates, add_data_to_file

    sample_file = main_arguments.pop("samplefilename")
    input_groups = main_arguments.pop("datafiles")
    output_file = "cis-col-" + main_arguments.pop("output") + ".nc"

    coords = read_file_coordinates(sample_file)

    for coord in coords:
        print coord.data
        coord.data = coord.data[0:10]
        print coord.data

    sample_points = coords.get_coordinates_points()

    write_coordinates(coords, output_file)
   
    for input_group in input_groups:
        filename = input_group['filename']
        variable = input_group['variable']
        method = input_group['method']

        try:
            data = read_data(filename, variable)
        except CISError as e:
            __error_occurred(e)
        
        try:
            col = Colocator(sample_points, data, method)
        except InvalidColocationMethodError as e:
            __error_occurred(str(e) + "\nInvalid co-location method: "+method)
        
        new_data = col.colocate()

        add_data_to_file(new_data, output_file)


commands = { 'plot' : plot_cmd,
             'info' : info_cmd,
             'col'  : col_cmd} 

def main():
    '''
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    '''
    from parse import parse_args
    import logging, logging.config
    from datetime import datetime

    # configure logging
    logging.config.fileConfig("logging.conf")
    logging.captureWarnings(True) # to catch warning from 3rd party libraries

    # parse command line arguments
    arguments = parse_args()
    command = arguments.pop("command")

    logging.debug("CIS started at: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    logging.debug("Running command: " + command)
    logging.debug("With the following arguments: " + str(arguments))

    # execute command
    commands[command](arguments)


if __name__ ==  '__main__':
    main()
