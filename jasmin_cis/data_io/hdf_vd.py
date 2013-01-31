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

def read_vds(filename, names=None, datadict=None):
    pass

def get_data(vds):
    pass

def get_metadata(vds):
    pass

def get_hdf4_VD_data(filename, variables=None, datadict=None):
    '''

    @param filename:
    @param variables:
    @param datadict:
    @return:
    '''
    datafile = HDF(filename)
    vs =  datafile.vstart()

    # List of required variable names
    if not variables:
        variables = vs.vdatainfo()
        variables = zip(*variables)
        variables = variables[0]

    # initialise dictionary
    if datadict == None:
        datadict = {}

    # loop over every variable names
    for name in variables:

        # get data for that variable
        vd = vs.attach(name)
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

        # put data in dictionary
        datadict[name] = data

        # detach
        vd.detach()

    # close
    vs.end()
    datafile.close()

    return datadict

