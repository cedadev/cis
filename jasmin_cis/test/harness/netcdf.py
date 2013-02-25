from jasmin_cis.data_io.netcdf import *

if __name__ == '__main__':
# get a list of files to read
    #folder = "/home/david/Data"
    #filenames = glob(folder + "/*" + "CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
    # WALDMfilenames = "/home/duncan/xenida.pah94?0.nc"
    # WALDM filename = '/home/duncan/xenida.pah9430.nc'
    filenames = "/home/daniel/CCI_Files/*"
    filename = "/home/daniel/CCI_Files/20080915012939-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_34210-fv02.02.nc"
    # WALDM var, coords = read_many_files(filenames, 'tendency_of_mass_fraction_of_cloud_liquid_water_in_air', 'time_1')
    aod550, aodcoords = read_many_files(filenames, 'AOD550', "pixel_number")
#    lat, latcoords = read_many_files(filenames, 'lat', "pixel_number")
 #   lon, loncoords = read_many_files(filenames, 'lon', "pixel_number")

    # read the data
    #data = readin_cloudsat_cwc_rvod(filenames,['RVOD_liq_water_content','Height','RVOD_ice_water_content'])

    # print results
#    print "\nkeys are: " , data.keys()
#
#    for key, value in data.iteritems():
#        try:
#            print "\n" + key + " :", get_metadata(value)['attributes'], ", dims: ", get_metadata(value)['dimensions']
#        except KeyError:
#            pass

    #var = data['tendency_of_mass_fraction_of_cloud_liquid_water_in_air']

    #coords = [ read_many_files(filenames, dim) for dim in var.dimensions ]

    print "aod550"
    print aod550
  #  print "lat"
   # print lat
    #print "lon"
    #print lon

    print "aodcoords"
    for coord in aodcoords:
        print coord
    #print "latcoords"
    #for coord in latcoords:
     #   print coord
    #print "loncoords"
    #for coord in loncoords:
     #   print coord

    print "aoddata"
    aoddata = get_data(aod550)
    print aoddata
    #print "latdata"
    #latdata = get_data(lat)
    #print latdata
    #print "londata"
    #londata = get_data(lon)
    #print londata
    #for item in data:
    #    if item != "--":
    #        print item
