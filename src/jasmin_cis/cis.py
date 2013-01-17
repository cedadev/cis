#!/bin/env python
'''
Main driver script for the Climate Intercomparison Suite
'''
import sys

def plot_cmd(main_arguments):
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
        plot(data, main_arguments.type, main_arguments.output, main_arguments.plot_format_args)
    except ex.InvalidPlotTypeError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except ex.InvalidPlotFormatError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)

def info_cmd(main_arguments):
    from data_io.read import get_netcdf_file_variables
    file_variables = get_netcdf_file_variables(main_arguments.filename)
    
    if main_arguments.variables != None:
        for variable in main_arguments.variables:
            print file_variables[variable]
    else:
        for item in file_variables:
            print item


commands = { 'plot' : plot_cmd,
             'info' : info_cmd}

def setup_logging(log_file, log_level):
    import logging
    logging.basicConfig(format='%(levelname)s: %(message)s',filename=log_file, level=log_level)
    logging.captureWarnings(True)

if __name__ ==  '__main__':
    from parse import parse_args
    import logging
    from datetime import datetime
    
    setup_logging("cis.log", logging.INFO)
    arguments = parse_args(sys.argv[1:])
    
    logging.info(datetime.now().strftime("%Y-%m-%d %H:%M")+ ": CIS "+arguments.command+" got the following arguments: ")
    logging.info(arguments)
    
    commands[arguments.command](arguments)
    
    
