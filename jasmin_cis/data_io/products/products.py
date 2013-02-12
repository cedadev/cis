from data_io import Coord
from data_io.hdf import read_hdf4
from data_io.products.AProducts import AProduct
from data_io.ungridded_data import UngriddedData


class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD*'];

    def create_ungridded_data(self, filenames, variable):

        import utils
        import data_io.hdf_vd as hdf_vd
        import data_io.hdf_sd as hdf_sd

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # list of variables we are interested in
        variables = [ variable, 'Latitude','Longitude','TAI_start','Profile_time','Height']

        # reading of all variables
        sdata = {}
        vdata = {}
        for filename in filenames:

            print filename

            try:

                # reading in all variables into a 2 dictionaries:
                # sdata, key: variable name, value: list of sds
                # vdata, key: variable name, value: list of vds
                sds_dict, vds_dict = read_hdf4(filename,variables)
                for var in sds_dict.keys():
                    utils.add_element_to_list_in_dict(sdata,var,sds_dict[var])
                for var in vds_dict.keys():
                    utils.add_element_to_list_in_dict(vdata,var,vds_dict[var])

            except:
                print 'Error while reading file ', filename

        # retrieve data + its metadata
        data = sdata[variable]
        metadata = hdf_sd.get_metadata(sdata[variable][0])

        # retrieve coordinates
        alt_data = utils.concatenate([hdf_sd.get_data(i) for i in sdata['Height'] ])
        alt_metadata = hdf_sd.get_metadata(sdata['Height'][0])
        alt_coord = Coord(alt_data, alt_metadata,'Y')

        lat_data = utils.concatenate([hdf_vd.get_data(i) for i in vdata['Latitude'] ])
        lat_data = utils.expand_1d_to_2d_array(lat_data,len(alt_data[1]),axis=1)
        lat_metadata = hdf_vd.get_metadata(vdata['Latitude'][0])
        lat_coord = Coord(lat_data, lat_metadata)

        lon_data = utils.concatenate([hdf_vd.get_data(i) for i in vdata['Longitude'] ])
        lon_data = utils.expand_1d_to_2d_array(lon_data,len(alt_data[1]),axis=1)
        lon_metadata = hdf_vd.get_metadata(vdata['Longitude'][0])
        lon_coord = Coord(lon_data, lon_metadata)

        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time_data = utils.concatenate(arrays)
        time_data = utils.expand_1d_to_2d_array(time_data,len(alt_data[1]),axis=1)
        time_metadata = hdf_vd.get_metadata(vdata['Profile_time'][0])
        time_coord = Coord(time_data, time_metadata,'X')

        coords= [lat_coord,lon_coord,alt_coord,time_coord]

        return UngriddedData(data,metadata,coords)


class NetCDF_CF(AProduct):

    def get_file_signature(self):
        return [r'.*.nc'];

    def create_ungridded_data(self, filenames, variable):

        from data_io.netcdf import read_many_files

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # get variable
        var = read_many_files(filenames, [variable, "Latitude", "Longitude", "Time"])

        # get coordinates
        #coords = [ read_many_files(filenames, dim) for dim in var.dimensions ]

        return UngriddedData(var, metadata=var["Longitude"], coords=var["Latitude"])

    '''
    def get_coords_from_variable(self):
        coord_standard_names = [coord for coord in data.coordinates.split()]
        coords = []
        for standard_name in coord_standard_names:
            for variable in datafile.variables:
                try:
                    if datafile.variables[variable].standard_name == standard_name:
                        coords.append(datafile.variables[variable])
                        break
                except AttributeError:
                    pass
    '''


class Cloud_CCI(AProduct):
    def get_file_signature(self):
        return [r'.*.nc'];

    def create_ungridded_data(self, filenames, variable):
        from data_io.netcdf import read_many_files, get_metadata
        from data_io import Coord

        variables = read_many_files(filenames, [variable, "lat", "lon", "time"], dim="pixel_number") #i.e. datafile.variables[usr_variable]
        coords = []
        coords.append(Coord(variables["lon"], get_metadata(variables["lon"]), "X"))
        coords.append(Coord(variables["lat"], get_metadata(variables["lat"]), "Y"))
        coords.append(Coord(variables["time"], get_metadata(variables["time"]), "T"))
        return UngriddedData(variables[variable], get_metadata(variables[variable]), coords)