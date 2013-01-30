"""
Module containing hdf file utility functions for the VD object
"""
import numpy as np

def get_hdf_VD_file_variables(filename):
    '''
    Get all the variables from an HDF VD file

    args:
        filename: The filename of the file to get the variables from

    returns:
        An OrderedDict containing the variables from the file
    '''
    from pyhdf.HDF import HDF
    from pyhdf.VS import VS

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


def read_hdf4_VD(filename, names=None, datadict=None):
    """
    Reads VD from a HDF4 file into a dictionary.

    Returns:
        A dictionary containing data references for requested variables.

    Arguments:
        filename    -- The name (with path) of the HDF file to read.
        names       -- A sequence of variable (dataset) names to read from the
                       file (default None, causing all variables to be read).
                       The names must appear exactly as in in the HDF file.
        datadic     -- Optional dictionary to add data to, otherwise a new, empty
                       dictionary is created

    """
    from pyhdf.HDF import HDF

    # Open file
    datafile = HDF(filename)
    vs =  datafile.vstart()
    # List of required variable names
    if names is None:
        names = vs.vdatainfo()
        names = zip(*names)
        names = names[0]
    if datadict is None:
        datadict = {}
    for name in names:
        vd = vs.attach(name)
        datadict[name] = vd
        # NOTE that this doesn't now detach vs or close the file - I'm not sure where this should
        #  happen - if at all

    return datadict


def get_hdf4_VD_data(vd):
    """
    Reads VD from a HDF4 file into a dictionary.

    Returns:
        A dictionary containing data for requested variables.
        Missing data is replaced by NaN.

    Arguments:
        vd -- the data handle to read off

    """
    data = vd.read(nRec = vd.inquire()[0])
    for x in range(0,len(data)):
        data[x] = data[x][0]
    data = np.array(data)
    try: #Deal with missing data
        missingval = vd.attrinfo()['missing'][2]
        wfillmask = 0
        wfillmask = np.where(data == missingval, np.nan, 1)
        data = data * wfillmask
    except KeyError:
        pass

    return data