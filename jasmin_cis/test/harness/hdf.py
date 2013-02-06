"""
Module containing hdf file functions
"""

from pyhdf import SD
import numpy as np
from pyhdf.HDF import *
from pyhdf.VS import *

def read_hdf4(filename, names=None, calipso_scaling=None, vdata=None,datadict=None):
    """
    Reads data from a HDF4 file into a dictionary. Automatically applies the
    scaling factors and offsets to the data arrays often found in NASA HDF-EOS
    data.
    
    Returns:
        A dictionary containing data for requested variables.
        Missing data is replaced by NaN.
        
    Arguments:
        filename    -- The name (with path) of the HDF file to read.
        names       -- A sequence of variable (dataset) names to read from the
                       file (default None, causing all variables to be read).
                       The names must appear exactly as in in the HDF file.

        calipso_scaling -- If set, the code will apply offsets and scaling in
                       the order used by CALIPSO data (rather than the MODIS
                       method). The two methods are:
                       MODIS:   (data - offset) * scale_factor
                       CALIPSO: data/scalefactor + offset.
        cloudsatPRECIP -- If set, reads in cloudsat data from the vdata style 
                       hdf file. For 2C-PRECIP-COLUMN.  Reads in dictionary of 
                       numpy arrays
    """

    if not vdata:
    # MODIS/Calipso data
    # Open the file.
        datafile = SD.SD(filename)
        # List of required variable names.
        if not names:
            names = datafile.datasets()
            # Create dictionary to hold data arrays for returning.
        if datadict==None:
            datadict = {}
            # Get data.
        for name in names:
            sds = datafile.select(name) # SDS object.
            data = sds.get()    # Extract raw data.
            attributes = sds.attributes()
            fillvalue = attributes.get('_FillValue', None)  # Missing data.
            wfill_mask = np.where(data == fillvalue, np.nan, 1)
            data = data * wfill_mask
            offset  = attributes.get('add_offset', 0)   # Offsets and scaling.
            scalefactor = attributes.get('scale_factor', 1)
            if not calipso_scaling:
                data = (data - offset) * scalefactor    # MODIS.
            else:
                data = (data/scalefactor) + offset      # Calipso.
            datadict[name] = data

    else:
        # CloudSatPRECIP data
        # Open file
        datafile = HDF(filename)
        vs =  datafile.vstart()
        # List of required variable names
        if not names:
            names = vs.vdatainfo()
            names = zip(*names)
            names = names[0]
        if datadict == None:
            datadict = {}
        failednames = []
        for name in names:
            try:
                vd = vs.attach(name)
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
                datadict[name] = data
                vd.detach()
            except:
                failednames.append(name)
        vs.end()
        datafile.close()
        if len(failednames) > 0:
            datadict = read_hdf4(filename,failednames,datadict=datadict)

    return datadict

def read_hdf4_metadata(filename,name):
    '''Retrieves long name and units from hdf4 file, for a single variable.'''
    datafile = SD.SD(filename)
    sds =datafile.select(name)
    attributes = sds.attributes()
    longName = attributes.get('long_name')
    units = attributes.get('units')
    validRange = attributes.get('valid_range')
    return longName,units,validRange




