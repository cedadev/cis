"""
Reading in data from MODIS L3
"""
import numpy as np
from pyhdf.error import HDF4Error
from pyhdf.SD import *
from jasmin_cis.test.harness import hdf
import re

def readin_MODIS_L3(filenames,sds,outdata=None):
    '''Reads in MODIS L3 data from the collection 5 daily files on cloud'''
    if outdata == None:
        outdata = {}

    names = sds + ['XDim','YDim']

    try:
        l3dict = hdf.read_hdf4(filenames[0],names)
        for name in names:
            try:
                outdata[name] = np.hstack((outdata[name],l3dict[name]))
            except KeyError:
                #print KeyError, ' in readin_MODIS_L3', name
                outdata[name] = l3dict[name]
    except HDF4Error:
        print HDF4Error, filenames
    return outdata


if __name__ ==  '__main__':

    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    from glob import glob

    # get a list of files to read
    folder = "/home/david/Data"
    filenames = glob(folder + "/*" + "MYD08_D3" + "*.hdf")
    filenames = np.sort(filenames)

    #Get some level 3 data (daily mean)
    L3_data = readin_MODIS_L3(filenames,['Cloud_Water_Path_Combined_Mean'])
    #The L3 data does have some lat/lon data in the file, but as it is regularly gridded, I
    # usually just plot it using imshow.
    plt_l3 = L3_data['Cloud_Water_Path_Combined_Mean'].squeeze()[::-1]

    # do plotting
    m = Basemap(-180,-90,180,90)
    m.imshow(plt_l3,vmax=600,interpolation='nearest')
    m.drawcoastlines()
    plt.title('MYD08_D3 - Cloud Water Path Combined')
    plt.xticks([-180,-90,0,90,180],[-180,-90,0,90,180])
    plt.yticks([-60,-30,0,30,60],[-60,-30,0,30,60,90])
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    cb = plt.colorbar(shrink=0.8)
    cb.set_label('gm $^{-2}$')

    plt.show()




