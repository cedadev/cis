import logging


def get_aeronet_file_variables(filename):
    import linecache

    vars = linecache.getline(filename, 5).split(",")
    vars_dict = {}
    for var in vars:
        var = var.strip()
        vars_dict[var] = var
    return vars_dict


def load_multiple_aeronet(fnames, variables=None):
    from cis.utils import add_element_to_list_in_dict, concatenate

    adata = {}

    for filename in fnames:
        logging.debug("reading file: " + filename)

        # reading in all variables into a dictionary:
        # a_dict, key: variable name, value: list of masked arrays
        a_dict = load_aeronet(filename, variables)
        for var in a_dict.keys():
            add_element_to_list_in_dict(adata, var, a_dict[var])

    for var in adata.keys():
        adata[var] = concatenate(adata[var])

    return adata


def load_aeronet(fname, variables=None):
    """
    loads aeronet lev 2.0 csv file.

        Originally from http://code.google.com/p/metamet/
        License: GNU GPL v3

    :param fname: data file name
    :param keep_fields: A list of variables to return
    :return: A
    """
    import numpy as np
    from numpy import ma
    from datetime import datetime, timedelta
    from cis.time_util import cis_standard_time_unit
    from cis.exceptions import InvalidVariableError

    std_day = cis_standard_time_unit.num2date(0)

    def date2daynum(datestr):
        the_day = datetime(int(datestr[-4:]), int(datestr[3:5]), int(datestr[:2]))
        return float((the_day - std_day).days)

    def time2fractionalday(timestr):
        td = timedelta(hours=int(timestr[:2]), minutes=int(timestr[3:5]), seconds=int(timestr[6:8]))
        return td.total_seconds()/(24.0*60.0*60.0)

    try:
        rawd = np.genfromtxt(fname, skip_header=5, delimiter=',', names=get_aeronet_file_variables(fname).keys(),
                             converters={0: date2daynum, 1: time2fractionalday, 'Last_Processing_Date': date2daynum},
                             dtype=np.float64, missing_values='N/A', usemask=True)
    except (StopIteration, IndexError) as e:
        raise IOError(e)

    lend = len(rawd)
    # The date and time column are already in days since cis standard time, and fractional days respectively, so we can 
    # just add them together
    # Find the columns by number rather than name as some older versions of numpy mangle the special characters
    datetimes = rawd[rawd.dtype.names[0]] + rawd[rawd.dtype.names[1]]

    metadata = get_file_metadata(fname)
    lon = np.zeros(lend) + float(metadata.misc[2][1].split("=")[1])
    lat = np.zeros(lend) + float(metadata.misc[2][2].split("=")[1])
    alt = np.zeros(lend) + float(metadata.misc[2][3].split("=")[1])

    data_dict = {}
    if variables is not None:
        for key in variables:
            try:
                data_dict[key] = rawd[key]
            except ValueError:
                raise InvalidVariableError(key + " does not exist in " + fname)

    data_dict["datetime"] = ma.array(datetimes)
    data_dict["longitude"] = ma.array(lon)
    data_dict["latitude"] = ma.array(lat)
    data_dict["altitude"] = ma.array(alt)

    return data_dict


def get_file_metadata(filename, variable='', shape=None):
    file = open(filename)
    from cis.data_io.ungridded_data import Metadata

    if variable is None:
        variable = ''
    metadata = Metadata(name=variable, long_name=variable, shape=shape)
    lines = []
    for i in range(0, 4):
        lines.append(file.readline().replace("\n", "").split(","))
    metadata.misc = lines
    return metadata
