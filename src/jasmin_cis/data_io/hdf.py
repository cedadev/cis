"""
Module containing hdf file functions
"""
from pyhdf import SD
from pyhdf import HDF
import numpy as np

def read_hdf4(filename, names=None, calipso_scaling=False, vdata=False, datadict=None):
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
        vdata       -- If set, reads in cloudsat data from the vdata style 
                       hdf file. For 2C-PRECIP-COLUMN.  Reads in dictionary of 
                       numpy arrays
        datadic     -- Optional dictionary to add data to, otherwise a new, empty
                       dictionary is created
    
    Notes for IDL users:
        This function is similar to read_hdf4.pro.
        Some of the read_hdf4.pro keyword options are not currently implemented
        here: quiet, info, global_attributes, variable_attributes, vdata..
        
    IDL inspiration:
        /home/crun/eodg/idl/hdf/read_hdf4.pro
        by G Thomas and B S Grandey.
        
    Python implementation authors and history:
        2010-06-23  B S Grandey.
        2010-10-15  E R I Gryspeerdt  - Added some vdata support
        
    """
       
    if not vdata: 
        # MODIS/Calipso data
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
            data = sds.get()    # Extract raw data.
            attributes = sds.attributes()
            fillvalue = attributes.get('_FillValue', None)  # Missing data.
            wfill_mask = np.where(data == fillvalue, np.nan, 1)
            data = data * wfill_mask
            offset  = attributes.get('add_offset', 0)   # Offsets and scaling.
            scalefactor = attributes.get('scale_factor', 1)
            if calipso_scaling:
                data = (data/scalefactor) + offset      # Calipso.
            else:
                data = (data - offset) * scalefactor    # MODIS.
            datadict[name] = data
    else:
        # CloudSatPRECIP data
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

def get_hdf_file_variables(filename, vdata=False):
    '''
    Get all the variables from an HDF file
    
    args:
        filename: The filename of the file to get the variables from
    
    returns:
        An OrderedDict containing the variables from the file
    '''
    if not vdata: 
        # MODIS/Calipso data
        # Open the file.
        datafile = SD.SD(filename)
        # List of required variable names.
        names = datafile.datasets()
    else:  
        # CloudSatPRECIP data
        # Open file
        datafile = HDF(filename)
        vs =  datafile.vstart()
        # List of required variable names
        names = vs.vdatainfo()
        names = zip(*names)
        names = names[0]
        vs.end()
        datafile.close()
    return names
    