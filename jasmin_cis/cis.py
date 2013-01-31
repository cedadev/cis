#!/bin/env python2.7
'''
Command line interface for the Climate Intercomparison Suite (CIS)
'''
import sys
from jasmin_cis.exceptions import CISError

def __setup_logging(log_file, log_level):
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


def __error_occurred(e):
    '''
    Wrapper method used to print error messages.
    
    args:
        An error object or any string
    '''
    sys.stderr.write(str(e) + "\n")
    exit(1)


def plot_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'plot' command. 
    Reads in the data files specified and passes the rest of the arguments to the plot function.
        
    args:
        main_arguments:    The command line arguments (minus the plot command)        
    '''
    from plot import Plotter
    from data_io.read import read_variable_from_files 
    import jasmin_cis.exceptions as ex
    from iris.exceptions import IrisError
    
    main_arguments.pop("variable") # Pop off default variable as will have already been assigned where necessary
    
    try:        
        data = [read_variable_from_files(datafile["filename"], datafile["variable"]) for datafile in main_arguments["datafiles"]]
    except IrisError as e:
        __error_occurred(e)
    except IOError as e:
        __error_occurred("There was an error reading one of the files: \n" + e)
    except ex.InvalidVariableError as e:
        __error_occurred(e)
    
    plot_type = main_arguments.pop("type")
    output = main_arguments.pop("output")
    
    try:
        Plotter(data, plot_type, output, **main_arguments)
    except (ex.InvalidPlotTypeError, ex.InvalidPlotFormatError, ex.InconsistentDimensionsError, ex.InvalidFileExtensionError) as e:
        __error_occurred(e)
    except ValueError as e:
        __error_occurred(e)


def info_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'info' command. 
    Reads in the variables from the data file specified and lists them to stdout if no
    particular variable was specified, otherwise prints detailed information about each
    variable specified
        
    args:
        main_arguments:    The command line arguments (minus the info command)         
    '''    
    variables = main_arguments.pop('variables', None)
    filename = main_arguments.pop('filename')
    
    try:
        summarise_all_variables_from_file(filename, variables)
    except CISError as e:
        __error_occurred(e)
    
    
def print_variables(all_variables, user_variables=None, print_err=True):
    '''
        Short routine for priting all variables, or a specified few.
    
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


def summarise_all_variables_from_file(filename, user_variables=None):
    from jasmin_cis.exceptions import CISError
    import data_io.read_gridded, data_io.read_ungridded
    from pyhdf.error import HDF4Error
    '''
    Read all the variables from a file and print to stdout.
    File can contain either gridded and ungridded data.
    First tries to read data as gridded, if that fails, tries as ungridded.
    
    args:
        filenames:   The filenames of the files to read
        user_variables:   The user specified variables of interest

    '''
    try:
        file_variables = data_io.read_gridded.get_file_variables(filename)
        print_variables(file_variables, user_variables)
    except RuntimeError:
        try:
            sd_vars, vd_vars = data_io.read_ungridded.get_file_variables(filename)
            print "SD variables:"
            print_variables(sd_vars, user_variables, False)
            print "VD variables:"
            print_variables(vd_vars, user_variables, False)
        except HDF4Error as e:
            raise CISError(e)

def col_cmd(main_arguments):
    '''
    Main routine for handling calls to the co-locate ('col') command. 
        
    args:
        main_arguments:    The command line arguments (minus the col command)         
    '''
    from jasmin_cis.exceptions import InvalidColocationMethodError, CISError
    from data_io.read import read_file_coordinates, read_variable_from_files
    from col import Colocator
    
    sample_ponts = read_file_coordinates(main_arguments.pop("samplefilename"))
   
    input_groups = main_arguments.pop("datafiles")
   
    for input_group in input_groups:
        filename = input_group['filename']
        variable = input_group['variable']
        method = input_group['method']
        
        #data_dict = read_variable(filename, variable)
        try:
            data = read_variable_from_files(filename,[variable]+['Latitude','Longitude'])
        except CISError:
            __error_occurred("Unable to read file: "+filename)
        
        try:
            col = Colocator(sample_ponts, data, method)
        except InvalidColocationMethodError:
            __error_occurred("Invalid co-location method: "+method)
        
        col.colocate()
        
        print col.points


commands = { 'plot' : plot_cmd,
             'info' : info_cmd,
             'col'  : col_cmd} 

def main():
    '''
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    '''
    from parse import parse_args
    import logging
    from datetime import datetime
    
    __setup_logging("cis.log", logging.INFO)
    
    arguments = parse_args()
    
    command = arguments.pop("command")
    
    # Log the input arguments so that the user can trace how a plot was created
    logging.info(datetime.now().strftime("%Y-%m-%d %H:%M")+ ": CIS "+ command + " got the following arguments: ")
    logging.info(arguments)
    
    commands[command](arguments)        
   
   
   
if __name__ ==  '__main__':
    main()
