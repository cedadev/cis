"""
    Data reading routines for satelite data. To be refactored.

"""

from pyhdf.error import HDF4Error
import hdf
import numpy as np
from glob import glob
import math
from gridding import *
from progressbar import *

# Radius of the earth in km
R_E = 6378.1

########################################################################
# Functions for reading in Satellite data, related to cloudsat
########################################################################
#
#  ERI Gryspeerdt, Climate processes group, Oxford University
#
#  2011-02-15 Initial submission to ClimProc-sat SVN
#  2011-02-17 Added different satellite support to readin_MODIS_L3
#  2011-05-27 Modification of the reflectivity readin to include gaseous absorbtion
########################################################################

def dictkeysappend(dict1,dict2): 
    ''' Appends data in dict2 to already existing keys in a dictionary dict1. If that key does not exist, it is created'''
    for key in dict2.keys():
        try:
            dict1[key] = np.hstack((dict1[key],dict2[key]))
        except KeyError:
            dict1[key] = dict2[key]
    return dict1


#Cloudsat Data

def readin_cloudsat_precip(day,year,sds,orbits=None,outdata=None): 
    '''Reads in data from CloudSat 2C-PRECIP-COLUMN files. Also reads in some geolocation data (lat,lon,TAI time) into the output dictionary. Setting outdata allows the data to be read into an already exisiting dictionary'''   
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/2C-PRECIP-COLUMN/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = sds+['Latitude','Longitude','TAI_start','Profile_time']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names,vdata=True)
            data['Profile_time'] = data['Profile_time'] + data['TAI_start']
            for name in data.keys():
                try:
                    outdata[name] = np.hstack((outdata[name],data[name]))
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata[name] = data[name]
        except HDF4Error:
            print HDF4Error, ' in readin_cloudsat_precip', file
    return outdata

def readin_cloudsat_cwc_rvod(day,year,sds,orbits=None,outdata=None): 
    '''Reads in data from CloudSat 2B-CWC-RVOD files. Also reads in some geolocation data (lat,lon,TAI time) into the output dictionary. Setting outdata allows the data to be read into an already exisiting dictionary'''   
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/2B-CWC-RVOD/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = sds+['Latitude','Longitude','TAI_start','Profile_time']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names,vdata=True)
            data['Profile_time'] = data['Profile_time'] + data['TAI_start']
            for name in data.keys():
                try:
                    outdata[name] = np.concatenate((outdata[name],data[name]),axis=0)
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_cwc_rvod'
                    outdata[name] = data[name]
        except HDF4Error:
            print HDF4Error, ' in readin_cloudsat_cwc_rvod', file
    return outdata

def readin_cloudsat_geoprof(day,year,sds,orbits=None,outdata=None,cloudmask=False): #2B-GEOPROF
    '''Reads in Cloudsat 2B-GEOPROF data including geolocation data.  Will create a cloudtop height product if cloudmask is set to True. Setting outdata allows the data to be read into an already exisiting dictionary'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/2B-GEOPROF/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = sds+['Latitude','Longitude','TAI_start','Profile_time']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names,vdata=True)
            data['gProfile_time'] = data['Profile_time'] + data['TAI_start']
            data['gLatitude'] = data['Latitude']
            data['gLongitude'] = data['Longitude']
            del(data['Latitude'])
            del(data['Longitude'])
            del(data['TAI_start'])
            del(data['Profile_time'])
            if cloudmask:
                datam = hdf.read_hdf4(file,['Height','CPR_Cloud_mask'])
                data['Cloud_top'] = np.zeros(datam['CPR_Cloud_mask'].shape[0])
                for col in range(datam['CPR_Cloud_mask'].shape[0]):
                    try: data['Cloud_top'][col] = datam['Height'][col,np.where(datam['CPR_Cloud_mask'][col,:] >= 30)[0][0]]
                    except: data['Cloud_top'][col] = np.nan
            for name in data.keys():
                try:
                    outdata[name] = np.hstack((outdata[name],data[name]))
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata[name] = data[name]
        except HDF4Error:
            print HDF4Error, ' in readin_cloudsat_precip', file
    return outdata

def readin_cloudsat_reflectivity(day,year,orbits=None,outdata=None): #2B-GEOPROF
    '''Reads in Cloudsat 2B-GEOPROF radar reflectivity data. Setting outdata allows the data to be read into an already exisiting dictionary'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/2B-GEOPROF/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['Latitude','Longitude','TAI_start','Profile_time']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names,vdata=True)
            data['gProfile_time'] = data['Profile_time'] + data['TAI_start']
            data['gLatitude'] = data['Latitude']
            data['gLongitude'] = data['Longitude']
            del(data['Latitude'])
            del(data['Longitude'])
            del(data['TAI_start'])
            del(data['Profile_time'])
            newdata = hdf.read_hdf4(file,['Radar_Reflectivity','CPR_Cloud_mask','Height','Gaseous_Attenuation'])
            data = dictkeysappend(data,newdata)
            for name in data.keys():
                try:
                    outdata[name] = np.concatenate((outdata[name],data[name]),axis=0)
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata[name] = data[name]
        except HDF4Error:
            print HDF4Error, ' in readin_cloudsat_precip', file
    return outdata


