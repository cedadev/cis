from jasmin_cis.data_io import hdf_sd as hdf_sd, hdf_vd
import jasmin_cis.utils as utils
import logging

def get_hdf4_file_variables(filename, data_type):
    """
    Get all variables from a file containing ungridded data.
    Concatenate variable from both VD and SD data

    :param filename: The filename of the file to get the variables from
    :param data_type: String representing the HDF data type, i.e. 'VD' or 'SD'. if None, both are computed.
    """

    SD_vars = VD_vars = None

    if data_type is None:
        SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)
        VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)
    else:
        if data_type.lower() == 'SD'.lower() or data_type.lower() == "all".lower():
            SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)

        if data_type.lower() == 'VD'.lower() or data_type.lower() == "all".lower():
            VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)

    return SD_vars, VD_vars


def get_hdf4_file_metadata(filename):
    """
    This returns a dictionary of file attributes, which often contains metadata information
    about the whole file. The value of each attribute can simply be a big string
    which will often need to be parsed manually thereafter.
    :param filename
    :return: dictionary of string attributes
    """
    from pyhdf.SD import SD
    return SD(filename).attributes()

def __read_hdf4(filename,variables):
    '''
        A wrapper method for reading raw data from hdf4 files. This returns a dictionary of io handles
         for each VD and SD data types.

        :param filename:     A name of a file to read
        :param variables:    List of variables to read from the files

        :return: (sds_dict, vds_dict) A tuple of dictionaries, one for sds objects and another for vds
    '''
    from jasmin_cis.exceptions import InvalidVariableError
    from pyhdf.error import HDF4Error

    variables = utils.listify(variables)

    try:
        sds_dict = hdf_sd.read(filename,variables)

        # remove the variables identified as SD (i.e. the keys in sds_dict)
        # no need to try looking for them as VD variable
        # AND this can cause a crash in some version/implementations of the core HDF4 libraries!

        # First create a copy of the list in order for the original list to be left intact when elements are removed from it
        # This enables the original list to be used when many files are read
        vdvariables = list(variables)
        for sds_dict_key in sds_dict:
            vdvariables.remove(sds_dict_key)

        vds_dict = hdf_vd.read(filename, vdvariables)
    except HDF4Error as e:
        joined_up_message = "".join(e)
        raise IOError(joined_up_message)

    for variable in variables:
        if variable not in sds_dict and variable not in vds_dict:
            raise InvalidVariableError("Could not find " + variable + " in file: " + filename)

    return sds_dict, vds_dict


def read(filenames,variables):

    sdata = {}
    vdata = {}

    for filename in filenames:

        logging.debug("reading file: " + filename)

        # reading in all variables into a 2 dictionaries:
        # sdata, key: variable name, value: list of sds
        # vdata, key: variable name, value: list of vds
        sds_dict, vds_dict = __read_hdf4(filename,variables)
        for var in sds_dict.keys():
            utils.add_element_to_list_in_dict(sdata,var,sds_dict[var])
        for var in vds_dict.keys():
            utils.add_element_to_list_in_dict(vdata,var,vds_dict[var])

    return sdata,vdata

def read_data(data_dict, data_type, missing_values=None):
    if data_type=='VD':
        out =  utils.concatenate([hdf_vd.get_data(i, missing_values=missing_values) for i in data_dict ])
    if data_type=='SD':
        out =  utils.concatenate([hdf_sd.get_data(i, missing_values=missing_values) for i in data_dict ])
    return out

def read_metadata(data_dict, data_type):
    if data_type=='VD':
        out = hdf_vd.get_metadata(data_dict[0])
    if data_type=='SD':
        out = hdf_sd.get_metadata(data_dict[0])
    return out




