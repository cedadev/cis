import unittest

from hamcrest import assert_that, is_, close_to

from cis import read_data
from cis.test.integration_test_data import *


class TestNetCDF_CF_Gridded_ECHAM_Hybrid_Pressure_Geopotential(unittest.TestCase):

    data = None

    def read_data(self):
        # Only do this once
        if self.data is None:
            filename = valid_echamham_geopotential_filename
            var = valid_echamham_geopotential_variable
            self.data = read_data(filename, var)

    def test_GIVEN_hybrid_pressure_readable_by_iris_WHEN_read_THEN_pressure_coordinate_present(self):
        self.read_data()
        # The air pressure aux coord is a CF compliant aux coord which IRIS identifies
        pressure = self.data.coord('air_pressure')
        assert_that(pressure.shape, is_((248, 31, 96, 192)))

    def test_GIVEN_altitude_not_read_by_iris_WHEN_read_THEN_pressure_coordinate_present(self):
        self.read_data()
        # The altitude aux coord is CF compliant but not identified by IRIS so we manually create it
        altitude = self.data.coord('altitude')
        assert_that(altitude.shape, is_((248, 31, 96, 192)))
        # Check it has been converted to meters
        assert_that(str(altitude.units), is_('meter'))
        assert_that(altitude.points[0, 0, 0, 0], close_to(275081.0 / 9.80665, 0.1))


class TestNetCDF_CF_Gridded_ECHAM_Hybrid_Pressure_Geopotential_Height(unittest.TestCase):

    data = None

    def read_data(self):
        # Only need to do this once
        if self.data is None:
            filename = valid_echamham_geopotential_height_filename
            var = valid_echamham_geopotential_height_variable
            self.data = read_data(filename, var)

    def test_GIVEN_hybrid_pressure_readable_by_iris_WHEN_read_THEN_pressure_coordinate_present(self):
        self.read_data()
        # The air pressure aux coord is a CF compliant aux coord which IRIS identifies
        pressure = self.data.coord('air_pressure')
        assert_that(pressure.shape, is_((248, 31, 96, 192)))

    def test_GIVEN_altitude_not_read_by_iris_WHEN_read_THEN_pressure_coordinate_present(self):
        self.read_data()
        # The altitude aux coord is CF compliant but not identified by IRIS so we manually create it
        altitude = self.data.coord('altitude')
        assert_that(altitude.shape, is_((248, 31, 96, 192)))

if __name__ == '__main__':
    unittest.main()
