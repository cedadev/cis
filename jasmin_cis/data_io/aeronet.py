

def get_aeronet_file_variables(filename):
    import linecache
    defaultdeletechars = """~!@#$%^&*()-=+~\|]}[{';: /?.>,<"""
    vars = linecache.getline(filename, 5).split(",")
    for i in range(0, len(vars)):
        for char in defaultdeletechars:
            vars[i] = vars[i].replace(char, "")
    vars_dict = {}
    for var in vars:
        vars_dict[var] = var
    return vars_dict


def load_multiple_aeronet(fnames, variables=None):
    from jasmin_cis.utils import concatenate
    #data = concatenate([load_aeronet(a_file, variables) for a_file in fnames])
    list_of_obj = [load_aeronet(a_file, variables) for a_file in fnames]
    for obj in list_of_obj:

    return data


def load_aeronet(fname, variables=None):
    """
    loads aeronet lev 2.0 csv file.

        Originally from http://code.google.com/p/metamet/
        License: GNU GPL v3

    @param fname: data file name
    @param keep_fields: A list of variables to return
    @return: A
    """
    import numpy as np
    from matplotlib import mlab
    from numpy import ma
    from datetime import datetime, timedelta

    std_day = datetime(1900,1,1,0,0,0)
    def date2daynum(datestr):
        the_day = datetime.strptime(datestr, '%d:%m:%Y')
        return float((the_day - std_day).days)

    def time2seconds(timestr):
        h, m, s = [int(t) for t in timestr.split(':')]
        return float(h * 3600 + m * 60 + s)

    def daynum_seconds2datetime(daynum, seconds):
        return std_day + timedelta(days=int(daynum), seconds=int(seconds))

    try:
        rawd = np.genfromtxt(fname, skip_header=4, delimiter=',', names=True, converters={0:date2daynum, 1:time2seconds}, missing_values='N/A', usemask = True)
    except StopIteration as e:
        raise IOError(e)

    lend = len(rawd)
    dates = np.zeros(len(rawd), dtype='O')
    for i in xrange(lend):
        dates[i] = daynum_seconds2datetime(rawd['Dateddmmyy'][i], rawd['Timehhmmss'][i])

    metadata = get_file_metadata(fname)
    lon = np.zeros(len(rawd)) + float(metadata.misc[2][1].split("=")[1])
    lat = np.zeros(len(rawd)) + float(metadata.misc[2][2].split("=")[1])
    alt = np.zeros(len(rawd)) + float(metadata.misc[2][3].split("=")[1])

    data_dict = {}
    for key in variables:
        data_dict = rawd[key]

    data_dict["datetime"] = ma.array(dates)
    data_dict["longitude"] = ma.array(lon)
    data_dict["latitude"] = ma.array(lat)
    data_dict["altitude"] = ma.array(alt)

    '''
    newd = mlab.rec_append_fields(rawd, ['datetime', 'longitude', 'latitude', 'altitude'], [dates, lon, lat, alt])
    newd = mlab.rec_drop_fields(newd, ['Dateddmmyy', 'Timehhmmss', 'Last_Processing_Date'])

    if variables is not None:
        keep_fields = ['datetime', 'longitude', 'latitude', 'altitude'] + variables
        newd = mlab.rec_keep_fields(newd, keep_fields)
    from numpy.ma.mrecords import MaskedRecords
    '''
    return data_dict


def get_file_metadata(filename, variable = '', shape = None):
    file = open(filename)
    from jasmin_cis.data_io.ungridded_data import Metadata
    if variable is None: variable = ''
    metadata = Metadata(name = variable, long_name = variable, shape = shape)
    lines = []
    for i in range(0, 4):
        lines.append(file.readline().replace("\n","").split(","))
    metadata.misc = lines
    return metadata