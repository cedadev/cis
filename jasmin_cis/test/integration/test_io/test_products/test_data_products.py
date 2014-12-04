'''
module to test the various subclasses of the abstract AProduct class
'''
import unittest
from nose.tools import istest, eq_, raises, nottest
from iris.exceptions import TranslationError

from jasmin_cis.data_io.products.products import *
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.test.test_files.data import non_netcdf_file


def check_regex_matching(cls_name, filename):
    from jasmin_cis.data_io.products.AProduct import __get_class
    cls = __get_class(filename)
    eq_(cls.__name__, cls_name)

invalid_variable = "im_an_invalid_variable"
invalid_filename = "im_an_invalid_file"
invalid_format = non_netcdf_file


class ProductTests(object):
    product = None
    filename = None
    vars = None
    valid_variable = None

    @istest
    def test_file_regex_matching(self):
        check_regex_matching(self.product.__name__, self.filename)

    @istest
    def test_file_regex_matching_for_full_path(self):
        check_regex_matching(self.product.__name__, "/home/duncan/" + self.filename)
        check_regex_matching(self.product.__name__, "/a/xenida/more/lev20/confusing/hdf/path/nc/" + self.filename)

    @istest
    def test_variable_wildcarding(self):
        vars = self.product().get_variable_names([self.filename])
        self.check_valid_vars(vars)

    def check_valid_vars(self, vars):
        assert set(vars) == set(self.vars)

    @istest
    def test_create_data_object(self):
        self.product().create_data_object([self.filename], self.valid_variable)

    @istest
    def test_create_coords(self):
        valid_standard_names = ['latitude', 'longitude', 'altitude', 'time', 'air_pressure']
        coords = self.product().create_coords([self.filename], self.valid_variable)
        coord_list = coords.coords()

        for coord in coord_list:
            logging.debug(coord.standard_name)

        for coord in coord_list:
            print coord.standard_name

        assert (all([coord.standard_name in valid_standard_names for coord in coord_list]))

    @istest
    def test_write_coords(self):
        from jasmin_cis.data_io.write_netcdf import write_coordinates
        from os import remove

        test_file = '/tmp/test_out.nc'
        coords = self.product().create_coords([self.filename], self.valid_variable)
        write_coordinates(coords, test_file)
        remove(test_file)

    @istest
    @raises(IOError)
    def should_raise_ioerror_with_invalid_filename(self):
        self.product().create_data_object([invalid_filename], self.valid_variable)

    @istest
    @raises(IOError, TranslationError)
    def should_raise_ioerror_or_translationerror_with_file_that_is_not_a_recognised_format(self):
        self.product().create_data_object([invalid_format], self.valid_variable)

    @istest
    @raises(InvalidVariableError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        self.product().create_data_object([self.filename], invalid_variable)


class TestCloudsatRVODsdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_sdata_variable

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_sdata_variable
        self.product = CloudSat

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


class TestCloudsatRVODvdata(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_RVOD_file, valid_cloudsat_RVOD_vdata_variable

        self.filename = valid_cloudsat_RVOD_file
        self.valid_variable = valid_cloudsat_RVOD_vdata_variable
        self.product = CloudSat

    def check_valid_vars(self, vars):
        assert len(vars) == 47 + 22  # Expect 47 valid SD vars and 22 valid VD vars


class TestCloudsatPRECIP(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloudsat_PRECIP_file, valid_cloudsat_PRECIP_variable

        self.filename = valid_cloudsat_PRECIP_file
        self.valid_variable = valid_cloudsat_PRECIP_variable
        self.product = CloudSat
        self.vars = ['Profile_time',
                     'Latitude',
                     'Longitude',
                     'DEM_elevation',
                     'Data_quality',
                     'Data_status',
                     'Data_targetID',
                     'Precip_rate',
                     'Precip_rate_min',
                     'Precip_rate_max',
                     'Precip_rate_no_ms',
                     'PIA_hydrometeor',
                     'PIA_near_surface',
                     'Sigma_zero',
                     'Near_surface_reflectivity',
                     'Cloud_top_lowest_layer',
                     'Cloud_top_highest_layer',
                     'Frozen_precip_height',
                     'Melted_fraction',
                     'Status_flag',
                     'Precip_flag',
                     'Retrieval_info_flag',
                     'Phase_flag',
                     'Cloud_flag',
                     'SRT_flag',
                     'Surface_type',
                     'Freezing_level',
                     'SST',
                     'Surface_wind',
                     'Aux_CWV_AMSR',
                     'Aux_LWP_AMSR',
                     'Aux_SST_AMSR',
                     'Aux_precip_AMSR',
                     'Aux_dist_AMSR']


class TestMODIS_L3(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_modis_l3_filename, valid_modis_l3_variable

        self.filename = valid_modis_l3_filename
        self.valid_variable = valid_modis_l3_variable
        self.product = MODIS_L3

    def check_valid_vars(self, vars):
        assert len(vars) == 700


class TestCaliop_L2(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_caliop_l2_filename, valid_caliop_l2_variable

        self.filename = valid_caliop_l2_filename
        self.valid_variable = valid_caliop_l2_variable
        self.product = Caliop_L2
        self.vars = ['Aerosol_Layer_Fraction',
                     'Aerosol_Multiple_Scattering_Profile_1064',
                     'Aerosol_Multiple_Scattering_Profile_532',
                     'Backscatter_Coefficient_1064',
                     'Backscatter_Coefficient_Uncertainty_1064',
                     'Cloud_Layer_Fraction',
                     'Extinction_Coefficient_1064',
                     'Extinction_Coefficient_532',
                     'Extinction_Coefficient_Uncertainty_1064',
                     'Extinction_Coefficient_Uncertainty_532',
                     'Molecular_Number_Density',
                     'Particulate_Depolarization_Ratio_Profile_532',
                     'Particulate_Depolarization_Ratio_Uncertainty_532',
                     'Perpendicular_Backscatter_Coefficient_532',
                     'Perpendicular_Backscatter_Coefficient_Uncertainty_532',
                     'Pressure',
                     'Relative_Humidity',
                     'Samples_Averaged',
                     'Temperature',
                     'Total_Backscatter_Coefficient_Uncertainty_532',
                     'Total_Backscatter_Coefficient_532']


class TestCaliop_L1(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_caliop_l1_filename, valid_caliop_l1_variable

        self.filename = valid_caliop_l1_filename
        self.valid_variable = valid_caliop_l1_variable
        self.product = Caliop_L1
        self.vars = ['Perpendicular_Attenuated_Backscatter_532',
                     'Attenuated_Backscatter_1064',
                     'Total_Attenuated_Backscatter_532']


class TestMODIS_L2(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_modis_l2_filename, valid_modis_l2_variable

        self.filename = valid_modis_l2_filename
        self.valid_variable = valid_modis_l2_variable
        self.product = MODIS_L2
        self.vars = ['Deep_Blue_Angstrom_Exponent_Land',
                     'Cloud_Fraction_Ocean',
                     'Corrected_Optical_Depth_Land_wav2p1',
                     'Mass_Concentration_Land',
                     'Solar_Zenith',
                     'Latitude',
                     'Sensor_Azimuth',
                     'Optical_Depth_Ratio_Small_Land_And_Ocean',
                     'Sensor_Zenith',
                     'Scan_Start_Time',
                     'Image_Optical_Depth_Land_And_Ocean',
                     'Cloud_Fraction_Land',
                     'Number_Pixels_Used_Ocean',
                     'Longitude',
                     'Aerosol_Type_Land',
                     'Cloud_Mask_QA',
                     'Optical_Depth_Ratio_Small_Land',
                     'Scattering_Angle',
                     'Solar_Azimuth',
                     'Angstrom_Exponent_Land',
                     'Deep_Blue_Aerosol_Optical_Depth_550_Land',
                     'Fitting_Error_Land',
                     'Optical_Depth_Land_And_Ocean']


class TestCloud_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cloud_cci_filename, valid_cloud_cci_variable

        self.filename = valid_cloud_cci_filename
        self.valid_variable = valid_cloud_cci_variable
        self.product = Cloud_CCI

    def check_valid_vars(self, vars):
        assert len(vars) == 30


class TestAerosol_CCI(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_aerosol_cci_filename, valid_aerosol_cci_variable

        self.filename = valid_aerosol_cci_filename
        self.valid_variable = valid_aerosol_cci_variable
        self.product = Aerosol_CCI
        self.vars = []

    def check_valid_vars(self, vars):
        exclude_vars = ["sun_zenith", "satellite_zenith", "relative_azimuth", "instrument_view"]
        assert len(vars) == 32
        for key in exclude_vars:
            assert key not in vars


class TestCis(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_cis_col_file

        self.filename = valid_cis_col_file
        self.valid_variable = 'AOT_440'
        self.product = cis
        self.vars = ['pixel_number', 'latitude', 'longitude', 'altitude', 'time', 'AOT_440']


class TestNCAR_NetCDF_RAF(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_NCAR_NetCDF_RAF_filename, valid_NCAR_NetCDF_RAF_variable

        self.filename = valid_NCAR_NetCDF_RAF_filename
        self.valid_variable = valid_NCAR_NetCDF_RAF_variable
        self.product = NCAR_NetCDF_RAF

    def check_valid_vars(self, vars):
        exclude_vars = ["ACDP_LWI", "AUHSAS_RWI", "CCDP_LWI",
                        "CUHSAS_RWI"]  # , "LATC", "LONC", "GGALTC", "Time", "PSXC"]
        assert len(vars) == 117
        for key in exclude_vars:
            assert key not in vars


class TestAeronet(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_aeronet_filename, valid_aeronet_variable, \
            another_valid_aeronet_filename

        self.filename = valid_aeronet_filename
        self.filenames = [valid_aeronet_filename, another_valid_aeronet_filename]
        self.valid_variable = valid_aeronet_variable
        self.product = Aeronet

    def check_valid_vars(self, vars):
        assert len(vars) == 45

    @istest
    def test_create_data_object_from_multiple_files(self):
        self.product().create_data_object(self.filenames, self.valid_variable)


class TestASCII(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_ascii_filename, valid_ascii_variable, \
            ascii_filename_with_no_values

        self.filename = valid_ascii_filename
        self.no_value_filename = ascii_filename_with_no_values
        self.valid_variable = valid_ascii_variable
        self.product = ASCII_Hyperpoints
        self.vars = ['latitude', 'longitude', 'altitude', 'time', 'value']

    @istest
    @raises(IOError)
    def should_raise_error_when_variable_does_not_exist_in_file(self):
        '''
         This product throws an IO error rather than an InvalidVariable error as the file can only have one variable
        :return:
        '''
        self.product().create_data_object([self.no_value_filename], True)

    @istest
    def test_create_data_object_with_missing_values(self):
        '''
         Check that missing values get masked correctly
        :return:
        '''
        data = self.product().create_data_object([self.filename], True)
        assert (all(data.data.mask == [False, False, False, True, False, True, False, False]))

    @istest
    def test_create_data_object_with_valid_datetime(self):
        import datetime
        from jasmin_cis.time_util import convert_datetime_to_std_time

        data = self.product().create_data_object([self.filename], True)
        assert (data.coord('time').data[3] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 25, 15, 32, 03)))
        assert (data.coord('time').data[4] == convert_datetime_to_std_time(datetime.datetime(2012, 8, 26)))


class TestNetCDF_Gridded_xenida(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_xenida_filename, valid_xenida_variable

        self.filename = valid_xenida_filename
        self.valid_variable = valid_xenida_variable
        self.product = default_NetCDF
        self.vars = [u'latitude_bounds',
                     u'longitude_bounds',
                     u'atmosphere_hybrid_height_coordinate_ak_bounds',
                     u'atmosphere_hybrid_height_coordinate_ak',
                     u'atmosphere_hybrid_height_coordinate_bk_bounds',
                     u'atmosphere_hybrid_height_coordinate_bk',
                     u'forecast_reference_time',
                     u'PP_1_265',
                     u'PP_1_266',
                     u'time_1_bounds',
                     u'atmosphere_hybrid_height_coordinate_ak_1_bounds',
                     u'atmosphere_hybrid_height_coordinate_ak_1',
                     u'atmosphere_hybrid_height_coordinate_bk_1_bounds',
                     u'atmosphere_hybrid_height_coordinate_bk_1',
                     u'PP_1_30035',
                     u'PP_1_4240',
                     u'PP_1_4241',
                     u'PP_1_5213',
                     u'mass_fraction_of_cloud_ice_in_air',
                     u'mass_fraction_of_cloud_liquid_water_in_air',
                     u'specific_humidity',
                     u'tendency_of_mass_fraction_of_cloud_ice_in_air',
                     u'tendency_of_mass_fraction_of_cloud_liquid_water_in_air',
                     u'tendency_of_specific_humidity']

    # TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass


class TestNetCDF_Gridded_xglnwa(ProductTests, unittest.TestCase):
    def setUp(self):
        from jasmin_cis.test.test_files.data import valid_1d_filename, valid_1d_variable

        self.filename = valid_1d_filename
        self.valid_variable = valid_1d_variable
        self.product = default_NetCDF

    def check_valid_vars(self, vars):
        coord_vars = [u't',
                      u'Trop',
                      u'latitude',
                      u'surface',
                      u'unspecified_1',
                      u'hybrid_ht_1',
                      u'hybrid_ht',
                      u'level6',
                      u'latitude_1',
                      u'ht',
                      u'msl',
                      u'pseudo_1',
                      u'hybrid_ht_2',
                      u'blht_1',
                      u'hybrid_ht_3',
                      u'toa',
                      u'pseudo',
                      u'hybrid_ht_4',
                      u'level275',
                      u'level1534',
                      u'theta_1']
        assert len(vars) == 466
        for key in coord_vars:
            assert key not in vars

    # TODO Create a new implementation of bypassed tests
    @nottest
    def test_write_coords(self):
        # This won't work for model data yet as the coordinates aren't all the same shape, they need to be 'expanded'
        pass

    @nottest
    def test_create_coords(self):
        # This won't work for model data yet as the coordinates can have names other than the expected ones
        pass
