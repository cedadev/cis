"""
Module containing hdf file utility functions for the SD object
"""
import logging
from jasmin_cis.utils import create_masked_array_for_missing_values


def get_hdf_SD_file_variables(filename):
    '''
    Get all the variables from an HDF SD file

    args:
        filename: The filename of the file to get the variables from

    returns:
        An OrderedDict containing the variables from the file
    '''
    from pyhdf import SD

    variables = None

    try:
        # Open the file.
        datafile = SD.SD(filename)
        # List of required variable names.
        variables = datafile.datasets()
        # Close the file
        datafile.end()
    except:
        logging.error("Error while reading SD data")

    return variables


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


def get_calipso_data(sds):
    """
    Reads raw data from an SD instance. Automatically applies the
    scaling factors and offsets to the data arrays found in Calipso data.

    Returns:
        A numpy array containing the raw data with missing data is replaced by NaN.

    Arguments:
        sds        -- The specific sds instance to read

    """
    from jasmin_cis.utils import create_masked_array_for_missing_data

    calipso_fill_values = {'Float_32' : -9999.0,
                           #'Int_8' : 'See SDS description',
                           'Int_16' : -9999,
                           'Int_32' : -9999,
                           'UInt_8' : -127,
                           #'UInt_16' : 'See SDS description',
                           #'UInt_32' : 'See SDS description',
                           'ExtinctionQC Fill Value' : 32768,
                           'FeatureFinderQC No Features Found' : 32767,
                           'FeatureFinderQC Fill Value' : 65535}

    data = sds.get()
    attributes = sds.attributes()

    # Missing data.
    missing_val = attributes.get('fillvalue', None)
    if missing_val is None:
        try:
            missing_val = calipso_fill_values[attributes.get('format', None)]
        except KeyError:
            # Last guess
            missing_val = attributes.get('_FillValue', None)

    data = create_masked_array_for_missing_data(data, missing_val)

    # Offsets and scaling.
    offset  = attributes.get('add_offset', 0)
    scale_factor = attributes.get('scale_factor', 1)
    data = __apply_scaling_factor_CALIPSO(data, scale_factor, offset)

    return data


def get_data(sds, missing_values=None):
    """
    Reads raw data from an SD instance. Automatically applies the
    scaling factors and offsets to the data arrays often found in NASA HDF-EOS
    data (e.g. MODIS)

    Returns:
        A numpy array containing the raw data with missing data is replaced by NaN.

    Arguments:
        sds        -- The specific sds instance to read

    """
    from jasmin_cis.utils import create_masked_array_for_missing_data

    data = sds.get()
    attributes = sds.attributes()

    # Missing data.
    if missing_values is None:
        missing_values = [attributes.get('_FillValue', None)]

    data = create_masked_array_for_missing_values(data,missing_values)

    # Offsets and scaling.
    offset  = attributes.get('add_offset', 0)
    scale_factor = attributes.get('scale_factor', 1)
    data = __apply_scaling_factor_MODIS(data, scale_factor, offset)

    return data


def get_metadata(sds):
    from jasmin_cis.data_io.ungridded_data import Metadata

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

