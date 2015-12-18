import logging
from cis.data_io.Coord import CoordList
from cis.data_io.products import AProduct
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData
from abc import ABCMeta, abstractmethod


class CCI(object):
    """
    Abstract class for the various possible data products. This just defines the interface which
    the subclasses must implement.
    """
    __metaclass__ = ABCMeta

    def _create_coord_list(self, filenames):

        from cis.data_io.netcdf import read_many_files_individually, get_metadata
        from cis.data_io.Coord import Coord
        from cis.exceptions import InvalidVariableError

        try:
            variables = ["lon", "lat", "time"]
            data = read_many_files_individually(filenames, variables)
        except InvalidVariableError:
            variables = ["longitude", "latitude", "time"]
            data = read_many_files_individually(filenames, variables)

        logging.info("Listing coordinates: " + str(variables))

        coords = CoordList()
        coords.append(Coord(data[variables[0]], get_metadata(data[variables[0]][0]), "X"))
        coords.append(Coord(data[variables[1]], get_metadata(data[variables[1]][0]), "Y"))
        coords.append(self._fix_time(Coord(data[variables[2]], get_metadata(data[variables[2]][0]), "T")))

        return coords

    @abstractmethod
    def _fix_time(self, coords):
        pass

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from cis.data_io.netcdf import get_metadata, read_many_files_individually

        coords = self._create_coord_list(filenames)
        var = read_many_files_individually(filenames, [variable])
        metadata = get_metadata(var[variable][0])

        return UngriddedData(var[variable], metadata, coords)


class Cloud_CCI(CCI, AProduct):

    def get_file_signature(self):
        return [r'..*ESACCI.*CLOUD.*']

    def _fix_time(self, coord):
        coord.convert_julian_to_std_time()
        return coord

    def get_file_format(self, filenames):
        return "NetCDF/Cloud_CCI"


class Aerosol_CCI(CCI, AProduct):

    valid_dimensions = ["pixel_number"]

    def get_file_signature(self):
        return [r'.*ESACCI.*AEROSOL.*']

    def _fix_time(self, coord):
        import datetime
        coord.convert_TAI_time_to_std_time(datetime.datetime(1970, 1, 1))
        return coord

    def get_file_format(self, filename):
        return "NetCDF/Aerosol_CCI"
