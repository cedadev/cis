from data_io.Coord import Coord, CoordList
from data_io.hdf import read_hdf4
from data_io.products.AProducts import AProduct
from data_io.ungridded_data import UngriddedData
import utils
import data_io.hdf_vd as hdf_vd
import data_io.hdf_sd as hdf_sd

import logging

class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD*']

    def create_coords(self, filenames, variable = None):
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # list of variables we are interested in
        variables = [ 'Latitude','Longitude','TAI_start','Profile_time','Height']

        if variable is not None:
            variables.append(variable)

        # reading of all variables
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

        # retrieve coordinates
        logging.debug("retrieving coordinate(s)")
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

        coords = CoordList([lat_coord,lon_coord,alt_coord,time_coord])

        if variable is None:
            return coords
        else:
            # retrieve data + its metadata
            logging.debug("retrieving data and associated metadata for variable: " + variable)
            data = sdata[variable]
            metadata = hdf_sd.get_metadata(sdata[variable][0])
            return UngriddedData(data,metadata,coords)

    def create_ungridded_data(self, filenames, variable):
        """
            This just refers the work to create coords which has to open all the files anyway to get the coordinates
        @param filenames:
        @param variable:
        @return:
        """
        return self.create_coords(filenames, variable)


class Cloud_CCI(AProduct):
    def get_file_signature(self):
        return [r'.*.nc']

    def create_coords(self, filenames, variable = None):
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = ["lat", "lon", "time"]

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables, dim="pixel_number") #i.e. datafile.variables[usr_variable]

        coords = CoordList()
        coords.append(Coord(data_variables["lon"], get_metadata(data_variables["lon"]), "X"))
        coords.append(Coord(data_variables["lat"], get_metadata(data_variables["lat"]), "Y"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        if variable is None:
            return coords
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_ungridded_data(self, filenames, variable):
        return self.create_coords(filenames, variable)