'''
From http://code.google.com/p/metamet/
License: GNU GPL v3
'''

from datetime import datetime, timedelta
import numpy as np
from matplotlib import mlab

__all__ = ['load_aeronet']

def load_aeronet(fname, keep_fields='all'):
    """loads aeronet lev 2.0 csv file.
    fname: data file name
    keep_fields: 'all' or a list of fields
    """

    std_day = datetime(1900,1,1,0,0,0)
    def date2daynum(datestr):
        the_day = datetime.strptime(datestr, '%d:%m:%Y')
        return float((the_day - std_day).days)

    def time2seconds(timestr):
        h, m, s = [int(t) for t in timestr.split(':')]
        return float(h * 3600 + m * 60 + s)

    def daynum_seconds2datetime(daynum, seconds):
        return std_day + timedelta(days=int(daynum), seconds=int(seconds))

    rawd = np.genfromtxt(fname, skip_header=4, delimiter=',', names=True, converters={0:date2daynum, 1:time2seconds})
    lend = len(rawd)
    dates = np.zeros(len(rawd), dtype='O')
    for i in range(lend):
        dates[i] = daynum_seconds2datetime(rawd['Dateddmmyy'][i], rawd['Timehhmmss'][i])

    newd = mlab.rec_append_fields(rawd, 'datetime', dates)
    newd = mlab.rec_drop_fields(newd, ['Dateddmmyy', 'Timehhmmss', 'Last_Processing_Date'])

    if keep_fields is not 'all':
        keep_fields = ['datetime'] + keep_fields
#        print keep_fields
        newd = mlab.rec_keep_fields(newd, keep_fields)
    return newd

def get_file_metadata(filename):
    file = open(filename)
    from data_io.ungridded_data import Metadata
    metadata = Metadata()
    lines = []
    for i in range(0, 4):
        lines.append(file.readline().replace("\n","").split(","))
    metadata.misc = lines
    return metadata