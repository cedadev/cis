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
        print "Error: " + str(e)
        exit(1)
    except IOError as e:
        print "There was an error reading one of the files: "
        print str(e)
        exit(1)
    
    try:
        plot(data, main_arguments.type, main_arguments.output, main_arguments.plot_format_args)
    except ex.InvalidPlotTypeError as e:
        print str(e)
        exit(1)
    except ex.InvalidPlotFormatError as e:
        print str(e)
        exit(1)

def info_cmd(main_arguments):
    from data_io.read import list_netcdf_file_variables
    for item in list_netcdf_file_variables(main_arguments.filename):
        print item


commands = { 'plot' : plot_cmd,
             'info' : info_cmd}

if __name__ ==  '__main__':
    from parse import parse_args
    #arguments = parse_args()
    arguments = parse_args(sys.argv[1:])
    commands[arguments.command](arguments)
    
    
