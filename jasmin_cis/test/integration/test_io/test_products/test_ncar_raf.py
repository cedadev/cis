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