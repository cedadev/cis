"""
Module containing hdf file utility functions for the VD object
"""
import numpy as np
from pyhdf.HDF import *
from pyhdf.VS import *

from jasmin_cis.data_io.hdf_util import __fill_missing_data

def get_hdf_VD_file_variables(filename):
    '''
    Get all the variables from an HDF VD file

    args:
        filename: The filename of the file to get the variables from

    returns:
        An OrderedDict containing the variables from the file
    '''

    # Open file
    datafile = HDF(filename)
    vs =  datafile.vstart()
    # List of required variable names
    names = vs.vdatainfo()
    # This returns a list of tuples, so convert into a dictionary for easy lookup
    variables = {}
    for var in names:
        variables[var[0]] = var[1:]
    # Close file
    vs.end()
    datafile.close()
    return variables

def read_vds(filename, variables=None, datadict=None):

    if datadict == None:
        datadict = {}

    datafile = HDF(filename)
    vs =  datafile.vstart()

    for variable in variables:
        try:
            vd = vs.attach(variable)
            vd.detach()
            datadict[variable] = filename, variable
        except:
            # ignore variable that failed
            print "--Could not find " + variable

    vs.end()
    datafile.close()

    return datadict

def get_data(vds):

    # get file and variable reference from tuple
    filename = vds[0];
    variable = vds[1];

    datafile = HDF(filename)
    vs =  datafile.vstart()

    # get data for that variable
    vd = vs.attach(variable)
    data = vd.read(nRec = vd.inquire()[0])

    # create numpy array from data
    for x in range(0,len(data)):
        data[x] = data[x][0]
    data = np.array(data)

    #Deal with missing data
    try:
        missing_val = vd.attrinfo()['missing'][2]
        data = __fill_missing_data(data,missing_val)
    except KeyError:
        pass

    # detach and close
    vd.detach()
    vs.end()
    datafile.close()

    return data

def get_metadata(vds):
    pass
