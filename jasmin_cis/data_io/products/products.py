from data_io.Coord import Coord, CoordList
from data_io.hdf import read_hdf4
from data_io.products.AProduct import AProduct
from data_io.ungridded_data import UngriddedData
import utils
import data_io.hdf_vd as hdf_vd
import data_io.hdf_sd as hdf_sd

import logging

class Cloudsat_2B_CWC_RVOD(AProduct):

    def __read_files(self, filenames, variables):

        sdata = {}
        vdata = {}
        for filename in filenames:

            logging.info("reading file: " + filename)

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

        return sdata,vdata


    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD*']

    def create_coords(self, filenames):

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # list of coordinate variables we are interested in
        variables = [ 'Latitude','Longitude','TAI_start','Profile_time','Height']

        # reading the various files
        sdata, vdata = self.__read_files(filenames,variables)

        logging.debug("retrieving coordinate(s) data+metadata")
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

        return CoordList([lat_coord,lon_coord,alt_coord,time_coord])


    def create_ungridded_data(self, filenames, variable):

        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = self.__read_files(filenames, variable)

        # retrieve data + its metadata
        logging.debug("retrieving data and associated metadata for variable: " + variable)
        data = sdata[variable]
        metadata = hdf_sd.get_metadata(sdata[variable][0])

        return UngriddedData(data,metadata,coords)


class Cloud_CCI(AProduct):

    def get_file_signature(self):
        return [r'.*ESACCI*.nc']

    def create_coords(self, filenames):

        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = ["lat", "lon", "time"]

        data = read_many_files(filenames, variables, dim="pixel_number")

        coords = CoordList()
        coords.append(Coord(data["lon"], get_metadata(data["lon"]), "X"))
        coords.append(Coord(data["lat"], get_metadata(data["lat"]), "Y"))
        coords.append(Coord(data["time"], get_metadata(data["time"]), "T"))

        return coords

    def create_ungridded_data(self, filenames, variable):

        from data_io.netcdf import read_many_files, get_metadata

        coords = self.create_coords(filenames)
        data = read_many_files(filenames, variable, dim="pixel_number")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)
