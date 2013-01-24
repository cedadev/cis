#!/bin/env python2.7
'''
Main driver script for the Climate Intercomparison Suite
'''
import sys

MAXIMUM_NUMBER_OF_VARIABLES = 10

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
    
    main_arguments.pop("variable")
    
    # This currently assumes the variable is in each of the filenames specified,
    #  this may change in the future.
    if len(main_arguments["datafiles"]) > MAXIMUM_NUMBER_OF_VARIABLES:
        sys.stderr.write("Number of variables must be less than or equal to " + str(MAXIMUM_NUMBER_OF_VARIABLES) + "\n")
        exit(1)
    
    data = []
    try:
        for datafile in main_arguments["datafiles"]:
            data.append(read_variable(datafile["filename"], datafile["variable"]))
    except IrisError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except IOError as e:
        print "There was an error reading one of the files: "
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except ex.InvalidVariableError as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    
    
    plot_type = main_arguments.pop("type")
    output = main_arguments.pop("output")
    
    try:
        plot(data, plot_type, output, **main_arguments)
    except (ex.InvalidPlotTypeError, ex.InvalidPlotFormatError, ex.InconsistentDimensionsError, ex.InvalidFileExtensionError) as e:
        sys.stderr.write(str(e) + "\n")
        exit(1)
    except ValueError as e:
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
    from data_io.hdf import get_hdf_SD_file_variables

    variables = main_arguments.pop('variables', None)
    filename = main_arguments.pop('filename')
    
    try:
        file_variables = get_netcdf_file_variables(filename)
    except RuntimeError:
        file_variables = get_hdf_SD_file_variables(filename)
    
    if variables is not None:
        for variable in variables:
            try:
                # For hdf files this prints:
                # dimension names, dimension lengths, data type and number of variables
                print file_variables[variable]
            except KeyError:
                print("Variable '{0}' not found".format(variable))
    else:
        for item in file_variables:
            print item

def col_cmd(main_arguments):
    '''
    Main routine for handling calls to the 'col' command. 
        
    args:
        main_arguments:    The command line arguments (minus the col command)         
    '''
    from data_io.read import read_variable
    import jasmin_cis.exceptions as ex
    from iris.exceptions import IrisError
    from col import col, HyperPoint
    import numpy as np
    
    sample = main_arguments.pop("samplefilename")
    sample_data = read_variable(sample, 'rain')
    
    print sample_data
    
    for datafile in main_arguments.pop("datafiles"):
        variable = datafile['variable']
        filename = datafile['filename']
        data_dict = read_variable(filename,[variable]+['Latitude','Longitude'])
        
#        print data_dict
#        for key, val in data_dict.items():
#            print key
#            print val.data.shape
#            print val.data[:,:]
#            print val.data[1,1]

        # Pack the data into a list of x,y, val points to be passed to col
        points = []
        for (x,y), value in np.ndenumerate(data_dict[variable].data[1,:,:]):
            lat = data_dict['Latitude'].data[x,y]
            lon = data_dict['Longitude'].data[x,y]
            points.append(HyperPoint(lat,lon, val=value))
            
        for point in points:
            print point.lat, point.lon, point.val
    
        col_data = col(sample_data, points, datafile['method'])

    # output col_data > ?
        
commands = { 'plot' : plot_cmd,
             'info' : info_cmd,
             'col'  : col_cmd}

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
   
if __name__ ==  '__main__':
    '''
    The main method for the program.
    Sets up logging, parses the command line arguments and then calls the appropriate command with its arguments
    '''
    from parse import parse_args
    import logging
    from datetime import datetime
    
    setup_logging("cis.log", logging.INFO)
    
    arguments = parse_args()
    
    command = arguments.pop("command")
    
    # Log the input arguments so that the user can trace how a plot was created
    logging.info(datetime.now().strftime("%Y-%m-%d %H:%M")+ ": CIS "+ command + " got the following arguments: ")
    logging.info(arguments)
    
    commands[command](arguments) 
