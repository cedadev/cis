"""
Module containing hdf file utility functions for the SD object
"""

from jasmin_cis.data_io.hdf_util import __fill_missing_data
import numpy as np

def get_hdf_SD_file_variables(filename):
    '''
    Get all the variables from an HDF SD file

    args:
        filename: The filename of the file to get the variables from

    returns:
        An OrderedDict containing the variables from the file
    '''
    from pyhdf import SD

    # Open the file.
    datafile = SD.SD(filename)
    # List of required variable names.
    return datafile.datasets()

def read(filename, variables=None, datadict=None):
    """
    Reads SD from a HDF4 file into a dictionary. 
    
    Returns:
        A dictionary containing data for requested variables.
        Missing data is replaced by NaN.
        
    Arguments:
        filename    -- The name (with path) of the HDF file to read.
        names       -- A sequence of variable (dataset) names to read from the
                       file (default None, causing all variables to be read).
                       The names must appear exactly as in in the HDF file.
        datadict     -- Optional dictionary to add data to, otherwise a new, empty
                       dictionary is created
    
    """
    from pyhdf import SD

    # Open the file.
    datafile = SD.SD(filename)


    # List of required variable names.
    if variables is None:
        variables = datafile.datasets().keys()
    if not isinstance(variables,list): variables = [ variables ]

    # Create dictionary to hold data arrays for returning.
    if datadict is None:
        datadict = {}

    # Get data.
    for variable in variables:
        try:
            sds = datafile.select(variable) # SDS object.
            datadict[variable] = sds
        except:
            # ignore variable that failed
            pass
    
    return datadict


def get_data(sds, calipso_scaling=False):
    """
    Reads raw data from an SD instance. Automatically applies the
    scaling factors and offsets to the data arrays often found in NASA HDF-EOS
    data. (Used for e.g. MODIS/Calipso data)

    Returns:
        A numpy array containing the raw data with missing data is replaced by NaN.

    Arguments:
        sds        -- The specific sds instance to read
        calipso_scaling -- If set, the code will apply offsets and scaling in
                       the order used by CALIPSO data (rather than the MODIS
                       method). The two methods are:
                       MODIS:   (data - offset) * scale_factor
                       CALIPSO: data/scalefactor + offset.

    """
    data = sds.get()
    attributes = sds.attributes()

    # Missing data.
    missing_val = attributes.get('_FillValue', None)
    data = __fill_missing_data(data, missing_val)

    # Offsets and scaling.
    offset  = attributes.get('add_offset', 0)
    scale_factor = attributes.get('scale_factor', 1)
    if calipso_scaling:
        data = __apply_scaling_factor_CALIPSO(data, scale_factor, offset)
    else:
        data = __apply_scaling_factor_MODIS(data, scale_factor, offset)

    return data


def get_metadata(sds):
    from ungridded_data import Metadata

    name = sds.info()[0]
    long_name = sds.attributes().get('long_name',None)
    shape = sds.info()[2]
    units = sds.attributes().get('units')
    valid_range = sds.attributes().get('valid_range')
    factor = sds.attributes().get('scale_factor')
    offset = sds.attributes().get('add_offset')
    missing = sds.attributes().get('_FillValue')

    # put the whole dictionary of attributes into 'misc'
    # so that other metadata of interest can still be retrieved if need be
    misc = sds.attributes()

    metadata = Metadata( name=name, long_name=long_name, shape=shape, units=units, range=valid_range,
        factor=factor, offset=offset, missing_value=missing, misc=misc)


    return metadata


def __apply_scaling_factor_CALIPSO(data, scale_factor, offset):
    '''
    Apply scaling factor Calipso data
    @param data:
    @param scale_factor:
    @param offset:
    @return:
    '''

    data = (data/scale_factor) + offset
    return data

def __apply_scaling_factor_MODIS(data, scale_factor, offset):
    '''
    Apply scaling factor for MODIS data
    @param data:
    @param scale_factor:
    @param offset:
    @return:
    '''
    data = (data - offset) * scale_factor
    return data

