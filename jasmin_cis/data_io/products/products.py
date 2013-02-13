from data_io.Coord import Coord, CoordList
from data_io.hdf import read_hdf4
from data_io.products.AProduct import AProduct
from data_io.ungridded_data import UngriddedData
import jasmin_cis.utils as utils
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

    def create_data_object(self, filenames, variable):

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
        return [r'.*ESACCI*\.nc']

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

    def create_data_object(self, filenames, variable):

        from data_io.netcdf import read_many_files, get_metadata

        coords = self.create_coords(filenames)
        data = read_many_files(filenames, variable, dim="pixel_number")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)

class NetCDF_CF(AProduct):
    def get_file_signature(self):
        return [r'.*\.nc']

    def create_coords(self, filenames, variable = None):
        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))
        coords.append(Coord(data_variables["altitude"], get_metadata(data_variables["altitude"]), "Z"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        if variable is None:
            return coords
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)


class NetCDF_CF_Gridded(NetCDF_CF):
    def get_file_signature(self):
        return [r'.*xenida.*\.nc']

    def create_coords(self, filenames):
        # TODO Expand coordinates
        # For gridded data sets this will actually return coordinates which are too short
        #  we need to think about how to expand them here
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from data_io.netcdf import read, get_metadata
        from data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]

        data_variables = read(filenames[0], variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))
        coords.append(Coord(data_variables["altitude"], get_metadata(data_variables["altitude"]), "Z"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        return coords

        #super(NetCDF_CF_Gridded, self).create_coords(filenames)

        # Something like:
        # for lat_p in lat:
        #     for lon_p in lon:
        #         for alt_p in alt:
        #             for time_p in time:
        #                 points.append(HyperPoint(lat_p,lon_p,alt_p,time_p))


    def create_data_object(self, filenames, variable):
        from jasmin_cis.exceptions import InvalidVariableError
        import iris

        var_constraint = iris.AttributeConstraint(name=variable)
        # Create an Attribute constraint on the name Attribute for the variable given

        try:
            cube = iris.load_cube(filenames, var_constraint)
        except iris.exceptions.ConstraintMismatchError:
            raise InvalidVariableError("Variable not found: " + variable +
                                       "\nTo see a list of variables run: cis info " + filenames[0] + " -h")

        sub_cube = list(cube.slices([ coord for coord in cube.coords() if coord.points.size > 1]))[0]
        #  Ensure that there are no extra dimensions which can confuse the plotting.
        # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about
        #  the dimension whose length is one. The above list comprehension would return a cube of
        #  shape (145, 165)

        return sub_cube

class Aeronet(AProduct):

    def get_file_signature(self):
        #TODO Update this
        return [r'\.lev20']

    def create_coords(self, filenames):
        from data_io.ungridded_data import Metadata
        from numpy import array
        from data_io.aeronet import load_aeronet, get_file_metadata

        for filename in filenames:
            data_obj = load_aeronet(filename)
            metadata = get_file_metadata(filename)
            lon = metadata.misc[2][1].split("=")[1]
            lat = metadata.misc[2][2].split("=")[1]

            coords = CoordList()
            coords.append(Coord(array([lon]), Metadata(name="Longitude", shape=(1,), units="degrees_east", range=(-180,180), missing_value=-999)))
            coords.append(Coord(array([lat]), Metadata(name="Latitude", shape=(1,), units="degrees_north", range=(-90,90), missing_value=-999)))
            date_time_data = data_obj["datetime"]
            coords.append(Coord(date_time_data, Metadata(name="Date time", shape=(len(date_time_data),), units="Time_units"), "X"))

        return coords

    def create_data_object(self, filenames, variable):
        from data_io.aeronet import load_aeronet, get_file_metadata
        data = []
        filename = filenames[0]
        data_obj = load_aeronet(filename)
        var_data = data_obj[variable]
        metadata = get_file_metadata(filename, variable, (len(var_data),))
        return UngriddedData(var_data, metadata, self.create_coords([filename]))

