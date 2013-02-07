from data_io.netcdf import *

if __name__ == '__main__':
# get a list of files to read
    #folder = "/home/david/Data"
    #filenames = glob(folder + "/*" + "CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")

    data = read('/home/duncan/xenida.pah9430.nc')

    # read the data
    #data = readin_cloudsat_cwc_rvod(filenames,['RVOD_liq_water_content','Height','RVOD_ice_water_content'])

    # print results
    print "\nkeys are: " , data.keys()

    for key, value in data.iteritems():
        try:
            print "\n" + key + " :", get_metadata(value)['attributes']
        except KeyError:
            pass

    print data['tendency_of_mass_fraction_of_cloud_liquid_water_in_air']

    print get_data(data['tendency_of_mass_fraction_of_cloud_liquid_water_in_air'])._get_mask