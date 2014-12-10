import logging
from data_io.Coord import CoordList
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.data_io.products.abstract_NetCDF_CF import abstract_NetCDF_CF
from data_io.ungridded_data import UngriddedCoordinates, UngriddedData
from utils import add_to_list_if_not_none


class NCAR_NetCDF_RAF_variable_name_selector(object):
    """
    This should successful differentiate the names of the variables for the various dimensions in NCAR-RAF and GASSP.
    The variables set are:
    station: True if this is for a fixed station data, False otherwise
    station_latitude: the latitude of the station (set only if station is true)
    station_longitude: the longitude of the station (set only if station is true)
    altitude: Altitude of the measurement if it is fixed, none if this is not fixed, defaults to DEFAULT_ALTITUDE
    time_variable_name: variable name for time
    latitude_variable_name: variable name of the latitude, None if fixed
    longitude_variable_name: variable name of the longitude, None if fixed
    altitude_variable_name: variable name of the altitude, None if fixed
    pressure_variable_name: variable name of the pressure, None if not included in data

    The choice are in order of preference:
    Aeroplane GASSP (Data with time, lat, lon and altitude vars)
    Ship GASSP (Data with time, lat and lon vars but fixed altitude)
    Station GASSP (Data with time vars but fixed lat, lon and altitude)
    NCAR-RAF: (Data with time, lat, lon and altitude, but names are defined in coordinates attribute)
    """

    TIME_COORDINATE_NAME = 'Time_Coordinate'
    LATITUDE_COORDINATE_NAME = 'Latitude_Coordinate'
    LONGITUDE_COORDINATE_NAME = 'Longitude_Coordinate'
    ALTITUDE_COORDINATE_NAME = 'Vertical_Coordinate'
    CORRECTED_PRESSURE_VAR_NAME = 'PSXC'
    PRESSURE_VAR_NAME = 'PRE'

    BEST_COORDINATES_NAME = 'Coordinates'

    STATION_LATITUDE_NAME = 'Station_Lat'
    STATION_LONGITUDE_NAME = 'Station_Lon'
    STATION_ALTITUDE_NAME = 'Station_Altitude'
    DEFAULT_ALTITUDE = 0

    def get_coordinate_variable_name(self, attribute_name, coordinate_display_name):
        """
        Reads an attribute value for a co-ordinate and returns the value. Checks that value is a variables in the data
        Throws InvalidVariableError if the attribute or variable does not exist
        :param attribute_name: the name of the attribute to read
        :param coordinate_display_name: the display name of the attribute read
        :returns: the variable name
        """
        if attribute_name.lower() in self._attributes:
            variable_name = self._attributes[attribute_name.lower()]
            if variable_name not in self._variables:
                raise InvalidVariableError("There is no variable for the {} co-ordinate '{}'"
                                           .format(coordinate_display_name, variable_name))
            return variable_name

        raise InvalidVariableError(
            "No attributes indicating {} variable name, expecting '{}'"
            .format(coordinate_display_name, attribute_name))

    def __init__(self, attributes, variables):
        self.station = False
        self.station_latitude = None
        self.latitude_variable_name = None
        self.station_longitude = None
        self.longitude_variable_name = None
        self.altitude = None
        self.altitude_variable_name = None
        self.pressure_variable_name = None

        self._attributes = {k.lower(): v for k, v in attributes.items()}
        self._variables = variables
        self._check_have_variables_and_attribure()

        if self.TIME_COORDINATE_NAME.lower() in self._attributes:
            self.time_variable_name = self.get_coordinate_variable_name(self.TIME_COORDINATE_NAME, "time")

            if self.LATITUDE_COORDINATE_NAME.lower() in self._attributes:
                self._lat_lon_var_specified_setup()
            elif self.STATION_LATITUDE_NAME.lower() in self._attributes:
                self._stationary_setup()
            else:
                raise InvalidVariableError("No attributes indicating latitude, expecting '{}' or '{}'"
                                           .format(self.STATION_LATITUDE_NAME, self.LONGITUDE_COORDINATE_NAME))
        elif self.BEST_COORDINATES_NAME.lower() in self._attributes:
            self._best_coordinates_setup()
        else:
            raise InvalidVariableError(
                "No attributes indicating time variable name, expecting either '{}' or 'Coordinates'"
                .format(self.TIME_COORDINATE_NAME))

        if self.CORRECTED_PRESSURE_VAR_NAME in self._variables:
            self.pressure_variable_name = self.CORRECTED_PRESSURE_VAR_NAME
        elif self.PRESSURE_VAR_NAME in self._variables:
            self.pressure_variable_name = self.PRESSURE_VAR_NAME
        else:
            self.pressure_variable_name = None

    def _stationary_setup(self):
        """
        Set up object when latitude and longitude are fixed
        """
        if self.STATION_LATITUDE_NAME.lower() not in self._attributes:
            raise InvalidVariableError("No attributes indicating latitude, expecting '{}'"
                                       .format(self.STATION_LATITUDE_NAME))
        self.station_latitude = self._attributes[self.STATION_LATITUDE_NAME.lower()]

        if self.STATION_LONGITUDE_NAME.lower() not in self._attributes:
            raise InvalidVariableError("No attributes indicating longitude, expecting '{}'"
                                       .format(self.STATION_LONGITUDE_NAME))
        self.station_longitude = self._attributes[self.STATION_LONGITUDE_NAME.lower()]
        self.station = True

        if self.STATION_ALTITUDE_NAME.lower() in self._attributes:
            self.altitude = self._attributes[self.STATION_ALTITUDE_NAME.lower()]
        else:
            self.altitude = self.DEFAULT_ALTITUDE

    def _check_have_variables_and_attribure(self):
        """
        Check that netcdf file has variables and attributes
        """
        if self._variables is None or len(self._variables) == 0:
            raise InvalidVariableError("No variables in the file so the type of data is unknown")
        if self._attributes is None or len(self._attributes) == 0:
            raise InvalidVariableError("No attributes in the file so type of data is unknown")

    def _lat_lon_var_specified_setup(self):
        """
        Set up object when latitude and longitude variables are being used
        """

        self.latitude_variable_name = self.get_coordinate_variable_name(self.LATITUDE_COORDINATE_NAME, "latitude")
        self.longitude_variable_name = self.get_coordinate_variable_name(self.LONGITUDE_COORDINATE_NAME, "longitude")

        if self.ALTITUDE_COORDINATE_NAME.lower() in self._attributes:
            self.altitude_variable_name = self.get_coordinate_variable_name(self.ALTITUDE_COORDINATE_NAME, "vertical")
        else:
            self.altitude = self.DEFAULT_ALTITUDE

    def _best_coordinates_setup(self):
        """
        Set up object when coordinates attribute is found
        """
        coordinates_vars = []
        coordinates = self._attributes[self.BEST_COORDINATES_NAME.lower()]
        if coordinates is not None:
            coordinates_vars = coordinates.split()  # split on whitespace

        if len(coordinates_vars) is not 4:
            raise InvalidVariableError('The coordinate attribute does not have four entries. '
                                       'It should be space separated "longitude latitude altitude time"')

        for coordinates_var in coordinates_vars:
            if coordinates_var not in self._variables:
                raise InvalidVariableError("There is no variable for the co-ordinate '{}'".format(coordinates_var))

        self.longitude_variable_name, \
            self.latitude_variable_name, \
            self.altitude_variable_name, \
            self.time_variable_name \
            = coordinates_vars


