"""
Module containing hdf file utility functions for the VD object
"""
import numpy as np
# Optional HDF import, if the module isn't found we defer raising ImportError until it is actually needed.
try:
    from pyhdf.HDF import HDF, HDF4Error
    from pyhdf.VS import VS
except ImportError:
    HDF = None

from collections import namedtuple
import logging
from cis.utils import create_masked_array_for_missing_values, listify


class VDS(namedtuple('VDS', ['filename', 'variable'])):
    pass


def get_hdf_VD_file_variables(filename):
    """
    Get all the variables from an HDF VD file

    :param filename: The filename of the file to get the variables from
    :return: An OrderedDict containing the variables from the file
    """
    variables = None
    if not HDF:
        raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

    try:
        # Open file
        datafile = HDF(filename)
        vs = datafile.vstart()
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
    """
    Given a filename and a list of file names return a dictionary of VD data handles

    :param filename: full path to a single HDF4 file
    :param variables: A list of variables to read, if no variables are given, no variables are read
    :param datadict: A dictionary of variable name, data handle pairs to be appended to
    :return: An updated datadict with any new variables appended.
    """

    if not HDF:
        raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

    if datadict is None:
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
    """
    Actually read the data from the VDS handle. We shouldn't need to check for HDF being installed here because the
    VDS object which is being passed to us can only have come from pyhdf.

    :param vds:
    :param first_record:
    :param missing_values:
    :return:
    """

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
        data = vd.read(nRec=vd.inquire()[0])

    # create numpy array from data
    data = np.array(data).flatten()

    # dealing with missing data
    if missing_values is None:
        missing_values = [_get_attribute_value(vd, 'missing')]

    data = create_masked_array_for_missing_values(data, missing_values)

    # detach and close
    vd.detach()
    vs.end()
    datafile.close()

    return data


def get_metadata(vds):
    from cis.data_io.ungridded_data import Metadata

    # get file and variable reference from tuple
    filename = vds.filename
    variable = vds.variable

    datafile = HDF(filename)
    vs = datafile.vstart()

    # get data for that variable
    vd = vs.attach(variable)

    name = variable
    misc = vd.attrinfo()

    long_name = _pop_attribute_value(misc, 'long_name', '')
    units = _pop_attribute_value(misc, 'units', '')
    factor = _pop_attribute_value(misc, 'factor')
    offset = _pop_attribute_value(misc, 'offset')
    missing = _pop_attribute_value(misc, 'missing')

    # VD data are always 1D, so the shape is simply the length of the data vector
    shape = [len(vd.read(nRec=vd.inquire()[0]))]

    # Tidy up the rest of the data in misc:
    misc = {k: v[2] for k, v in misc.items()}

    metadata = Metadata(name=name, long_name=long_name, shape=shape, units=units,
                        factor=factor, offset=offset, missing_value=missing, misc=misc)

    # detach and close
    vd.detach()
    vs.end()
    datafile.close()

    return metadata


def _get_attribute_value(vd, name, default=None):
    val = vd.attrinfo().get(name, None)
    # if the attribute is not present
    if val is None:
        return default
    else:
        # attrinfo() returns a tuple in which the value of interest is the 3rd item, hence the '[2]'
        return val[2]


def _pop_attribute_value(att_dict, name, default=None):
    val = att_dict.pop(name, None)
    # if the attribute is not present
    if val is None:
        return default
    else:
        # attrinfo() returns a tuple in which the value of interest is the 3rd item, hence the '[2]'
        return val[2]
