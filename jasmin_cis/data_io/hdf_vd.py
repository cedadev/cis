"""
Module containing hdf file utility functions for the VD object
"""
import numpy as np
from pyhdf.HDF import *
from pyhdf.VS import *
from collections import namedtuple
import logging
from jasmin_cis.utils import create_masked_array_for_missing_values, listify


class VDS(namedtuple('VDS',['filename','variable'])):
    pass

def get_hdf_VD_file_variables(filename):
    '''
    Get all the variables from an HDF VD file

    args:
        filename: The filename of the file to get the variables from

    returns:
        An OrderedDict containing the variables from the file
    '''
    variables = None
    try:
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
    except:
        logging.error("Error while reading VD data")

    return variables

def read(filename, variables=None, datadict=None):

    if datadict == None:
        datadict = {}

    variables = listify(variables)

    vs = None
    datafile = None
    try:
        datafile = HDF(filename)
        vs = datafile.vstart()

        for variable in variables:
            try:
                vd = vs.attach(variable)
                vd.detach()
                datadict[variable] = VDS(filename, variable)
            except:
                # ignore variable that failed
                pass
    finally:
        if vs is not None:
            vs.end()
        if datafile is not None:
            datafile.close()

    return datadict

def get_data(vds, first_record=False, missing_values=None):

    # get file and variable reference from tuple
    filename = vds.filename
    variable = vds.variable

    try:
        datafile = HDF(filename)
    except HDF4Error as e:
        raise IOError(e)

    vs = datafile.vstart()

    if first_record:
        vd = vs.attach(vs.next(-1))
        vd.setfields(variable)
        data = vd.read()
    else:
        # get data for that variable
        vd = vs.attach(variable)
        data = vd.read(nRec = vd.inquire()[0])

    # create numpy array from data
    data = np.array(data).flatten()

    # dealing with missing data
    if missing_values is None:
        missing_values = [__get_attribute_value(vd, 'missing')]

    data = create_masked_array_for_missing_values(data,missing_values)

    #np.set_printoptions(threshold=np.nan)
    #print data

    # detach and close
    vd.detach()
    vs.end()
    datafile.close()

    return data

def get_metadata(vds):
    from jasmin_cis.data_io.ungridded_data import Metadata

    # get file and variable reference from tuple
    filename = vds.filename
    variable = vds.variable

    datafile = HDF(filename)
    vs =  datafile.vstart()

    # get data for that variable
    vd = vs.attach(variable)

    name = variable
    long_name = __get_attribute_value(vd, 'long_name')
    shape = [len(vd.read(nRec = vd.inquire()[0]))] #VD data are always 1D, so the shape is simply the length of the data vector
    units = __get_attribute_value(vd, 'units')
    valid_range = __get_attribute_value(vd, 'valid_range')
    factor = __get_attribute_value(vd, 'factor')
    offset = __get_attribute_value(vd, 'offset')
    missing = __get_attribute_value(vd, 'missing')

    # put the whole dictionary of attributes into 'misc'
    # so that other metadata of interest can still be retrieved if need be
    misc = vd.attrinfo()

    metadata = Metadata( name=name, long_name=long_name, shape=shape, units=units, range=valid_range,
                            factor=factor, offset=offset, missing_value=missing, misc=misc)

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