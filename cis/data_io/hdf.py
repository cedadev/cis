from cis.data_io import hdf_sd as hdf_sd, hdf_vd
import cis.utils as utils
import logging


def get_hdf4_file_variables(filename, data_type=None):
    """
    Get all variables from a file containing ungridded data.
    Concatenate variable from both VD and SD data

    :param filename: The filename of the file to get the variables from
    :param data_type: String representing the HDF data type, i.e. 'VD' or 'SD'. if None, both are computed.
    """

    SD_vars = VD_vars = None

    if data_type is None or data_type.lower() == "sd":
        SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)
    elif data_type is None or data_type.lower() == "vd":
        VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)
    else:
        raise ValueError("Invalid data-type: %s, HDF variables must be VD or SD only" % data_type)

    return SD_vars, VD_vars


def get_hdf4_file_metadata(filename):
    """
    This returns a dictionary of file attributes, which often contains metadata information
    about the whole file. The value of each attribute can simply be a big string
    which will often need to be parsed manually thereafter.
    :param filename
    :return: dictionary of string attributes
    """
    # Optional HDF import, if the module isn't found we defer raising ImportError until it is actually needed.
    try:
        from pyhdf.SD import SD
    except ImportError:
        raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

    return SD(filename).attributes()


def _read_hdf4(filename, variables):
    """
        A wrapper method for reading raw data from hdf4 files. This returns a dictionary of io handles
         for each VD and SD data types.

        :param filename:     A name of a file to read
        :param variables:    List of variables to read from the files

        :return: (sds_dict, vds_dict) A tuple of dictionaries, one for sds objects and another for vds
    """
    from cis.exceptions import InvalidVariableError
    from pyhdf.error import HDF4Error

    variables = utils.listify(variables)

    # I'd rather not have to make this check but for pyhdf 0.9.0 and hdf 4.2.9 on OS X the c-level read routine will at
    # some point call exit(138) when reading valid netcdf files (rather than returning a negative status).
    if not filename.endswith('.hdf'):
        raise IOError("Tried to read non HDF file: {}".format(filename))

    try:
        sds_dict = hdf_sd.read(filename, variables)

        # remove the variables identified as SD (i.e. the keys in sds_dict)
        # no need to try looking for them as VD variable
        # AND this can cause a crash in some version/implementations of the core HDF4 libraries!

        # First create a copy of the list in order for the original list to be left intact when elements are removed
        # from it, this enables the original list to be used when many files are read
        vdvariables = list(variables)
        for sds_dict_key in sds_dict:
            vdvariables.remove(sds_dict_key)

        vds_dict = hdf_vd.read(filename, vdvariables)
    except HDF4Error as e:
        raise IOError(str(e))

    for variable in variables:
        if variable not in sds_dict and variable not in vds_dict:
            raise InvalidVariableError("Could not find " + variable + " in file: " + filename)

    return sds_dict, vds_dict


def read(filenames, variables):

    sdata = {}
    vdata = {}

    for filename in filenames:

        logging.debug("reading file: " + filename)

        # reading in all variables into a 2 dictionaries:
        # sdata, key: variable name, value: list of sds
        # vdata, key: variable name, value: list of vds
        sds_dict, vds_dict = _read_hdf4(filename, variables)
        for var in list(sds_dict.keys()):
            utils.add_element_to_list_in_dict(sdata, var, sds_dict[var])
        for var in list(vds_dict.keys()):
            utils.add_element_to_list_in_dict(vdata, var, vds_dict[var])

    return sdata, vdata


def read_data(data_list, read_function):
    """
    Wrapper for calling an HDF reading function for each dataset, and then concatenating the result.

    :param list data_list: A list of data objects to read
    :param callable or str read_function: A function for reading the data, or 'SD' or 'VD' for default reading routines.
    :return: A single numpy array of concatenated data values.
    """
    if callable(read_function):
        out = utils.concatenate([read_function(i) for i in data_list])
    elif read_function == 'VD':
        out = utils.concatenate([hdf_vd.get_data(i) for i in data_list])
    elif read_function == 'SD':
        out = utils.concatenate([hdf_sd.get_data(i) for i in data_list])
    else:
        raise ValueError("Invalid read-function: {}, please supply a callable read "
                         "function, 'VD' or 'SD' only".format(read_function))
    return out


def read_metadata(data_dict, data_type):
    if data_type == 'VD':
        out = hdf_vd.get_metadata(data_dict[0])
    elif data_type == 'SD':
        out = hdf_sd.get_metadata(data_dict[0])
    else:
        raise ValueError("Invalid data-type: %s, HDF variables must be VD or SD only" % data_type)
    return out
