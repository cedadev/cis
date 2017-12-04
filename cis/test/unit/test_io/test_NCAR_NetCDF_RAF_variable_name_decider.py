from unittest import TestCase
from hamcrest import *

from cis.data_io.products.NCAR_NetCDF_RAF import NCAR_NetCDF_RAF_variable_name_selector
from cis.exceptions import InvalidVariableError


class TestDataReader(TestCase):
    class MockVar(object):
        def __init__(self, dimensions=('Time',)):
            self.dimensions = dimensions

    def test_GIVEN_no_attributes_or_variables_WHEN_construct_THEN_throw_exception(self):
        variables = []
        attributes = {}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No variables in the file so the type of data is unknown"))

    def test_GIVEN_no_attributes_WHEN_construct_THEN_throw_exception(self):
        variables = [{"Var": self.MockVar()}]
        attributes = {}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No attributes in the file so type of data is unknown"))

    def test_GIVEN_no_time_coordinate_or_general_coordinates_WHEN_construct_THEN_throw_exception(self):
        variables = [{"Var": self.MockVar()}]
        attributes = {"not time": "not time"}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No attributes indicating time variable name, "
                                              "expecting either 'Time_Coordinate' or 'Coordinates'"))

    def test_GIVEN_time_coordinate_but_no_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = [{"not time var": self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("There is no variable for the time co-ordinate '{}'"
                                              .format(expected_time_var)))

    def test_GIVEN_time_coordinate_but_no_lat_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = [{expected_time_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No attributes indicating latitude, "
                                              "expecting 'Station_Lat' or 'Longitude_Coordinate'"))

    def test_GIVEN_time_coordinate_station_lat_but_no_lon_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        variables = [{expected_time_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": 27.2}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No attributes indicating longitude, expecting 'Station_Lon'"))

    def test_GIVEN_time_coordinate_station_lat_and_lon_variable_WHEN_construct_THEN_names_are_correct(self):
        expected_time_var = "time_var"
        expected_station_latitude = 27.1
        expected_station_longitude = 10
        variables = [{expected_time_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": expected_station_latitude,
                      "Station_Lon": expected_station_longitude}
        aggregated_dim = "Time"
        expected_time_dimensions = (aggregated_dim,)

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.station, is_(True), "File should be for station")
        assert_that(decider.time_variable_name, is_(expected_time_var))
        assert_that(decider.station_latitude, is_([expected_station_latitude]))
        assert_that(decider.station_longitude, is_([expected_station_longitude]))
        assert_that(decider.altitude, is_([0]))
        assert_that(decider.time_dimensions, is_(expected_time_dimensions))

    def test_GIVEN_station_alt_WHEN_construct_THEN_alt_set(self):
        expected_time_var = "time_var"
        expected_station_latitude = 27.1
        expected_station_longitude = 10
        expected_alt = 125.4
        variables = [{expected_time_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": expected_station_latitude,
                      "Station_Lon": expected_station_longitude,
                      "Station_Altitude": expected_alt}

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.altitude, is_([expected_alt]))

    def test_GIVEN_station_coords_in_different_cases_WHEN_construct_THEN_values_are_correct(
            self):
        expected_time_var = "time_var"
        expected_station_latitude = 27.1
        expected_station_longitude = 10
        expected_alt = 125.4
        variables = [{expected_time_var: self.MockVar()}]
        attributes = {"tIME_CoorDinate": expected_time_var,
                      "StatioN_lat": expected_station_latitude,
                      "StaTion_Lon": expected_station_longitude,
                      "StAtion_Altitude": expected_alt}

        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.station, is_(True), "File should be for station")
        assert_that(decider.time_variable_name, is_(expected_time_var))
        assert_that(decider.station_latitude, is_([expected_station_latitude]))
        assert_that(decider.station_longitude, is_([expected_station_longitude]))
        assert_that(decider.altitude, is_([expected_alt]))

    def test_GIVEN_time_coordinate_variable_lat_but_lat_variable_does_not_exist_WHEN_construct_THEN_throw_exception(
            self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        variables = [{expected_time_var: self.MockVar(), "not LON": self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("There is no variable for the latitude co-ordinate '{}'"
                                              .format(expected_lat_var)))

    def test_GIVEN_time_coordinate_variable_lat_but_no_lon_variable_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("No attributes indicating longitude variable name, "
                                              "expecting 'Longitude_Coordinate'"))

    def test_GIVEN_time_coordinate_variable_lat_lon_but_lon_variable_does_not_exist_WHEN_construct_THEN_throw_exception(
            self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(), "not LAT": self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("There is no variable for the longitude co-ordinate '{}'"
                                              .format(expected_lon_var)))

    def test_GIVEN_time_coordinate_variable_lat_lon_with_no_alt_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.station, is_(False), "station")
        assert_that(selector.time_variable_name, is_(expected_time_var), "time variable name")
        assert_that(selector.longitude_variable_name, is_(expected_lon_var), "longitude variable name")
        assert_that(selector.latitude_variable_name, is_(expected_lat_var), "latitude variable name")
        assert_that(selector.altitude, is_([0]), "altitude is fixed at zero")
        assert_that(selector.pressure_variable_name, is_(None), "pressure variable name")

    def test_GIVEN_time_coordinate_var_lat_lon_alt_but_alt_variable_does_not_exist_WHEN_construct_THEN_throw_exception(
            self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      "not ALT": self.MockVar(), expected_lon_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var,
                      "Vertical_Coordinate": expected_alt_var}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0],
                    is_("There is no variable for the vertical co-ordinate '{}'".format(expected_alt_var)))

    def test_GIVEN_time_coordinate_variable_lat_lon_alt_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_alt_var: self.MockVar()}]
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
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_pressure_var: self.MockVar()}]
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
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_pressure_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.pressure_variable_name, is_(expected_pressure_var), "pressure variable name")

    def test_GIVEN_time_coordinate_variable_lat_lon_with_PRE_and_PSXC_WHEN_construct_THEN_pressure_name_is_set_to_PSXC(
            self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_pressure_var = "PSXC"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_pressure_var: self.MockVar(), "PRE": self.MockVar()}]
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
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_alt_var: self.MockVar()}]
        attributes = {"Coordinates": "incorect"}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("The coordinate attribute does not have four entries. "
                                              "It should be space separated \"longitude latitude altitude time\""))

    def test_GIVEN_coordinate_attribute_but_no_variable_for_one_value_WHEN_construct_THEN_throw_exception(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"

        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), "NOT ALT": self.MockVar()}]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var,
                                                          expected_alt_var, expected_time_var)}

        with self.assertRaises(InvalidVariableError) as cm:
            NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(cm.exception.args[0], is_("There is no variable for the co-ordinate '{}'".format(expected_alt_var)))

    def test_GIVEN_coordinate_attribute_WHEN_construct_THEN_values_are_set(self):
        expected_time_var = "time_var"
        expected_lat_var = "LAT"
        expected_lon_var = "LON"
        expected_alt_var = "ALT"
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_alt_var: self.MockVar()}]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var,
                                                          expected_alt_var, expected_time_var)}

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
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_alt_var: self.MockVar(),
                      expected_pres_var: self.MockVar()}]
        attributes = {"Coordinates": "{} {} {} {}".format(expected_lon_var, expected_lat_var,
                                                          expected_alt_var, expected_time_var)}

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
        variables = [{expected_time_var: self.MockVar(), expected_lat_var: self.MockVar(),
                      expected_lon_var: self.MockVar(), expected_alt_var: self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Latitude_Coordinate": expected_lat_var,
                      "Longitude_Coordinate": expected_lon_var,
                      "Vertical_Coordinate": expected_alt_var,
                      "Time_Stamp_Info": expected_timestamp}

        selector = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(selector.time_stamp_info, is_([expected_timestamp]), "time stamp info")

    def test_GIVEN_valid_file_with_all_variables_same_shape_as_time_WHEN_get_vars_THEN_all_variables_returned(self):
        expected_time_var = "time_var"
        expected_station_latitude = "27.1"
        expected_station_longitude = "10"
        variables = [{expected_time_var: self.MockVar(), "another_var": self.MockVar()}]
        attributes = {"Time_Coordinate": expected_time_var,
                      "Station_Lat": expected_station_latitude,
                      "Station_Lon": expected_station_longitude}
        aggregated_dim = "Time"
        expected_time_dimensions = [aggregated_dim]
        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        vars = decider.get_variable_names_which_have_time_coord()

        assert_that(vars, all(variables), "File should be for station")

    def test_GIVEN_valid_file_with_one_variables_same_shape_others_not_WHEN_get_vars_THEN_only_same_shape_is_returned(
            self):
        time_dims = ["Time"]
        time_var = "time_var"
        expected_var = "good_shape"
        variable_dimensions = {
            time_var: time_dims,
            expected_var: time_dims,
            "too_many_dims": ["one", "two"],
            "too_few_dims": [],
            "Not time": ["not time"],
            "Time and one other": [time_dims[0], "other"]
        }
        attributes = {"Time_Coordinate": time_var,
                      "Station_Lat": "27.1",
                      "Station_Lon": "10"}

        variables = [{key: self.MockVar(val) for key, val in list(variable_dimensions.items())}]
        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        vars = decider.get_variable_names_which_have_time_coord()

        assert_that(vars, is_(set([expected_var, time_var, "Time and one other"])), "variables should be ones with same dim as time")

    def test_GIVEN_valid_file_w_1_var_same_shape_others_not_and_t_is_multid_WHEN_get_vars_THEN_only_same_shape_returned(
            self):
        time_dims = ["Time", "time2"]
        time_var = "time_var"
        expected_var = "good_shape"
        variable_dimensions = {
            time_var: time_dims,
            expected_var: time_dims,
            "too_many_dims": ["one", "two", "Three"],
            "too_few_dims": ["one"],
            "Not time": ["not time", "not Time"],
            "Time and one other": [time_dims[0], time_dims[1], "other"],
            "Time and Time": [time_dims[0], time_dims[0]],
            "Time2 and time": [time_dims[1], time_dims[0]]
        }
        attributes = {"Time_Coordinate": time_var,
                      "Station_Lat": "27.1",
                      "Station_Lon": "10"}

        variables = [{key: self.MockVar(val) for key, val in list(variable_dimensions.items())}]
        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        vars = decider.get_variable_names_which_have_time_coord()

        assert_that(vars, is_(set([expected_var, time_var, "Time and one other"])),
                    "variables should be ones with same dim as time")

    def test_GIVEN_valid_file_w_var_with_aux_coords_WHEN_find_auxiliary_coordinates_THEN_returns_aux_coords(self):
        time_dims = ["Time"]
        time_var = "time_var"
        expected_var = "good_shape"
        variable_dimensions = {
            time_var: time_dims,
            expected_var: time_dims,
            "extra_dim": [time_dims[0], "aux_coord"],
            "two_extra": [time_dims[0], "aux_coord", "another_aux"],
            "aux_coord": ["aux_coord"],
        }
        attributes = {"Time_Coordinate": time_var,
                      "Station_Lat": "27.1",
                      "Station_Lon": "10"}

        variables = [{key: self.MockVar(val) for key, val in list(variable_dimensions.items())}]
        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.find_auxiliary_coordinate(expected_var), is_(None))
        assert_that(decider.find_auxiliary_coordinate('extra_dim'), is_('aux_coord'))

        # Don't return variables with more than one aux coord (which would have to be more than 2D)
        with self.assertRaises(InvalidVariableError) as cm:
            decider.find_auxiliary_coordinate('two_extra')

    def test_GIVEN_valid_file_w_var_with_unnamed_aux_WHEN_find_auxiliary_coordinates_THEN_returns_aux_coords(self):
        """
        Test if we can find the right variable even if the auxiliary dimension has a different name
        """
        time_dims = ["Time"]
        time_var = "time_var"
        expected_var = "good_shape"
        variable_dimensions = {
            time_var: time_dims,
            expected_var: time_dims,
            "extra_dim": [time_dims[0], "aux_coord"],
            "two_extra": [time_dims[0], "aux_coord", "another_aux"],
            "aux_var": ["aux_coord"]
        }
        attributes = {"Time_Coordinate": time_var,
                      "Station_Lat": "27.1",
                      "Station_Lon": "10"}

        variables = [{key: self.MockVar(val) for key, val in list(variable_dimensions.items())}]
        decider = NCAR_NetCDF_RAF_variable_name_selector(attributes, variables)

        assert_that(decider.find_auxiliary_coordinate(expected_var), is_(None))
        assert_that(decider.find_auxiliary_coordinate('extra_dim'), is_('aux_var'))

        # Don't return variables with more than one aux coord (which would have to be more than 2D)
        with self.assertRaises(InvalidVariableError) as cm:
            decider.find_auxiliary_coordinate('two_extra')
