"""
Module containing hdf file utility functions for the SD object
"""
import logging
from cis.utils import create_masked_array_for_missing_values, listify
# Optional HDF import, if the module isn't found we defer raising ImportError until it is actually needed.
try:
    from pyhdf import SD
except ImportError:
    SD = None


def get_hdf_SD_file_variables(filename):
    """
    Get all the variables from an HDF SD file

    :param str filename: The filename of the file to get the variables from
    :returns: An OrderedDict containing the variables from the file
    """
    if not SD:
        raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

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


class HDF_SDS(object):
    """
    This class is used in place of the pyhdf.SD.SDS class to allow the file contents to be loaded at a later time
    rather than in this module read method (so that we can close the SD instances and free up file handles)
    """

    _sd = None
    _sds = None
    _filename = None
    _variable = None

    def __init__(self, filename, variable):
        self._filename = filename
        self._variable = variable

    def _open_sds(self):
        """
        Open the SDS file for reading
        """
        from pyhdf.SD import SD as SDS

        self._sd = SDS(self._filename)
        self._sds = self._sd.select(self._variable)

    def _close_sds(self):
        """
        Close the SDS file for reading

        NB: Exceptions thrown from here may hide an exception thrown in get(), info(), etc.
        """
        try:
            if self._sds is not None:
                self._sds.endaccess()
        finally:
            if self._sd is not None:
                self._sd.end()

    def get(self):
        """
        Call pyhdf.SD.SDS.get(), opening and closing the file
        """
        try:
            self._open_sds()
            data = self._sds.get()
            return data
        finally:
            self._close_sds()

    def attributes(self):
        """
        Call pyhdf.SD.SDS.attributes(), opening and closing the file
        """
        try:
            self._open_sds()
            attributes = self._sds.attributes()
            return attributes
        finally:
            self._close_sds()

    def info(self):
        """
        Call pyhdf.SD.SDS.info(), opening and closing the file
        """
        try:
            self._open_sds()
            info = self._sds.info()
            return info
        finally:
            self._close_sds()


def read(filename, variables=None, datadict=None):
    """
    Reads SD from a HDF4 file into a dictionary. 

    :param str filename: The name (with path) of the HDF file to read.
    :param iterable names: A sequence of variable (dataset) names to read from the
     file (default None, causing all variables to be read). The names must appear exactly as in in the HDF file.
    :param dict datadict: Optional dictionary to add data to, otherwise a new, empty dictionary is created
    :return: A dictionary containing data for requested variables. Missing data is replaced by NaN.
    """
    # Optional HDF import
    if not SD:
        raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

    # List of required variable names.
    # Open the file.
    datafile = None
    try:
        datafile = SD.SD(filename)
        sd_variables = list(datafile.datasets().keys())
    finally:
        if datafile is not None:
            datafile.end()

    if variables is None:
        requested_sd_variables = sd_variables
    else:
        requested_sd_variables = set(listify(variables)).intersection(set(sd_variables))

    # Create dictionary to hold data arrays for returning.
    if datadict is None:
        datadict = {}

    # Get data.
    for variable in requested_sd_variables:
        datadict[variable] = HDF_SDS(filename, variable)

    return datadict


def get_calipso_data(sds):
    """
    Reads raw data from an SD instance. Automatically applies the
    scaling factors and offsets to the data arrays found in Calipso data.

    :param sds: The specific sds instance to read
    :returns: A numpy array containing the raw data with missing data is replaced by NaN.
    """
    from cis.utils import create_masked_array_for_missing_data
    import numpy as np

    calipso_fill_values = {'Float_32': -9999.0,
                           # 'Int_8' : 'See SDS description',
                           'Int_16': -9999,
                           'Int_32': -9999,
                           'UInt_8': -127,
                           # 'UInt_16' : 'See SDS description',
                           # 'UInt_32' : 'See SDS description',
                           'ExtinctionQC Fill Value': 32768,
                           'FeatureFinderQC No Features Found': 32767,
                           'FeatureFinderQC Fill Value': 65535}

    data = sds.get()
    attributes = sds.attributes()

    # Missing data. First try 'fillvalue'
    missing_val = attributes.get('fillvalue', None)
    if missing_val is None:
        try:
            # Now try and lookup the fill value based on the data type
            missing_val = calipso_fill_values[attributes.get('format', None)]
        except KeyError:
            # Last guess
            missing_val = attributes.get('_FillValue', None)

    data = create_masked_array_for_missing_data(data, missing_val)

    # Now handle valid range mask
    valid_range = attributes.get('valid_range', None)
    if valid_range is not None:
        v_range = np.asarray(valid_range.split("..."), dtype=data.dtype)
        data = np.ma.masked_outside(data, *v_range)

    # Offsets and scaling.
    offset = attributes.get('add_offset', 0)
    scale_factor = attributes.get('scale_factor', 1)
    data = __apply_scaling_factor_CALIPSO(data, scale_factor, offset)

    return data


def get_data(sds, missing_values=None):
    """
    Reads raw data from an SD instance. Automatically applies the
    scaling factors and offsets to the data arrays often found in NASA HDF-EOS
    data (e.g. MODIS)

    :param sds: The specific sds instance to read
    :return: A numpy array containing the raw data with missing data is replaced by NaN.
    """
    data = sds.get()
    attributes = sds.attributes()

    # Missing data.
    if missing_values is None:
        missing_values = [attributes.get('_FillValue', None)]

    data = create_masked_array_for_missing_values(data, missing_values)

    # Offsets and scaling.
    offset = attributes.get('add_offset', 0)
    scale_factor = attributes.get('scale_factor', 1)
    data = __apply_scaling_factor_MODIS(data, scale_factor, offset)

    return data


def get_metadata(sds):
    from cis.data_io.ungridded_data import Metadata

    name = sds.info()[0]
    long_name = sds.attributes().get('long_name', None)
    shape = sds.info()[2]
    units = sds.attributes().get('units')
    valid_range = sds.attributes().get('valid_range')
    factor = sds.attributes().get('scale_factor')
    offset = sds.attributes().get('add_offset')
    missing = sds.attributes().get('_FillValue')

    # put the whole dictionary of attributes into 'misc'
    # so that other metadata of interest can still be retrieved if need be
    misc = sds.attributes()

    metadata = Metadata(name=name, long_name=long_name, shape=shape, units=units, range=valid_range,
                        factor=factor, offset=offset, missing_value=missing, misc=misc)

    return metadata


def __apply_scaling_factor_CALIPSO(data, scale_factor, offset):
    """
    Apply scaling factor (applicable to Calipso data) of the form:
    ``data = (data/scale_factor) + offset``

    :param data: A numpy array like object
    :param scale_factor:
    :param offset:
    :return: Scaled data
    """

    data = (data/scale_factor) + offset
    return data


def __apply_scaling_factor_MODIS(data, scale_factor, offset):
    """
    Apply scaling factor (applicable to MODIS data) of the form:
    ``data = (data - offset) * scale_factor``

    :param data: A numpy array like object
    :param scale_factor:
    :param offset:
    :return: Scaled data
    """
    data = (data - offset) * scale_factor
    return data
