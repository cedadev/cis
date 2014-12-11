from unittest import TestCase
from hamcrest import assert_that, is_, instance_of
from mock import MagicMock
from jasmin_cis.data_io.products.NCAR_NetCDF_RAF import NCAR_NetCDF_RAF_variable_name_selector
from jasmin_cis.exceptions import InvalidVariableError


class TestDataReader(TestCase):

    def test_GIVEN_no_attributes_or_variables_WHEN_construct_THEN_throw_exception(self):
        variables = []
        attributes = {}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No variables in the file so the type of data is unknown"))

    def test_GIVEN_no_attributes_WHEN_construct_THEN_throw_exception(self):
        variables = ["Var"]
        attributes = {}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No attributes in the file so type of data is unknown"))

    def test_GIVEN_no_time_coordinate_or_general_coordinates_WHEN_construct_THEN_throw_exception(self):
        variables = ["Var"]
        attributes = {"not time": "not time"}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No attributes indicating time variable name, expecting either 'Time_Coordinate' or 'Coordinates'"))

    def test_GIVEN_time_coordinate_but_no_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = ["not time var"]
        attributes = {"Time_Coordinate": expected_time_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("There is no variable for the time co-ordinate '{}'".format(expected_time_var)))

    def test_GIVEN_time_coordinate_but_no_lat_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = [expected_time_var]
        attributes = {"Time_Coordinate": expected_time_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No attributes indicating latitude, expecting 'Station_Lat' or 'Longitude_Coordinate'"))

    def test_GIVEN_time_coordinate_station_lat_but_no_lon_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = [expected_time_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": "27.2"}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No attributes indicating longitude, expecting 'Station_Lon'"))

    def test_GIVEN_time_coordinate_station_lat_and_lon_variable_WHEN_construct_THEN_names_are_correct(self):
        expected_time_var = "time_var"
        expected_station_latitude = "27.1"
        expected_station_longitude = "10"
        variables = [expected_time_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": expected_station_latitude,
                      "Station_Lon": expected_station_longitude}

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.station, is_(True), "File should be for station")
        assert_that(decider.time_variable_name, is_(expected_time_var))
        assert_that(decider.station_latitude, is_(expected_station_latitude))
        assert_that(decider.station_longitude, is_(expected_station_longitude))
        assert_that(decider.altitude, is_(0))

    def test_GIVEN_station_alt_WHEN_construct_THEN_alt_set(self):
        expected_time_var = "time_var"
        expected_station_latitude = "27.1"
        expected_station_longitude = "10"
        expected_alt = 125.4
        variables = [expected_time_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": expected_station_latitude,
                      "Station_Lon": expected_station_longitude,
                      "Station_Altitude": expected_alt}

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.altitude, is_(expected_alt))

    def test_GIVEN_time_coordinate_station_lat_and_lon_variable_and_alt_in_different_case_WHEN_construct_THEN_values_are_correct(self):
        expected_time_var = "time_var"
        expected_station_latitude = "27.1"
        expected_station_longitude = "10"
        expected_alt = 125.4
        variables = [expected_time_var]
        attributes = {"tIME_CoorDinate": expected_time_var,
                      "StatioN_lat": expected_station_latitude,
                      "StaTion_Lon": expected_station_longitude,
                      "StAtion_Altitude": expected_alt}

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.station, is_(True), "File should be for station")
        assert_that(decider.time_variable_name, is_(expected_time_var))
        assert_that(decider.station_latitude, is_(expected_station_latitude))
        assert_that(decider.station_longitude, is_(expected_station_longitude))
        assert_that(decider.altitude, is_(expected_alt))

    def test_GIVEN_time_coordinate_variable_lat_but_lat_variable_does_not_exist_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        variables = [expected_time_var, "not LON"]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("There is no variable for the latitude co-ordinate '{}'".format(expected_lat_var)))

    def test_GIVEN_time_coordinate_variable_lat_but_no_lon_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        variables = [expected_time_var, expected_lat_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("No attributes indicating longitude variable name, expecting 'Longitude_Coordinate'"))

    def test_GIVEN_time_coordinate_variable_lat_lon_but_lon_variable_does_not_exist_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        variables = [expected_time_var, expected_lat_var, "not LAT"]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("There is no variable for the longitude co-ordinate '{}'".format(expected_lon_var)))

    def test_GIVEN_time_coordinate_variable_lat_lon_with_no_alt_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        variables = [expected_time_var, expected_lat_var, expected_lon_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.station, is_(False), "station")
        assert_that(selector.time_variable_name, is_(expected_time_var), "time variable name")
        assert_that(selector.longitude_variable_name, is_(expected_lon_var), "longitude variable name")
        assert_that(selector.latitude_variable_name, is_(expected_lat_var), "latitude variable name")
        assert_that(selector.altitude, is_(0), "altitude is fixed at zero")
        assert_that(selector.pressure_variable_name, is_(None), "pressure variable name")

    def test_GIVEN_time_coordinate_variable_lat_lon_alt_but_alt_variable_does_not_exist_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [expected_time_var, expected_lat_var, "not ALT", expected_lon_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var,
                      "Vertical_Coordinate": expected_alt_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("There is no variable for the vertical co-ordinate '{}'".format(expected_alt_var)))

    def test_GIVEN_time_coordinate_variable_lat_lon_alt_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_alt_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var,
                      "Vertical_Coordinate": expected_alt_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.altitude, is_(None), "altitude not fixed")
        assert_that(selector.altitude_variable_name, is_(expected_alt_var), "altitude var name")

    def test_GIVEN_time_coordinate_variable_lat_lon_with_PSXC_WHEN_construct_THEN_pressure_name_is_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_pressure_var = "PSXC"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_pressure_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.pressure_variable_name, is_(expected_pressure_var), "pressure variable name")

    def test_GIVEN_time_coordinate_variable_lat_lon_with_PRE_WHEN_construct_THEN_pressure_name_is_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_pressure_var = "PRE"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_pressure_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.pressure_variable_name, is_(expected_pressure_var), "pressure variable name")

    def test_GIVEN_time_coordinate_variable_lat_lon_with_PRE_and_PSXC_WHEN_construct_THEN_pressure_name_is_set_to_PSXC(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_pressure_var = "PSXC"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_pressure_var, "PRE"]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.pressure_variable_name, is_(expected_pressure_var), "pressure variable name")

    def test_GIVEN_coordinate_attribute_which_does_not_have_four_variables_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [expected_time_var, expected_lat_var, expected_alt_var, expected_lon_var]
        attributes = {"Coordinates": "incorect"}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("The coordinate attribute does not have four entries. It should be space separated \"longitude latitude altitude time\""))

    def test_GIVEN_coordinate_attribute_but_no_variable_for_one_value_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, "NOT ALT"]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var, expected_alt_var, expected_time_var)}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.message, is_("There is no variable for the co-ordinate '{}'".format(expected_alt_var)))

    def test_GIVEN_coordinate_attribute_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_alt_var]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var, expected_alt_var, expected_time_var)}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.station, is_(False), "station")
        assert_that(selector.time_variable_name, is_(expected_time_var), "time variable name")
        assert_that(selector.longitude_variable_name, is_(expected_lon_var), "longitude variable name")
        assert_that(selector.latitude_variable_name, is_(expected_lat_var), "latitude variable name")
        assert_that(selector.altitude, is_(None), "altitude not fixed")
        assert_that(selector.altitude_variable_name, is_(expected_alt_var), "altitude var name")
        assert_that(selector.pressure_variable_name, is_(None), "pressure variable name")

    def test_GIVEN_coordinate_attribute_and_pressure_WHEN_construct_THEN_pressure_name_is_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        expected_pres_var = "PSXC"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_alt_var, expected_pres_var]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var, expected_alt_var, expected_time_var)}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.station, is_(False), "station")
        assert_that(selector.time_variable_name, is_(expected_time_var), "time variable name")
        assert_that(selector.longitude_variable_name, is_(expected_lon_var), "longitude variable name")
        assert_that(selector.latitude_variable_name, is_(expected_lat_var), "latitude variable name")
        assert_that(selector.altitude, is_(None), "altitude not fixed")
        assert_that(selector.altitude_variable_name, is_(expected_alt_var), "altitude var name")
        assert_that(selector.pressure_variable_name, is_(expected_pres_var), "pressure variable name")

    def test_GIVEN_time_coordinate_variable_lat_lon_alt_with_timestamp_WHEN_construct_THEN_timestamp_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        expected_timestamp = "timestamp"
        variables = [expected_time_var, expected_lat_var, expected_lon_var, expected_alt_var]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var,
                      "Vertical_Coordinate": expected_alt_var,
                      "Time_Stamp_Info": expected_timestamp}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.time_stamp_info, is_(expected_timestamp), "time stamp info")