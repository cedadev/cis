from netCDF4 import Dataset

from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to
from nose.tools import raises
import unittest

from cis.cis_main import subset_cmd
from cis.parse import parse_args
from cis.test.integration_test_data import *
from cis.test.integration.base_integration_test import BaseIntegrationTest
from cis.time_util import convert_time_since_to_std_time
from cis.exceptions import CoordinateNotFoundError, NoDataInSubsetError


class TestSubsetIntegration(BaseIntegrationTest):
    def test_GIVEN_single_variable_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable])

    def test_GIVEN_shape_WHEN_subset_ungridded_data_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        shape_wkt = "POLYGON((-10 50, 0 60, 10 50, 0 40, -10 50))"
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'shape=%s' % shape_wkt, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_as_var_name_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'lon=[%s,%s],lat=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_hadgem_variable
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, 'lat', 'lon')
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_as_var_name_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_hadgem_variable
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'longitude=[%s,%s],latitude=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, 'lat', 'lon')
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable])

    def test_GIVEN_multiple_variables_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_multiple_variables_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_echamham_variable_1
        variable2 = valid_echamham_variable_2
        filename = valid_echamham_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, 'lat', 'lon')
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_variables_specified_by_wildcard_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = 'surface_albedo???'
        variable2 = 'AOD*'
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['AOD550', 'AOD870', 'surface_albedo550',
                                                                              'surface_albedo670', 'surface_albedo870'])


