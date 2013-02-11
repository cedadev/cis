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

def read(filename, variables=None, datadict=None):

    if datadict == None:
        datadict = {}

    if not isinstance(variables,list): variables = [ variables ]

    datafile = HDF(filename)
    vs =  datafile.vstart()

    for variable in variables:
        try:
            vd = vs.attach(variable)
            vd.detach()
            datadict[variable] = filename, variable
        except:
            # ignore variable that failed
            pass

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
    from ungridded_data import Metadata

    # get file and variable reference from tuple
    filename = vds[0];
    variable = vds[1];

    datafile = HDF(filename)
    vs =  datafile.vstart()

    # get data for that variable
    vd = vs.attach(variable)

    name = variable
    long_name = __get_attribute_value(vd, 'long_name')
    shape = [len(vd.read(nRec = vd.inquire()[0]))] #VD data are always 1D, so the shape is simply the length of the data vector
    units = __get_attribute_value(vd, 'units')
    range = __get_attribute_value(vd, 'valid_range')
    factor = __get_attribute_value(vd, 'factor')
    offset = __get_attribute_value(vd, 'offset')
    missing = __get_attribute_value(vd, 'missing')

    # put the whole dictionary of attributes into 'misc'
    # so that other metadata of interest can still be retrieved if need be
    misc = vd.attrinfo()

    metadata = Metadata(name, long_name, shape, units, range, factor, offset, missing, misc)

    # detach and close
    vd.detach()
    vs.end()
    datafile.close()

    return metadata

def __get_attribute_value(vd, name):

    val = vd.attrinfo().get(name,None)
    # if the attribute is not present
    if val is None:
        return val
    else:
        #attrinfo() returns a tuple in which the value of interest is the 3rd item, hence the '[2]'
        return val[2]