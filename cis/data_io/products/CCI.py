import logging
import six

from cis.data_io.Coord import CoordList
from cis.data_io.products import AProduct, NetCDF_Gridded
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData
from cf_units import Unit, CALENDAR_STANDARD
from abc import ABCMeta, abstractmethod


ESA_TIME_UNIT = Unit("hours since 1970-01-01 00:00:00", calendar=CALENDAR_STANDARD)


@six.add_metaclass(ABCMeta)
class CCI_L2(object):
    """
    Abstract class for the various Level 2 CCI data products. This just defines the interface which
    the subclasses must implement.
    """
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


class Cloud_CCI_L2(CCI_L2, AProduct):
    """Climate Change Initiative cloud data at satellite resolution (1km)."""

    def get_file_signature(self):
        return [r'.*ESACCI-L2_CLOUD.*']

    def _fix_time(self, coord):
        coord.convert_julian_to_std_time()
        return coord

    def get_file_format(self, filenames):
        return "NetCDF/Cloud_CCI_L2"


class Aerosol_CCI_L2(CCI_L2, AProduct):
    """Climate Change Initiative aerosol data at near-satellite resolution (10km)."""

    valid_dimensions = ["pixel_number"]

    def get_file_signature(self):
        return [r'.*ESACCI-L2P_AEROSOL.*']

    def _fix_time(self, coord):
        import datetime
        coord.convert_TAI_time_to_std_time(datetime.datetime(1970, 1, 1))
        return coord

    def get_file_format(self, filename):
        return "NetCDF/Aerosol_CCI_L2"


def convert_time_string_to_number(time_str, units):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    if "44T" in time_str:
        # Workaround a bug in the generation of timestamps in monthly Level 3 data
        time = datetime.strptime(time_str.replace("44T", "T"), "%Y%mT%H%M%SZ")
        time += relativedelta(months=1, days=-1)
    else:
        time = datetime.strptime(time_str, "%Y%m%dT%H%M%SZ")
    return units.date2num(time)


class Cloud_CCI_L3(NetCDF_Gridded):
    """Climate Change Initiative cloud data on a rectangular lat/lon grid."""

    def get_file_signature(self):
        return [r'.*ESACCI-L3C_CLOUD.*nc', r'.*ESACCI-L3U_CLOUD.*nc']

    def get_file_format(self, filenames):
        return "NetCDF/Cloud_CCI_L3"

    def load_single_file_callback(self, cube, field, filename):
        """Add time coordinate to cube"""
        time_coord = cube.coord("time")

        # Pop time attributes to remove them from the cube
        time_bounds = [convert_time_string_to_number(cube.attributes.pop(att), time_coord.units)
                       for att in ("time_coverage_start", "time_coverage_end")]
        time_coord.bounds = time_bounds

    def load_multiple_files_callback(self, cube, field, filename):
        """Remove attributes that vary from file to file"""
        for att in ('number_of_processed_orbits', 'id', 'tracking_id', 'date_created'):
            try:
                _ = cube.attributes.pop(att)
            except KeyError:
                pass

        self.load_single_file_callback(cube, field, filename)


class Aerosol_CCI_L3(NetCDF_Gridded):
    """Climate Change Initiative aerosol data on a rectangular lat/lon grid."""

    def get_file_signature(self):
        return [r'.*ESACCI-L3C_AEROSOL.*nc']

    def get_file_format(self, filenames):
        return "NetCDF/Aerosol_CCI_L3"

    def load_single_file_callback(self, cube, field, filename):
        """Add time coordinate"""
        from iris.coords import AuxCoord

        # Pop time attributes to remove them from the cube
        try:
            time_bounds = [convert_time_string_to_number(cube.attributes.pop(att), ESA_TIME_UNIT)
                           for att in ("time_coverage_start", "time_coverage_end")]
        except ValueError:
            if "201101-ESACCI" in filename:
                # Manually fix a bugged file
                # (201101-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR-ENVISAT-ADV_MOTNHLY-v2.30.nc)
                time_bounds = [convert_time_string_to_number(s, time_coord.units)
                               for s in ("20110101T000000Z", "20110131T235959Z")]
            else:
                raise ValueError("Bad time_coverage attribute in {}".format(filename))

        time_centre = 0.5 * sum(time_bounds)
        time_coord = AuxCoord(time_centre, standard_name="time", units=ESA_TIME_UNIT, bounds=time_bounds)
        cube.add_aux_coord(time_coord)

    def load_multiple_files_callback(self, cube, field, filename):
        """Remove attributes that vary from file to file"""
        for att in ('id', 'tracking_id', 'date_created', 'time_coverage_duration', 'history', 'inputfilelist'):
            try:
                _ = cube.attributes.pop(att)
            except KeyError:
                pass

        self.load_single_file_callback(cube, field, filename)