#For data from MODIS-AUX
def MODIS_day_flag(day,year,orbits=None,outdata=None):
    '''Creates a day flag for Cloudsat using MODIS-AUX radiances.'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/MODIS-AUX/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['EV_250_RefSB']
    outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names)
            data['Day'] = np.where(data['EV_250_RefSB'][0,:,7] > 60000,np.nan,1)
            try:
                outdata['Day'] = np.hstack((outdata['Day'],data['Day']))
            except KeyError:
                outdata['Day'] = data['Day']                    
        except HDF4Error:
            print HDF4Error, ' in MODIS_day_flag', file
    return outdata

def MODIS_ice_flag(day,year,orbits=None,outdata=None): #Checking the cloud mask for high level cloud
    '''Creates a high cloud flag for cloudsat using MODIS-AUX data. Use not recommended, use the MODIS_scene_char product from 2B-GEOPROF instead'''
    print 'Use of the function is not currently recommended, use MODIS_scene_char from 2B-GEOPROF instead (MODIS_ice_flag)'
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/MODIS-AUX/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['Cloud_Mask']
    outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names)
            data['IceA'] = np.where(((data['Cloud_Mask'][1,:,7].astype(int) & 202) == 202) ,1,0)
            data['IceB'] = np.where(((data['Cloud_Mask'][2,:,7].astype(int) & 3) != 0) ,1,0)
            data['Ice'] = data['IceA'] * data['IceB']
            try:
                outdata['Ice'] = np.hstack((outdata['Ice'],data['Ice']))
            except KeyError:
                outdata['Ice'] = data['Ice']
        except HDF4Error:
            print HDF4Error, ' in MODIS_ice_flag', file
    return outdata

def MODIS_cloudmask(day,year,orbits=None,outdata=None): #Checking the cloud mask for high level cloud
    '''Should read out the MOD35 cloudmask from MODIS-AUX, use not currently recommended'''
    print 'Use of this function is not currently recommended (MODIS_cloudmask)'
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/MODIS-AUX/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['Cloud_Mask']
    outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names)
            try:
                outdata['Cloud_Mask'] = np.hstack((outdata['Cloud_Mask'],data['Cloud_Mask']))
            except KeyError:
                outdata['Cloud_Mask'] = data['Cloud_Mask']
        except HDF4Error:
            print HDF4Error, ' in MODIS_cloudmask', file
    return outdata

def MODIS_AUX_10p8um(day,year,orbits=None,outdata=None,min=None):
    '''Reads in the 10.8um radiances from MODIS-AUX for cloudsat'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/MODIS-AUX/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['EV_1KM_Emissive','EV_1KM_Emissive_rad_offsets','EV_1KM_Emissive_rad_scales','MODIS_granule_index']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names)
            if min == True: 
                for x in range(1,int(data['MODIS_granule_index'].max())+1):
                    ref = np.where(data['MODIS_granule_index'][:,:] == x)
                    data['EV_1KM_Emissive'][6,:,:][ref] = (data['EV_1KM_Emissive'][6,:,:][ref]-data['EV_1KM_Emissive_rad_offsets'][6][x]) * data['EV_1KM_Emissive_rad_scales'][6][x]
                try:
                    outdata['Radiances'] = np.hstack((outdata['Radiances'],data['EV_1KM_Emissive'][6,:,7]))
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata['Radiances'] = data['EV_1KM_Emissive'][6,:,:].min(axis=1)
            else:
                for x in range(1,int(data['MODIS_granule_index'].max())+1):
                    ref = np.where(data['MODIS_granule_index'][:,7] == x)
                    data['EV_1KM_Emissive'][6,:,7][ref] = (data['EV_1KM_Emissive'][6,:,7][ref]-data['EV_1KM_Emissive_rad_offsets'][6][x]) * data['EV_1KM_Emissive_rad_scales'][6][x]
                try:
                    outdata['Radiances'] = np.hstack((outdata['Radiances'],data['EV_1KM_Emissive'][6,:,7]))
                except KeyError:
                    #print KeyError, ' in readin_cloudsat_precip'
                    outdata['Radiances'] = data['EV_1KM_Emissive'][6,:,7]
        except HDF4Error:
            print HDF4Error, ' in MODIS_AUX_10p8um', file
    return outdata