class NCAR_NetCDF_RAF(abstract_NetCDF_CF):
    """
    Data product for NCAR-RAF NetCDF files. This includes the subset of GASSP (which is its major use case)
    """
    def __init__(self, variableSelectorClass=NCAR_NetCDF_RAF_variable_name_selector):
        self.variableSelectorClass = variableSelectorClass

    def get_file_signature(self):
        return [r'.*\.nc']

    def create_coords(self, filenames, variable=None):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata, read_attributes_and_variables_many_files

        attributes, variables_list, variables = read_attributes_and_variables_many_files(filenames)
        variable_selector = self.variableSelectorClass(attributes, variables_list)

        variables_list = [variable_selector.time_variable_name]
        add_to_list_if_not_none(variable_selector.latitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.longitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.altitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.pressure_variable_name, variables_list)

        logging.info("Listing coordinates: " + str(variables_list))
        add_to_list_if_not_none(variable, variables_list)

        aggregation_dimension = variables[variable_selector.time_variable_name].dimensions[0]
        data_variables = read_many_files(filenames, variables_list, dim=aggregation_dimension)

        coords = CoordList()
        coords.append(self._create_coord("Y", variable_selector.latitude_variable_name, data_variables, "latitude"))
        coords.append(self._create_coord("X", variable_selector.longitude_variable_name, data_variables, "longitude"))
        coords.append(self._create_coord("Z", variable_selector.altitude_variable_name, data_variables, "altitude"))
        time_coord = self._create_coord("T", variable_selector.time_variable_name, data_variables, "time")
        time_coord.convert_to_std_time()
        coords.append(time_coord)

        if variable_selector.pressure_variable_name is not None:
            coords.append(
                self._create_coord("P", variable_selector.pressure_variable_name, data_variables, "air_pressure"))

        if variable is None:
            return UngriddedCoordinates(coords)
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

    def _create_coord(self, coord_axis, data_variable_name, data_variables, standard_name):
        """
        Create a coordinate for the co-ordinate list
        :param coord_axis: axis of the coordinate in the coords
        :param data_variable_name: the name of the variable in the data
        :param data_variables: the data variables
        :param standard_name: the standard name it should have
        :return: a coords object
        """
        from jasmin_cis.data_io.netcdf import get_metadata
        from jasmin_cis.data_io.Coord import Coord

        data_variable = data_variables[data_variable_name]
        metadata = get_metadata(data_variable)
        metadata.alter_standard_name(standard_name)
        return Coord(data_variable, metadata, coord_axis)