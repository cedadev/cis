"""
Module containing hdf file utility functions for the SD object
"""
import logging
from cis.utils import listify
# Optional HDF import, if the module isn't found we defer raising ImportError until it is actually needed.
try:
    from pyhdf import SD
except ImportError:
    SD = None


def get_hdf_SD_file_variables(filename):
    """
    Get all the variables from an HDF SD file

    :param str filename: The filename of the file to get the variables from
    :return: An OrderedDict containing the variables from the file
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

    def __init__(self, filename, variable, start=None, count=None, stride=None):
        self._filename = filename
        self._variable = variable
        self._start = start
        self._count = count
        self._stride = stride

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

    def get(self, start=None, count=None, stride=None):
        """
        Call pyhdf.SD.SDS.get(), opening and closing the file
        """
        if start is None:
            start = self._start
        if count is None:
            count = self._count
        if stride is None:
            stride = self._stride
        try:
            self._open_sds()
            data = self._sds.get(start, count, stride)
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

    def dimensions(self):
        """
        Call pyhdf.SD.SDS.dimensions(), opening and closing the file
        """
        from collections import OrderedDict
        try:
            self._open_sds()
            var_description = self._sd.datasets()[self._variable]
            return OrderedDict(zip(var_description[0], var_description[1]))
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


def get_data(sds):
    """
    Reads raw data from an SD instance.

    :param sds: The specific sds instance to read
    :return: A numpy array containing the raw data with missing data is replaced by NaN.
    """
    from cis.utils import create_masked_array_for_missing_data
    from cis.data_io.netcdf import apply_offset_and_scaling
    import numpy as np

    data = sds.get()
    attributes = sds.attributes()

    # Apply Fill Value
    missing_value = attributes.get('_FillValue', None)
    if missing_value is not None:
        data = create_masked_array_for_missing_data(data, missing_value)

    # Check for valid_range
    valid_range = attributes.get('valid_range', None)
    if valid_range is not None:
        data = np.ma.masked_outside(data, *valid_range)

    # Offsets and scaling.
    add_offset = attributes.get('add_offset', 0.0)
    scale_factor = attributes.get('scale_factor', 1.0)
    logging.warning("Applying standard offset and scaling for dataset - this may not be appropriate for HDF_EOS data!")
    data = apply_offset_and_scaling(data, add_offset=add_offset, scale_factor=scale_factor)

    return data


def get_metadata(sds):
    from cis.data_io.ungridded_data import Metadata

    name = sds.info()[0]

    misc = sds.attributes()
    long_name = misc.pop('long_name', '')
    units = misc.pop('units', '')
    factor = misc.pop('scale_factor', None)
    offset = misc.pop('add_offset', None)
    missing = misc.pop('_FillValue', None)

    shape = sds.info()[2]

    metadata = Metadata(name=name, long_name=long_name, shape=shape, units=units,
                        factor=factor, offset=offset, missing_value=missing, misc=misc)

    return metadata
