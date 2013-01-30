"""
Module containing hdf file utility functions for the SD object
"""
from logilab.common import attrdict
import numpy as np

def read_hdf4_SD_variable(filename, name):
    """
    Reads a single SD from an HDF4 file. 
    
    Returns:
        A single SDS instance 
        
    Arguments:
        filename    -- The name (with path) of the HDF file to read.
        name       -- A variable (dataset) name to read from the
                       file. The names must appear exactly as in in the HDF file.
    """
    from pyhdf import SD

    # Open the file.
    datafile = SD.SD(filename)
    sds = datafile.select(name) # SDS object.
    
    return sds

def read_hdf4_SD(filename, names=None, datadict=None):
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
        datadic     -- Optional dictionary to add data to, otherwise a new, empty
                       dictionary is created
    
    """
    from pyhdf import SD

    # Open the file.
    datafile = SD.SD(filename)
    # List of required variable names.
    if names is None:
        names = datafile.datasets()
    # Create dictionary to hold data arrays for returning.
    if datadict is None:
        datadict = {}
    # Get data.
    for name in names:
        sds = datafile.select(name) # SDS object.
        datadict[name] = sds
    
    return datadict

def get_hdf_SD_file_datasets(filename):
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

def read_hdf4_SD_metadata(sds):
    "Retrieves long name and units from an sds instance"

    attributes = sds.attributes()
    longName = attributes.get('long_name')
    units = attributes.get('units')
    validRange = attributes.get('valid_range')
    return longName,units,validRange

def get_hdf4_SD_data(sds, calipso_scaling=False):
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

    data = __fill_missing_data(data, attributes)

    if calipso_scaling:
        data = __apply_scaling_factor_CALIPSO(data, attributes)
    else:
        data = __apply_scaling_factor_MODIS(data, attributes)

    return data

def __apply_scaling_factor_CALIPSO(data, attributes):
    '''
    Apply scaling factor Calipso data
    @param data:
    @param attributes:
    @return:
    '''
    offset  = attributes.get('add_offset', 0)   # Offsets and scaling.
    scale_factor = attributes.get('scale_factor', 1)
    data = (data/scale_factor) + offset
    return data

def __apply_scaling_factor_MODIS(data, attributes):
    '''
    Apply scaling factor for MODIS data
    @param data:
    @param attributes:
    @return:
    '''
    offset  = attributes.get('add_offset', 0)   # Offsets and scaling.
    scale_factor = attributes.get('scale_factor', 1)
    data = (data - offset) * scale_factor
    return data

def __fill_missing_data(data, attributes):
    '''
    Replace missing data with NaN

    @param data: raw data (numpy array) from sds instance
    @param attributes: Attributes from sds instance
    @return: A numpy array containing the raw data with missing data is replaced by NaN
    '''
    fill_value = attributes.get('_FillValue', None)  # Missing data.
    w_fill_mask = np.where(data == fill_value, np.nan, 1)
    data = data * w_fill_mask
    return data

