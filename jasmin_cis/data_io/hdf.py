"""
Module containing hdf file utility functions
"""
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
        calipso_scaling -- If set, the code will apply offsets and scaling in
                       the order used by CALIPSO data (rather than the MODIS
                       method). The two methods are:
                       MODIS:   (data - offset) * scale_factor
                       CALIPSO: data/scalefactor + offset.
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
    
    return data

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
    from pyhdf import HDF
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
    # This returns a list of tuples, so convert into a dictonary for easy lookup
    variables = {}
    for var in names:
        variables[var[0]] = var[1:]
    # Close file
    vs.end()
    datafile.close()
    return variables
        
def read_hdf4_SD_metadata(sds):
    "Retrieves long name and units from an sds instance"

    attributes = sds.attributes()
    longName = attributes.get('long_name')
    units = attributes.get('units')
    validRange = attributes.get('valid_range')
    return longName,units,validRange
    