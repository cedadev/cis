import logging
from jasmin_cis.data_io.Coord import CoordList
from jasmin_cis.data_io.products import AProduct
from jasmin_cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData


class Cloud_CCI(AProduct):

    def get_file_signature(self):
        return [r'..*ESACCI.*CLOUD.*']

    def _create_coord_list(self, filenames):

        from jasmin_cis.data_io.netcdf import read_many_files_individually, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = ["lat", "lon", "time"]
        logging.info("Listing coordinates: " + str(variables))

        var_data = read_many_files_individually(filenames, variables)

        coords = CoordList()
        coords.append(Coord(var_data['lat'], get_metadata(var_data['lat'][0]), 'Y'))
        coords.append(Coord(var_data['lon'], get_metadata(var_data['lon'][0]),'X'))
        time_coord = Coord(var_data['time'], get_metadata(var_data['time'][0]))

        # TODO: Is this really julian?
        time_coord.convert_julian_to_std_time()
        coords.append(time_coord)

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):

        from jasmin_cis.data_io.netcdf import get_metadata, read_many_files_individually

        coords = self._create_coord_list(filenames)
        var = read_many_files_individually(filenames, [variable])
        metadata = get_metadata(var[variable][0])

        return UngriddedData(var[variable], metadata, coords)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "NetCDF/Cloud_CCI"


class Aerosol_CCI(AProduct):

    valid_dimensions = ["pixel_number"]

    def get_file_signature(self):
        return [r'.*ESACCI.*AEROSOL.*']

    def _create_coord_list(self, filenames):

        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord
        import datetime

        #!FIXME: when reading an existing file variables might be "latitude", "longitude"
        variables = ["lat", "lon", "time"]
        logging.info("Listing coordinates: " + str(variables))

        data = read_many_files(filenames, variables, dim="pixel_number")

        coords = CoordList()
        coords.append(Coord(data["lon"], get_metadata(data["lon"]), "X"))
        coords.append(Coord(data["lat"], get_metadata(data["lat"]), "Y"))
        time_coord = Coord(data["time"], get_metadata(data["time"]), "T")
        time_coord.convert_TAI_time_to_std_time(datetime.datetime(1970,1,1))
        coords.append(time_coord)

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata

        coords = self._create_coord_list(filenames)
        data = read_many_files(filenames, variable, dim="pixel_number")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "NetCDF/Aerosol_CCI"