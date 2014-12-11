from hamcrest import *
from jasmin_cis.data_io.products.NCAR_NetCDF_RAF import NCAR_NetCDF_RAF
from test.integration.test_io.test_products.test_data_products import ProductTests


class TestNCAR_NetCDF_RAF(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_NCAR_NetCDF_RAF_filename, valid_NCAR_NetCDF_RAF_variable
        self.filename = valid_NCAR_NetCDF_RAF_filename
        self.valid_variable = valid_NCAR_NetCDF_RAF_variable
        self.product = NCAR_NetCDF_RAF


class TestNCAR_NetCDF_RAF_with_GASSP_aeroplan(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_GASSP_aeroplane_filename, valid_GASSP_aeroplane_variable
        self.filename = valid_GASSP_aeroplane_filename
        self.valid_variable = valid_GASSP_aeroplane_variable
        self.product = NCAR_NetCDF_RAF


class TestNCAR_NetCDF_RAF_with_GASSP_ship(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_GASSP_ship_filename, valid_GASSP_ship_variable
        self.filename = valid_GASSP_ship_filename
        self.valid_variable = valid_GASSP_ship_variable
        self.product = NCAR_NetCDF_RAF


class TestNCAR_NetCDF_RAF_with_GASSP_station(ProductTests):

    def __init__(self):
        from jasmin_cis.test.test_files.data import valid_GASSP_station_filename, valid_GASSP_station_variable
        self.filename = valid_GASSP_station_filename
        self.valid_variable = valid_GASSP_station_variable
        self.product = NCAR_NetCDF_RAF


class TestNCAR_NetCDF_RAF_File_Test(object):

    def test_WHEN_file_is_GASSP_THEN_no_errors(self):
        from jasmin_cis.test.test_files.data import valid_GASSP_station_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_GASSP_station_filename)

        assert_that(errors, is_(None), "file should be GASSP")

    def test_WHEN_file_is_NCAR_RAF_THEN_no_errors(self):
        from jasmin_cis.test.test_files.data import valid_NCAR_NetCDF_RAF_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_NCAR_NetCDF_RAF_filename)

        assert_that(errors, is_(None), "file should be GASSP")

    def test_WHEN_file_dose_not_exist_THEN_errors(self):
        from jasmin_cis.test.test_files.data import invalid_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(invalid_filename)

        assert_that(errors, is_(["File does not exist"]), "file should not exist")

    def test_WHEN_file_is_not_NCAR_RAF_OR_GASSP_THEN_errors(self):
        from jasmin_cis.test.test_files.data import valid_hadgem_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_hadgem_filename)

        assert_that(len(errors), is_(1), "file should not be GASSP")

    def test_WHEN_file_is_not_netcdf_THEN_errors(self):
        from jasmin_cis.test.test_files.data import valid_aeronet_filename
        product = NCAR_NetCDF_RAF()

        errors = product.get_file_type_error(valid_aeronet_filename)

        assert_that(len(errors), is_(2), "file should not be netcdf")
