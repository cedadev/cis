
import numpy as np
from pyhdf.error import HDF4Error
import hdf

def dictkeysappend(dict1,dict2,axis=0):
    ''' Appends data in dict2 to already existing keys in a dictionary dict1. If that key does not exist, it is created'''
    for key in dict2.keys():
        try:
            dict1[key] = np.concatenate((dict1[key],dict2[key]),axis=axis)
        except KeyError:
            dict1[key] = dict2[key]
    return dict1


def readin_MODIS_L2(filenames,sds,outdata = None):
    '''Reads in single day of MODIS L2 data'''

    if outdata == None:
        outdata = {}

    names = sds + ['Latitude','Longitude']

    for file in filenames:
        #print file
        try:
            print "reading: " + file
            data_dict = hdf.read_hdf4(file,names,vdata=None)
            dictkeysappend(outdata,data_dict)
        except HDF4Error as e:
            print e.message, 'in readin_MODIS_L2', file
    return outdata


def field_interpolate(data,factor=5):
    '''Interpolates the given 2D field by the factor, edge pixels are defined by the ones in the centre, odd factords only!'''
    output = np.zeros((factor*data.shape[0],factor*data.shape[1]))*np.nan
    output[int(factor/2)::factor,int(factor/2)::factor] = data
    for i in range(1,factor+1):
        output[(int(factor/2)+i):(-1*factor/2+1):factor,:] = i*((output[int(factor/2)+factor::factor,:]-output[int(factor/2):(-1*factor):factor,:])
                                                                /float(factor))+output[int(factor/2):(-1*factor):factor,:]
    for i in range(1,factor+1):
        output[:,(int(factor/2)+i):(-1*factor/2+1):factor] = i*((output[:,int(factor/2)+factor::factor]-output[:,int(factor/2):(-1*factor):factor])
                                                                /float(factor))+output[:,int(factor/2):(-1*factor):factor]

    return output


if __name__ ==  '__main__':

    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    from glob import glob

    # get a list of files to read
    folder = "/home/david/Data"
    filenames = glob(folder + "/*" + "MYD06_L2" + "*.hdf")
    filenames = np.sort(filenames)

    #Scan_Start_Time is the time of the MODIS observations - it is not read in by default as
    # the joint L2 product (MYDATML2) omits it.  However, the scan time can be approximated
    # by the time in the filename
    #The is currently only collection 5.1 (col='51') on cloud for MYD06 for a limited area
    # around the Barbados Cloud Observatory
    L2_data = readin_MODIS_L2(filenames,['Cloud_Water_Path','Cloud_Top_Pressure_Day','Scan_Start_Time'])

    #The latitude and longitude are on a 5km grid, whereas the data is on a 1km grid.  MODIS
    # data comes at several different scales - the cloud optical properties retrieval is done
    # at 1km, some retrievals are at 5km and the aerosol retrieval is at 10km.  If relevant,
    # 5km and 10km lat/lon are usually included - to get 1km lat/lon you have to interpolate.
    # This is a very simple interpolation linear scheme which could do with some improvement.
    latitude_1km = field_interpolate(L2_data['Latitude'])
    longitude_1km = field_interpolate(L2_data['Longitude'])
    #latitude_1km = L2_data['Latitude']
    #longitude_1km = L2_data['Longitude']


    #The last four bins in the across scan direction are truncated (According to P. Hubanks
    # at NASA), I can't find this mentionned anywhere in the documentation though, and it is probably
    # not true for all datasets
    plt_lwp = L2_data['Cloud_Water_Path'][:,:-4]
    plt_lwp = np.ma.array(plt_lwp,mask=np.isnan(plt_lwp))

    m = Basemap(-75,0,-45,35,resolution='i')
    plt.subplot(221)
    m.pcolormesh(longitude_1km,latitude_1km,plt_lwp,vmax=600)
    m.drawcoastlines()
    plt.xticks([-75,-65,-55,-45],[-75,-65,-55,-45])
    plt.yticks([0,5,10,15,20,25,30,35],[0,5,10,15,20,25,30,35])
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('MYD06 - Cloud Water Path (1km)')
    cb = plt.colorbar(shrink=0.8)
    cb.set_label('gm $^{-2}$')


    plt.show()
