import logging
from cis.data_io.Coord import Coord, CoordList
from cis.data_io.products.AProduct import AProduct
from cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedCoordinates
import cis.utils as utils


class cis(AProduct):
    # If a file matches the CIS product signature as well as another signature (e.g. because we aggregated from another
    # data product) we need to prioritise the CIS data product
    priority = 100

    def get_file_signature(self):
        return [r'cis\-.*\.nc']

    def create_coords(self, filenames, usr_variable=None):
        from cis.data_io.netcdf import read_many_files_individually, get_metadata
        from cis.data_io.Coord import Coord
        from cis.exceptions import InvalidVariableError

        variables = [("longitude", "x"), ("latitude", "y"), ("altitude", "z"), ("time", "t"), ("air_pressure", "p")]

        logging.info("Listing coordinates: " + str(variables))

        coords = CoordList()
        for variable in variables:
            try:
                var_data = read_many_files_individually(filenames, variable[0])[variable[0]]
                coords.append(Coord(var_data, get_metadata(var_data[0]), axis=variable[1]))
            except InvalidVariableError:
                pass

        # Note - We don't need to convert this time coord as it should have been written in our
        #  'standard' time unit

        if usr_variable is None:
            res = UngriddedCoordinates(coords)
        else:
            usr_var_data = read_many_files_individually(filenames, usr_variable)[usr_variable]
            res = UngriddedData(usr_var_data, get_metadata(usr_var_data[0]), coords)

        return res

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

    def get_file_format(self, filename):
        return "NetCDF/CIS"


class Aeronet(AProduct):
    def get_file_signature(self):
        return [r'.*\.lev20']

    def _create_coord_list(self, filenames, data=None):
        from cis.data_io.ungridded_data import Metadata
        from cis.data_io.aeronet import load_multiple_aeronet
        from cis.time_util import cis_standard_time_unit as ct

        if data is None:
            data = load_multiple_aeronet(filenames)

        coords = CoordList()
        coords.append(Coord(data['longitude'], Metadata(name="Longitude", shape=(len(data),),
                                                        units="degrees_east", range=(-180, 180))))
        coords.append(Coord(data['latitude'], Metadata(name="Latitude", shape=(len(data),),
                                                       units="degrees_north", range=(-90, 90))))
        coords.append(Coord(data['altitude'], Metadata(name="Altitude", shape=(len(data),), units="meters")))
        coords.append(Coord(data["datetime"], Metadata(name="DateTime", standard_name='time', shape=(len(data),),
                                                       units=str(ct)), "X"))

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from cis.data_io.aeronet import load_multiple_aeronet

        data_obj = load_multiple_aeronet(filenames, [variable])

        coords = self._create_coord_list(filenames, data_obj)

        return UngriddedData(data_obj[variable],
                             Metadata(name=variable, long_name=variable, shape=(len(data_obj),), missing_value=-999.0),
                             coords)


class ASCII_Hyperpoints(AProduct):
    def get_file_signature(self):
        return [r'.*\.txt']

    def get_variable_names(self, filenames, data_type=None):
        return ['value']

    def create_coords(self, filenames, variable=None):
        from cis.data_io.ungridded_data import Metadata
        from numpy import genfromtxt, NaN
        from cis.exceptions import InvalidVariableError
        from cis.time_util import convert_datetime_to_std_time
        import dateutil.parser as du

        array_list = []

        for filename in filenames:
            try:
                array_list.append(genfromtxt(filename, dtype="f8,f8,f8,O,f8",
                                             names=['latitude', 'longitude', 'altitude', 'time', 'value'],
                                             delimiter=',', missing_values='', usemask=True, invalid_raise=True,
                                             converters={"time": du.parse}))
            except:
                raise IOError('Unable to read file ' + filename)

        data_array = utils.concatenate(array_list)
        n_elements = len(data_array['latitude'])

        coords = CoordList()
        coords.append(Coord(data_array["latitude"],
                            Metadata(standard_name="latitude", shape=(n_elements,), units="degrees_north")))
        coords.append(Coord(data_array["longitude"],
                            Metadata(standard_name="longitude", shape=(n_elements,), units="degrees_east")))
        coords.append(
            Coord(data_array["altitude"], Metadata(standard_name="altitude", shape=(n_elements,), units="meters")))

        time_arr = convert_datetime_to_std_time(data_array["time"])
        time = Coord(time_arr,
                     Metadata(standard_name="time", shape=(n_elements,), units="days since 1600-01-01 00:00:00"))
        coords.append(time)

        if variable:
            try:
                data = UngriddedData(data_array['value'], Metadata(name="value", shape=(n_elements,), units="unknown",
                                                                   missing_value=NaN), coords)
            except:
                InvalidVariableError("Value column does not exist in file " + filenames)
            return data
        else:
            return UngriddedCoordinates(coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, True)

    def get_file_format(self, filenames):
        """
        Returns the file format
        """
        return "ASCII/ASCIIHyperpoints"

