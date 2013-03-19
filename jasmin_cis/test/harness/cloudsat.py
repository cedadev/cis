from glob import glob
from pyhdf.error import HDF4Error
import numpy as np
import hdf

def dictkeysappend(dict1,dict2,axis=-1):
    '''
    Appends data in dict2 to already existing keys in a dictionary dict1.
    If that key does not exist, it is created
    '''
    for key in dict2.keys():
        try:
            dict1[key] = np.concatenate((dict1[key],dict2[key]),axis=axis)
        except KeyError:
            dict1[key] = dict2[key]
    return dict1

def readin_cloudsat_cwc_rvod(filenames,sds,outdata=None):
    '''
    Reads in data from CloudSat 2B-CWC-RVOD files.
    Also reads in some geolocation data (lat,lon,TAI time) into the output dictionary.
    Setting outdata allows the data to be read into an already exisiting dictionary
    '''
    names = sds+['Latitude','Longitude','TAI_start','Profile_time']
    if outdata == None:
        outdata = {}
    for file in filenames:
        try:
            print '...Reading file ' + file
            data = hdf.read_hdf4(file,names,vdata=True)
            data['Profile_time'] = data['Profile_time'] + data['TAI_start']
            outdata = dictkeysappend(outdata,data,axis=0)
        except HDF4Error:
            print HDF4Error, ' in readin_cloudsat_cwc_rvod', file
    return outdata


def plot(data):

    import matplotlib.pyplot as plt

    plt.imshow(data['RVOD_liq_water_content'][3000:3600,:103].transpose(),vmin=0)
    plt.yticks([0,25,50,75,100],[25,18.75,12.5,6.25,0])
    plt.ylabel('~Height above MSL (km)')
    plt.title('CloudSat RVOD Liquid Water Content')
    cm = plt.colorbar()
    cm.set_label('mg m$^{-3}$')
    plt.show()

if __name__ == '__main__':

    import numpy as np

    # get a list of files to read
    folder = "/home/david/Data"
    #filenames = glob(folder + "/*" + "CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
    filenames = [folder + "/2007180012247_06214_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf"]
    filenames = np.sort(filenames)

    # read the data
    data = readin_cloudsat_cwc_rvod(filenames,['RVOD_liq_water_content','Height','RVOD_ice_water_content'])

    # print data
    print "\nkeys are: " , data.keys()

    for key, value in data.iteritems():
        print "\n" + key + " :", value, len(value), np.nanmin(value), np.nanmax(value)

    # plot data
    plot(data)