#Reading in data from MODIS L3
def readin_MODIS_L3(day,year,sds,outdata=None,sat='aqua',col='5'):
    '''Reads in MODIS L3 data from the collection 5 daily files on cloud'''
    day = str(day).rjust(3,'0')
    if outdata == None:
        outdata = {}
    names = sds + ['XDim','YDim']
    if col == '5':
        col = '005'
    elif col == '51':
        col = '051'
    if sat == 'aqua': datafilename = '/home/cloud/cp/Data/MODIS/MYD08_D3/'+col+'/'+str(year)+'/'
    elif sat == 'terra': datafilename = '/home/cloud/cp/Data/MODIS/MOD08_D3/'+col+'/'+str(year)+'/'
    else: 
        print 'Not a valid MODIS satellite'
        return
    datafilename = glob(datafilename + '*.A'+ str(year) +str(day)+'*')
    try:
        l3dict = hdf.read_hdf4(datafilename[0],names)
        for name in names:
            try:
                outdata[name] = np.hstack((outdata[name],l3dict[name]))
            except KeyError:
                #print KeyError, ' in readin_MODIS_L3', name
                outdata[name] = l3dict[name]
    except HDF4Error:
        print HDF4Error, datafilename
    return outdata

def readin_MODIS_csfp(day,year,sds,outdata = None):
    '''Reads in MODIS cloud data on the cloudsat footprint.'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/MODIS/'
    filename = glob(folder + str(year) + '/' + str(day) + '/*')
    filename = np.sort(filename)
    if outdata == None:
        outdata = {} 
    names = sds + ['Latitude','Longitude','Scan_Start_Time']
    for file in filename:
        #print file
        try:
            print file
            csfpdict = hdf.read_hdf4(file,names,vdata=None)
            for name in names:
                try:
                    mid = csfpdict[name].shape[1]/2
                    if name == 'Quality_Assurance_1km':
                        outdata[name] = np.hstack((outdata[name],csfpdict[name][:,mid,4]))
                    else:
                        outdata[name] = np.hstack((outdata[name],csfpdict[name][:,mid]))
                except KeyError:
                    if name == 'Quality_Assurance_1km':
                        outdata[name] = csfpdict[name][:,mid,4]
                    else:
                        outdata[name] = csfpdict[name][:,mid]
        except HDF4Error:
            print HDF4Error, 'in readin_MODIS_csfp', file
    return outdata

def compdist(latp,lonp,lat1,lon1,lat2,lon2):
    '''Compares the distance from p to 1 and 2. Returns True if 2 is closer'''
    #print (haversine(latp,lonp,lat1,lon1), haversine(latp,lonp,lat2,lon2))
    #if not np.isfinite(haversine(latp,lonp,lat1,lon1)):
    #    return True
    return (haversine(latp,lonp,lat1,lon1) > haversine(latp,lonp,lat2,lon2))

def haversine(lat1,lon1,lat2,lon2):
    '''Computes the Haversine distance between two points'''
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    arclen = 2*math.asin(math.sqrt((math.sin((lat2-lat1)/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2-lon1)/2))**2))
    return arclen*R_E

def geoloc_interpolate(geoloc):  
    '''Interpolates geolocation data, intended for use only with MODIS_L2_regrid'''
    geolocexpand = np.zeros(5*len(geoloc))
    dtln_flag = (abs(max(geoloc))+abs(min(geoloc)))/2
    for x in range(0,len(geoloc)-1):
        for y in range(0,5):
            geolocexpand[5*x + y] = geoloc[x] + (geoloc[x+1] - geoloc[x])/5 * y
            if (geoloc[x+1] - geoloc[x]) > dtln_flag:
                geolocexpand[5*x + y] = geoloc[x] + (geoloc[x+1] - geoloc[x] -360)/5 * y 
    x = x+1
    for y in range(0,5):
            geolocexpand[5*x + y] = geoloc[x] + (geoloc[x] - geoloc[x-1])/5 * y
    return geolocexpand #np.reshape(geolocexpand,(-1))


def MODIS_L2_regrid(MODISdata,cloudsatdata,sds): 
    '''Regrids MODIS data on the cloudsat track to the cloudsat grid. It will need to be run twice over consecutive days of MODIS data to make sure all cloudsat data has correctponding MODIS data. The MODIS data requires (Latitude,Longitude,Scan_Start_Time and the necessary SDS. The Cloudsat data requires (Latitude,Longitude,Profile time)'''
    outputdata = {}
    #Gets the geoloc data at the same resolution as the SDS
    if MODISdata[sds[0]].shape != MODISdata['Latitude'].shape:
        MODISdata['Latitude'] = geoloc_interpolate(MODISdata['Latitude']) 
        MODISdata['Longitude'] = geoloc_interpolate(MODISdata['Longitude'])
        MODISdata['Scan_Start_Time'] = geoloc_interpolate(MODISdata['Scan_Start_Time'])
    mask = np.where(np.isfinite(MODISdata['Latitude']))
    for key in MODISdata.keys():
        MODISdata[key] = MODISdata[key][mask]
    #Move MODIS infront of cloudsat by specifying the start time.  
    z = 0
    while MODISdata['Scan_Start_Time'][z] < cloudsatdata['Profile_time'][0]:
        z = z +1
    while MODISdata['Latitude'][z] < cloudsatdata['Latitude'][0]:
        z = z-1
    
    y=z
    for name in sds:
        outputdata[name] = np.zeros(len(cloudsatdata['Latitude']))
    outputdata['Dist'] = np.zeros(len(cloudsatdata['Latitude']))
    for x in range(len(cloudsatdata['Latitude'])):
        while compdist(cloudsatdata['Latitude'][x],cloudsatdata['Longitude'][x], \
                       MODISdata['Latitude'][y],MODISdata['Longitude'][y], \
                       MODISdata['Latitude'][y+1],MODISdata['Longitude'][y+1]):
            y = y+1
        outputdata['Dist'][x] = haversine(cloudsatdata['Latitude'][x], \
                                              cloudsatdata['Longitude'][x], \
                                              MODISdata['Latitude'][y], \
                                              MODISdata['Longitude'][y])
        if outputdata['Dist'][x] > 6:
            while MODISdata['Scan_Start_Time'][y] < cloudsatdata['Profile_time'][x]:
                y = y +1
            while MODISdata['Latitude'][y] < cloudsatdata['Latitude'][x]:
                y = y-1
            outputdata['Dist'][x] = haversine(cloudsatdata['Latitude'][x], \
                                                   cloudsatdata['Longitude'][x], \
                                                   MODISdata['Latitude'][y], \
                                                   MODISdata['Longitude'][y])
        for name in sds:
            outputdata[name][x] = MODISdata[name][y]
        
        #print x, y, cloudsat['Dist'][x]
        if y+1 == len(MODISdata['Latitude']): break
    return outputdata












    
#Functions for calculating the LTSS as the ECMWF-AUX file is read in

def readin_ECMWF(day,year,sds,orbits = None, outdata=None):
    '''Reads in ECMWF LTSS on the cloudsat footprint'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/ECMWF/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = sds
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            try:
                data = hdf.read_hdf4(file,names,vdata=False)
                dictkeysappend(outdata,data)
            except:
                surfdata = hdf.read_hdf4(file,names,vdata=True)
                dictkeysappend(outdata,surfdata)
        except HDF4Error:
            print HDF4Error, ' in readin_ECMWF', file
    return outdata

def readin_ECMWF_LTSS(day,year,orbits = None, outdata=None):
    '''Reads in ECMWF LTSS on the cloudsat footprint'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/ECMWF/'
    if orbits == None:
        filename = glob(folder + str(year) + '/' + str(day) + '/*')
        filename = np.sort(filename)
    else:
        filename = []
        for orbit in orbits:
            file = glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')
            filename.append(file[0])
    names = ['Pressure','Temperature']
    if outdata == None:
        outdata = {}
    for file in filename:
        try:
            print file
            data = hdf.read_hdf4(file,names,vdata=False)
            surfdata = hdf.read_hdf4(file,names=['Surface_pressure','Temperature_2m','EC_height','Latitude','Longitude'],vdata=True)
            LTSS_data = np.zeros(data['Temperature'].shape[0])
            height270 = np.zeros(data['Temperature'].shape[0])
            pheight500 = np.zeros(data['Temperature'].shape[0])
            for x in range(0,data['Temperature'].shape[0]):
                LTSS_data[x] = LTSS(data['Temperature'][x],data['Pressure'][x],surfdata['Surface_pressure'][x],surfdata['Temperature_2m'][x])
                height270[x] = theight(data['Temperature'][x],surfdata['EC_height'])
                pheight500[x] = pheight(data['Pressure'][x],surfdata['EC_height'])
            try:
                outdata['LTSS'] = np.hstack((outdata['LTSS'],LTSS_data))
                outdata['height270'] = np.hstack((outdata['height270'],height270))
                outdata['pheight500'] = np.hstack((outdata['pheight500'],pheight500))
                outdata['eLatitude'] = np.hstack((outdata['eLatitude'],surfdata['Latitude']))
                outdata['eLongitude'] = np.hstack((outdata['eLongitude'],surfdata['Longitude']))
            except KeyError:
                #print KeyError, ' in readin_ECMWF'
                outdata['eLatitude'] = surfdata['Latitude']
                outdata['eLongitude'] = surfdata['Longitude']
                outdata['pheight500'] = pheight500
                outdata['height270'] = height270
                outdata['LTSS'] = LTSS_data
        except HDF4Error:
            print HDF4Error, ' in readin_ECMWF', file
    return outdata


def theta(temperature,pressure):
    '''Calculated potential temperature'''
    theta = temperature * (100000/pressure) ** 0.288
    return theta

def LTSS(temperature, pressure, surfacepres, surfacetemp):
    '''Calculated Low Troposphere Static Stability'''
    try:
        p700plus = 85
        while True:
            if pressure[p700plus] > 70000: break
            p700plus = p700plus + 1   
            
        p700minus = p700plus - 1
        
        #while True:
        #    if not np.isfinite(pressure[surface + 1]): break
        #    surface = surface +1
            
        theta700plus = theta(temperature[p700plus],pressure[p700plus])
        theta700minus = theta(temperature[p700minus],pressure[p700minus])
        gradient = (theta700plus - theta700minus)/(pressure[p700plus]-pressure[p700minus])
        theta700 = gradient * (70000 - pressure[p700minus]) + theta700minus
        LTSSout = theta700 - theta(surfacetemp,surfacepres)
    except IndexError: LTSSout = np.nan
    return LTSSout

def theight(temperature,heights): 
    '''Find the height of the 270K level from cloudsat ECMWF data'''
    try:
        t270minus = 50
        while True:
            if temperature[t270minus] > 270: break
            t270minus = t270minus + 1
            
        t270plus = t270minus -1
        if not np.isfinite(temperature[t270plus]): return np.nan
        gradient = (heights[t270minus] - heights[t270plus])/(temperature[t270minus] - temperature[t270plus])
        height270 = gradient * (270 - temperature[t270minus]) + heights[t270minus]
    except IndexError: height270 = np.nan
    return height270

def pheight(pressure,heights): 
    '''Find the height of the 500hPa level from cloudsat ECMWF data'''
    try:
        t270minus = 50
        while True:
            if pressure[t270minus] > 50000: break
            t270minus = t270minus + 1
            
        t270plus = t270minus -1
        if not np.isfinite(pressure[t270plus]): return np.nan
        gradient = (heights[t270minus] - heights[t270plus])/(pressure[t270minus] - pressure[t270plus])
        height270 = gradient * (50000 - pressure[t270minus]) + heights[t270minus]
    except IndexError: height270 = np.nan
    return height270


#PERSIANN data
def readin_PERSIANN(day,year):
    '''Reads in PERSIANN data from the PERSIANN text files'''
    day = str(day).rjust(3,'0')
    folder = '/home/cloud/cp/Users/gryspeerdt/cloudsat/PERSIANN/'
    filename = glob(folder + str(year) + str(day) + '.asc')
    data = []
    for file in filename:
        try:
            print file
            f = open(file,'r')
            for line in f:
                try:
                    z = map(float,line.split())
                    zmask = np.where(z < 0, np.nan, 1)
                    data.append(z * zmask)
                except:
                    pass  
        except:
            print 'Error reading PERSIANN file ' + day
    return np.flipud(np.array(data))
