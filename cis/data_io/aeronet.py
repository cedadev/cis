import logging

defaultdeletechars = """~!@#$%^&*=+~\|]}[{'; /?.>,<"""


def get_aeronet_file_variables(filename):
    import linecache

    vars = linecache.getline(filename, 5).split(",")
    for i in range(0, len(vars)):
        for char in defaultdeletechars:
            vars[i] = vars[i].replace(char, "")
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

    std_day = cis_standard_time_unit.num2date(0)

    def date2daynum(datestr):
        try:
            the_day = datetime.strptime(datestr, '%d:%m:%Y')
        except ValueError:
            the_day = datetime.strptime(datestr, '%d/%m/%Y')
        return float((the_day - std_day).days)

    def time2fractionalday(timestr):
        h, m, s = [int(t) for t in timestr.split(':')]
        td = timedelta(hours=h, minutes=m, seconds=s)
        return td.total_seconds()/(24.0*60.0*60.0)

    def convert_datatypes_to_floats(column):
        """
        Numpy.genfromtext() converts missing values 'N/A' to floats when using dtype=None.
        Also converts dates to objects.
        Convert them into float64 as they should be.
        :param column: Column to convert if a boolean.
        :return:
        """
        if column.dtype == np.bool:
            return column.astype(np.float64)
        if column.dtype == np.object:
            return np.array([column], dtype=np.float64)
        return column

    try:
        rawd = np.genfromtxt(fname, skip_header=4, delimiter=',', names=True, deletechars=defaultdeletechars,
                             converters={0: date2daynum, 1: time2fractionalday, 'Last_Processing_Date': date2daynum},
                             dtype=None, missing_values='N/A', usemask=True)
    except (StopIteration, IndexError) as e:
        raise IOError(e)

    lend = len(rawd)
    # The date and time column are already in days since cis standard time, and fractional days respectively, so we can 
    # just add them together
    datetimes = rawd['Date(dd-mm-yy)'] + rawd['Time(hh:mm:ss)']

    metadata = get_file_metadata(fname)
    lon = np.zeros(lend) + float(metadata.misc[2][1].split("=")[1])
    lat = np.zeros(lend) + float(metadata.misc[2][2].split("=")[1])
    alt = np.zeros(lend) + float(metadata.misc[2][3].split("=")[1])

    data_dict = {}
    if variables is not None:
        for key in variables:
            data_dict[key] = convert_datatypes_to_floats(rawd[key])

    data_dict["datetime"] = ma.array(datetimes, dtype=np.float64)
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