class TestTemporalSubsetAllProductsNamedVariables(BaseIntegrationTest):
    def do_subset(self, filename, time_min, time_max, variable):
        arguments = ['subset', variable + ':' + escape_colons(filename), 't=[%s,%s]' % (time_min, time_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def check_temporal_subsetting(self, t_min, t_max):
        import datetime
        from cf_units import Unit
        self.ds = Dataset(self.OUTPUT_FILENAME)
        cis_standard = datetime.datetime(1600, 1, 1, 0, 0, 0)
        time = self.ds.variables['time']
        datetime_min = datetime.datetime.strptime(t_min, "%Y-%m-%dT%H:%M:%S")
        datetime_max = datetime.datetime.strptime(t_max, "%Y-%m-%dT%H:%M:%S")
        # Expand the search by a second either way to avoid rounding problems
        datetime_min -= datetime.timedelta(seconds=1.5)
        datetime_max += datetime.timedelta(seconds=1.5)
        time_vals = convert_time_since_to_std_time(time[:], Unit(time.units))
        for time_val in time_vals:
            delta = datetime.timedelta(days=time_val)
            datetime_value = cis_standard + delta
            assert_that(datetime_value, greater_than_or_equal_to(datetime_min))
            assert_that(datetime_value, less_than_or_equal_to(datetime_max))

    @raises(NoDataInSubsetError)
    def test_subset_Cloud_CCI(self):
        # Takes 4s
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        time_min, time_max = '2008-07', '2008-08'
        # This is a single timestamp so the best we can do is exclude it and confirm no data is returned.
        self.do_subset(filename, time_min, time_max, variable)

    def test_subset_Aerosol_CCI(self):
        # Takes 2s
        variable = 'lat,lon,time,AOD550,AOD870,pixel_number'
        filename = valid_aerosol_cci_filename
        time_min, time_max = '2008-06-12T10:15:00', '2008-06-12T10:35:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_NCAR_RAF(self):
        # Takes 4s
        filename = valid_NCAR_NetCDF_RAF_filename
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        time_min, time_max = '2009-01-14T20:15:00', '2009-01-15T02:45:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_NCAR_RAF_with_named_time_variable(self):
        # Takes 4s
        filename = valid_NCAR_NetCDF_RAF_filename
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        time_min, time_max = '2009-01-14T20:15:00', '2009-01-15T02:45:00'
        arguments = ['subset', variable + ':' + escape_colons(filename), 'time=[%s,%s]' % (time_min, time_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_GASSP(self):
        # Takes 1.3s
        filename = valid_GASSP_aeroplane_filename
        variable = ",".join(valid_GASSP_aeroplane_vars)
        time_min, time_max = '2006-09-27T19:15:00', '2006-09-27T20:45:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_GASSP_aux_coord(self):
        # Takes 1.3s
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        variable = ",".join(cis_test_files['GASSP_aux_coord'].all_variable_names)
        time_min, time_max = '1995-11-08T17:00:00', '1995-11-08T20:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_GASSP_not_entirely_valid(self):
        # see issue JASCIS-145
        filename = valid_GASSP_not_entirely_correct_filename
        variable = valid_GASSP_not_entirely_correct_variable
        time_min, time_max = '1993-10-27T00:00:00', '1993-11-27T00:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_Caliop_L1(self):
        # Takes 1470s
        variable = 'Perpendicular_Attenuated_Backscatter_532,Attenuated_Backscatter_1064,' \
                   'Total_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        time_min, time_max = '2009-12-31T23:40:00', '2010-01-01T00:17:17'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_Aeronet(self):
        # Takes 30s
        variable = ','.join(all_aeronet_variables[0:5])
        filename = valid_aeronet_filename
        time_min, time_max = '2003-09-24T07:00:00', '2003-11-04T07:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_MODIS_L2(self):
        # Takes 16s
        variable = 'Solar_Zenith,Latitude,Sensor_Azimuth,Optical_Depth_Ratio_Small_Land_And_Ocean,Sensor_Zenith,' \
                   'Scan_Start_Time,Image_Optical_Depth_Land_And_Ocean,Cloud_Fraction_Land,' \
                   'Number_Pixels_Used_Ocean,Longitude'
        filename = valid_modis_l2_filename
        time_min, time_max = '2010-01-01T22:55:19', '2010-01-01T22:58:44'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @raises(CoordinateNotFoundError)
    def test_subset_MODIS_L3(self):
        # Takes 5s
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        time_min, time_max = '2010-01-13T00:00:01', '2010-01-13T00:01:44'
        # This is a single scalar timestamp so trying to subset on time will result in CoordinateNotFound (as we only
        # look for extended coordinates). We may want to revisit this if there is some good reason for subsetting scalar
        # coordinates...
        self.do_subset(filename, time_min, time_max, variable)

    @skip_pyhdf
    def test_subset_CloudSatPRECIP(self):
        # Takes 17s
        variable = 'Profile_time,Latitude,Longitude,DEM_elevation,Data_quality'
        filename = valid_cloudsat_PRECIP_file
        time_min, time_max = '2008-02-14T00:57:36', '2008-02-14T02:09:36'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_subset_Caliop_L2(self):
        # Takes 25s
        variable = 'Perpendicular_Backscatter_Coefficient_532,' \
                   'Perpendicular_Backscatter_Coefficient_Uncertainty_532,Pressure'
        filename = valid_caliop_l2_filename
        time_min, time_max = '2009-12-31T23:42:43', '2010-01-01T00:17:17'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_subset_CloudSatRVOD(self):

        variable = "RVOD_liq_water_content,RVOD_ice_water_path"
        filename = valid_cloudsat_RVOD_file
        time_min, time_max = '2007-06-29T13:12:00', '2007-06-29T14:29:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_cis_gridded(self):
        # Takes 1s
        variable = 'TAU_2D_550nm'
        filename = valid_cis_gridded_output_filename
        time_min, time_max = '2007-06-04T10:18:37', '2007-06-28T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_cis_ungridded(self):
        # Takes 1s
        variable = 'AOD550,AOD870,latitude,time'
        filename = valid_cis_ungridded_output_filename
        time_min, time_max = '2008-06-12T10:18:37', '2008-06-12T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        time_min, time_max = '2007-06-02T10:18:37', '2007-06-12T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_subset_ASCII(self):
        variable = 'value'
        filename = valid_ascii_filename
        time_min, time_max = '2012-08-23T15:32:03', '2012-08-28T00:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))


class TestSpatialSubsetAllProductsAllValidVariables(BaseIntegrationTest):
    def do_subset(self, filename, lat_max, lat_min, lon_max, lon_min, variable):
        arguments = ['subset', variable + ':' + escape_colons(filename),
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def test_subset_Cloud_CCI(self):
        # (All variables takes 30 mins)
        variable = '*'  # Would like to run this but it takes up a lot of memory on Jenkins.
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        lon_min, lon_max = 84, 99
        lat_min, lat_max = -6, 6
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_Aerosol_CCI(self):
        # Takes 97s
        variable = '*'
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -15, 5
        lat_min, lat_max = -30, 45
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_NCAR_RAF(self):
        # Takes 170s
        variable = 'ATX,PITCH'
        filename = valid_NCAR_NetCDF_RAF_filename
        lon_min, lon_max = -160, -157
        lat_min, lat_max = 30, 50
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    @skip_pyhdf
    def test_subset_Caliop_L1(self):
        # Takes 473s
        variable = '*'
        filename = valid_caliop_l1_filename
        lon_min, lon_max = 0, 60
        lat_min, lat_max = -30, 30
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_Aeronet(self):
        # Takes 60s
        variable = 'AOT_*'
        filename = valid_aeronet_filename
        lon_min, lon_max = -1.5, 1.4
        lat_min, lat_max = 15, 15.5
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    @skip_pyhdf
    def test_subset_MODIS_L2(self):
        # Takes 35s
        variable = '*'
        filename = valid_modis_l2_filename
        lon_min, lon_max = -150, 150
        lat_min, lat_max = -72, -63
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    @skip_pyhdf
    def test_subset_MODIS_L3(self):
        variable = '*'
        filename = valid_modis_l3_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = '*'
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 120
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, 'lat', 'lon')

    @skip_pyhdf
    def test_subset_Caliop_L2(self):
        # Takes 40s
        variable = '*'
        filename = valid_caliop_l2_filename
        lon_min, lon_max = 0, 60
        lat_min, lat_max = -30, 30
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    @skip_pyhdf
    def test_subset_CloudSatPRECIP(self):
        # Takes 100s
        variable = '*'
        filename = valid_cloudsat_PRECIP_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_cis_gridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_gridded_output_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, 'lat', 'lon')

    def test_subset_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max = 1, 3
        lat_min, lat_max = 41, 42
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    @skip_pyhdf
    def test_subset_CloudSatRVOD(self):
        # 257s exit code 137
        variable = '*'  # Gets killed by Jenkins
        variable = "RVOD_liq_water_path,RVOD_ice_water_path"
        filename = valid_cloudsat_RVOD_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_GASP(self):
        # 257s exit code 137
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        lon_min, lon_max = -94, 95
        lat_min, lat_max = 30, 31
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_GASSP_aux_coord(self):
        # Takes 1.3s
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        variable = ",".join(cis_test_files['GASSP_aux_coord'].all_variable_names)
        lon_min, lon_max = -156, -155
        lat_min, lat_max = 5, 10
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)

    def test_subset_ASCII(self):
        variable = '*'
        filename = valid_ascii_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 1, 6
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min)


class TestEmptySubsets(BaseIntegrationTest):

    def do_subset(self, filename, variable, alt_bounds='', pres_bounds=''):
        # Join the bounds with a comma if they are both specified
        joint_bounds = ','.join([alt_bounds, pres_bounds]) if alt_bounds and pres_bounds else alt_bounds or pres_bounds
        arguments = ['subset', variable + ':' + escape_colons(filename), joint_bounds, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    @raises(NoDataInSubsetError)
    def test_empty_subset_ungridded_vertical(self):
        # Takes 170s
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        alt_min, alt_max = 15000, 20000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    #More...


class TestVerticalSubsetAllProducts(BaseIntegrationTest):
    def do_subset(self, filename, variable, alt_bounds='', pres_bounds=''):
        # Join the bounds with a comma if they are both specified
        joint_bounds = ','.join([alt_bounds, pres_bounds]) if alt_bounds and pres_bounds else alt_bounds or pres_bounds
        arguments = ['subset', variable + ':' + escape_colons(filename), joint_bounds, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def test_subset_NCAR_RAF_alt(self):
        # Takes 170s
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        alt_min, alt_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    def test_subset_NCAR_RAF_pres(self):
        # Takes 170s
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        pres_min, pres_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='p=[{},{}]'.format(pres_min, pres_max))
        self.check_pres_subsetting(pres_max, pres_min)

    def test_subset_NCAR_RAF_pres_order_doesnt_matter(self):
        # Takes 170s
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        pres_min, pres_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='p=[{},{}]'.format(pres_max, pres_min))
        self.check_pres_subsetting(pres_max, pres_min)

    @skip_pyhdf
    def test_subset_Caliop_L1(self):
        # Takes 473s
        variable = ','.join(valid_caliop_l1_variables)
        filename = valid_caliop_l1_filename
        alt_min, alt_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    def test_subset_hybrid_pressure_model_field(self):
        """
        In the case of subsetting hybrid height/pressure fields using the axis name CIS (iris) will choose the vertical
        *dimension* coordinate, whether that is model level number, hybrid sigma, or something else
        """
        # Takes 1s
        variable = valid_hybrid_pressure_variable
        filename = valid_hybrid_pressure_filename
        pres_min, pres_max = 0.95, 0.96
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(pres_min, pres_max))
        self.check_pres_subsetting(pres_max, pres_min, pres_name='lev')

    @raises(CoordinateNotFoundError)
    def test_subset_hybrid_pressure_model_field_by_variable(self):
        """
        In the case of hybrid height/pressure fields specifying the hybrid variable directly will result in a coordinate
          not found error
        """
        # Takes 1s
        variable = valid_hybrid_pressure_variable
        filename = valid_hybrid_pressure_filename
        pres_min, pres_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='air_pressure=[{},{}]'.format(pres_min, pres_max))
        self.check_pres_subsetting(pres_max, pres_min)

    @skip_pyhdf
    def test_subset_Caliop_L2(self):
        # Takes 40s
        variable = ','.join(valid_caliop_l2_variables)
        filename = valid_caliop_l2_filename
        alt_min, alt_max = 1000, 2000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    @skip_pyhdf
    def test_subset_CloudSatRVOD_alt(self):
        # 257s exit code 137
        variable = "RVOD_liq_water_content,RVOD_ice_water_path"
        filename = valid_cloudsat_RVOD_file
        alt_min, alt_max = 0, 2000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    def test_subset_GASSP(self):
        # 257s exit code 137
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        alt_min, alt_max = 0, 2000
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)

    @raises(CoordinateNotFoundError)
    def test_subset_GASSP_pres(self):
        # 257s exit code 137
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        pres_min, pres_max = 2000, 200
        self.do_subset(filename, variable, alt_bounds='p=[{},{}]'.format(pres_min, pres_max))

    def test_subset_ASCII(self):
        variable = '*'
        filename = valid_ascii_filename
        alt_min, alt_max = 0, 12
        self.do_subset(filename, variable, alt_bounds='z=[{},{}]'.format(alt_min, alt_max))
        self.check_alt_subsetting(alt_max, alt_min)


class TestAuxSubset(BaseIntegrationTest):

    def check_aux_subsetting(self, aux_min, aux_max, var):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        alt = self.ds.variables[var][:]
        assert_that(alt.min(), greater_than_or_equal_to(aux_min))
        assert_that(alt.max(), less_than_or_equal_to(aux_max))
        self.ds.close()

    def do_subset(self, filename, variable, aux_bounds):
        # Join the bounds with a comma if they are both specified
        arguments = ['subset', variable + ':' + escape_colons(filename), aux_bounds, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def test_subset_GASSP_aux_coord(self):
        # Takes 1.3s
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        variable = cis_test_files['GASSP_aux_coord'].data_variable_name
        dp_min, dp_max = 0.05, 0.8
        self.do_subset(filename, variable, 'DP_MID=[{min},{max}]'.format(min=dp_min, max=dp_max))
        self.check_aux_subsetting(dp_min, dp_max, 'DP_MID')
