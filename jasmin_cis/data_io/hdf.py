from data_io import hdf_sd as hdf_sd, hdf_vd
import jasmin_cis.utils as utils
import logging

def get_hdf4_file_variables(filename):
    '''
    Get all variables from a file containing ungridded data.
    Concatenate variable from both VD and SD data

    args:
        filename: The filename of the file to get the variables from

    '''
    SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)
    VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)

    return SD_vars, VD_vars

def __read_hdf4(filename,variables):
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


def read(filenames,variables):

    sdata = {}
    vdata = {}

    for filename in filenames:

        logging.debug("reading file: " + filename)

        try:
            # reading in all variables into a 2 dictionaries:
            # sdata, key: variable name, value: list of sds
            # vdata, key: variable name, value: list of vds
            sds_dict, vds_dict = __read_hdf4(filename,variables)
            for var in sds_dict.keys():
                utils.add_element_to_list_in_dict(sdata,var,sds_dict[var])
            for var in vds_dict.keys():
                utils.add_element_to_list_in_dict(vdata,var,vds_dict[var])

        except:
            print 'Error while reading file ', filename

    return sdata,vdata

def read_data(data_dict, data_type):
    if data_type=='VD':
        out =  utils.concatenate([hdf_vd.get_data(i) for i in data_dict ])
    if data_type=='SD':
        out =  utils.concatenate([hdf_sd.get_data(i) for i in data_dict ])
    return out

def read_metadata(data_dict, data_type):
    if data_type=='VD':
        out = hdf_vd.get_metadata(data_dict[0])
    if data_type=='SD':
        out = hdf_sd.get_metadata(data_dict[0])
    return out