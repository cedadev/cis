from data_io import hdf_sd as hdf_sd, hdf_vd

def read_hdf4(filename,variables):
    '''
        A wrapper method for reading raw data from hdf4 files. This returns a dictionary of io handles
         for each VD and SD data types.

        @param filename:     A name of a file to read
        @param variables:    List of variables to read from the files

        @return (sds_dict, vds_dict) A tuple of dictionaries, one for sds objects and another for vds
    '''
    from jasmin_cis.exceptions import InvalidVariableError, FileIOError
    from pyhdf.error import HDF4Error

    if not isinstance(variables,list): variables = [ variables ]

    try:
        sds_dict = hdf_sd.read(filename,variables)
        vds_dict = hdf_vd.read(filename,variables)
    except HDF4Error as e:
        raise FileIOError(str(e))

    for variable in variables:
        if variable not in sds_dict and variable not in vds_dict:
            raise InvalidVariableError("Could not find " + variable + " in file: " + filename)

    return sds_dict, vds_dict