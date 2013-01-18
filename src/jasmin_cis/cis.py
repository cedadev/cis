#!/bin/env python
'''
Main driver script for the Climate Intercomparison Suite
'''
import sys

def plot_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'plot' command. 
    Reads in the data files specified and passes the rest of the arguments to the plot function.
        
    args:
        main_arguments:    The command line arguments (minus the plot command)        
    '''
    from plot import plot
    from data_io.read import read_variable 
    import jasmin_cis.exceptions as ex
    from iris.exceptions import IrisError
    
    data = []
    # This currently assumes the variable is in each of the filenames specified,
    #  this may change in the future.
    try:
        for variable in main_arguments.variables:
            data.append(read_variable(main_arguments.filenames, variable))
    except IrisError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except IOError as e:
        print "There was an error reading one of the files: "
        sys.stderr.write(str(e) + "\n")
        exit(1)
    
    try:
        plot(data, main_arguments.type, main_arguments.output, **main_arguments.plot_format_args)
    except ex.InvalidPlotTypeError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except ex.InvalidPlotFormatError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)

def info_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'info' command. 
    Reads in the variables from the data file specified and lists them to stdout if no
    particular variable was specified, otherwise prints detailed information about each
    variable specified
        
    args:
        main_arguments:    The command line arguments (minus the info command)         
    '''    
    from data_io.read import get_netcdf_file_variables
    file_variables = get_netcdf_file_variables(main_arguments.filename)
    
    if main_arguments.variables != None:
        for variable in main_arguments.variables:
            try:
                print file_variables[variable]
            except KeyError:
                print("Variable '{0}' not found".format(variable))
    else:
        for item in file_variables:
            print item


commands = { 'plot' : plot_cmd,
             'info' : info_cmd}

def setup_logging(log_file, log_level):
    '''
    Set up the logging used throughout cis
    
    args:
        log_file:    The filename of the file to store the logs
        log_level:   The level at which to log 
    '''
    import logging
    logging.basicConfig(format='%(levelname)s: %(message)s',filename=log_file, level=log_level)
    # This sends warnings straight to the logger, this is used as iris can throw a lot of warnings
    #  that we don't want bubbling up. We may change this in the future as it's a bit overkill.
    logging.captureWarnings(True)

def main():
    '''
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    '''
    from parse import parse_args
    import logging
    from datetime import datetime
    
    setup_logging("cis.log", logging.INFO)
    
    arguments = parse_args()
    
    # Log the input arguments so that the user can trace how a plot was created
    logging.info(datetime.now().strftime("%Y-%m-%d %H:%M")+ ": CIS "+ arguments.command + " got the following arguments: ")
    logging.info(arguments)
    
    commands[arguments.command](arguments)
    
if __name__ ==  '__main__':
    main()   