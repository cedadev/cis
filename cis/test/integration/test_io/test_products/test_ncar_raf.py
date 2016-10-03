import unittest

from hamcrest import *

from cis.data_io.products.NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from cis.test.integration.test_io.test_products.test_data_products import ProductTests
from cis.test.integration_test_data import cis_test_files


class TestNCAR_NetCDF_RAF(ProductTests, unittest.TestCase):
    def setUp(self):
        self.setup(cis_test_files["NCAR_NetCDF_RAF"], NCAR_NetCDF_RAF)

    def test_can_concatenate_files_with_different_time_stamps(self):
        from cis import read_data
        import numpy as np
        from cis.test.integration_test_data import valid_GASSP_station_files_with_different_timestamps,\
            valid_GASSP_station_var_with_different_timestamps
        var = valid_GASSP_station_var_with_different_timestamps
        filename = valid_GASSP_station_files_with_different_timestamps
        data = read_data(filename, var)
        time_coord = data.coord(axis='T')
        assert_that(np.min(time_coord.data), close_to(149107 + 54690.0/86400, 1e-5))
        assert_that(np.max(time_coord.data), close_to(149110 + 81330.0/86400, 1e-5))

    def test_can_concatenate_aircraft_files(self):
        from cis import read_data
        from cis.test.integration_test_data import valid_GASSP_aircraft_files_with_different_timestamps,\
            valid_GASSP_aircraft_var_with_different_timestamps
        data = read_data(valid_GASSP_aircraft_files_with_different_timestamps,
                         valid_GASSP_aircraft_var_with_different_timestamps)
        time_coord = data.coord(axis='T')
        assert_that(len(time_coord.data), equal_to(63609))


class TestNCAR_NetCDF_RAF_with_GASSP_aux_coord(ProductTests, unittest.TestCase):

    def setUp(self):
        self.setup(cis_test_files["GASSP_aux_coord"], NCAR_NetCDF_RAF)

    def test_variable_wildcarding(self):
        # We get all of the variables from the file like this - but this isn't the same as the set defined in the
        #  test data because they are all the same shape. These aren't.
        self.vars = [u'AREADIST_DMA_OPC', u'VOLDIST_DMA_OPC', u'DYNAMIC_PRESSURE', u'NUMDIST_DMA_OPC', u'PRESSURE_ALTITUDE',
                     u'LONGITUDE', u'RELATIVE_HUMIDITY', u'AIR_TEMPERATURE', u'AIR_PRESSURE', u'TIME', u'LATITUDE']
        super(TestNCAR_NetCDF_RAF_with_GASSP_aux_coord, self).test_variable_wildcarding()


class TestNCAR_NetCDF_RAF_with_GASSP_aeroplane(ProductTests, unittest.TestCase):

    def setUp(self):
        self.setup(cis_test_files["GASSP_aeroplane"], NCAR_NetCDF_RAF)


class TestNCAR_NetCDF_RAF_with_GASSP_ship(ProductTests, unittest.TestCase):

    def setUp(self):
        self.setup(cis_test_files["GASSP_ship"], NCAR_NetCDF_RAF)


class TestNCAR_NetCDF_RAF_with_GASSP_station(ProductTests, unittest.TestCase):

    def setUp(self):
        self.setup(cis_test_files["GASSP_station"], NCAR_NetCDF_RAF)


class TestNCAR_NetCDF_RAF_get_file_type_error(unittest.TestCase):

    def test_WHEN_file_is_GASSP_THEN_no_errors(self):
        from cis.test.integration_test_data import valid_GASSP_station_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_GASSP_station_filename)

        assert_that(errors, is_(None), "file should be GASSP")

    def test_WHEN_file_is_NCAR_RAF_THEN_no_errors(self):
        from cis.test.integration_test_data import valid_NCAR_NetCDF_RAF_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_NCAR_NetCDF_RAF_filename)

        assert_that(errors, is_(None), "file should be GASSP")

    def test_WHEN_file_dose_not_exist_THEN_errors(self):
        from cis.test.integration_test_data import invalid_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(invalid_filename)

        assert_that(errors, is_(["File does not exist"]), "file should not exist")

    def test_WHEN_file_is_not_NCAR_RAF_OR_GASSP_THEN_errors(self):
        from cis.test.integration_test_data import valid_hadgem_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_hadgem_filename)

        assert_that(len(errors), is_(1), "file should not be GASSP")

    def test_WHEN_file_is_not_netcdf_THEN_errors(self):
        from cis.test.integration_test_data import valid_aeronet_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_aeronet_filename)

        assert_that(len(errors), is_(2), "file should not be netcdf")
