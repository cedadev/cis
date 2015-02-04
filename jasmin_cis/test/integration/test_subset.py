from netCDF4 import Dataset

from hamcrest import assert_that, greater_than_or_equal_to, less_than_or_equal_to
import sys
from mock import MagicMock

from jasmin_cis.cis import subset_cmd
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest
from jasmin_cis.time_util import convert_time_since_to_std_time


class TestSubsetIntegration(BaseIntegrationTest):

    def test_GIVEN_single_variable_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_single_variable_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable = valid_hadgem_variable
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable])

    def test_GIVEN_multiple_variables_in_ungridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_multiple_variables_in_gridded_file_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = valid_echamham_variable_1
        variable2 = valid_echamham_variable_2
        filename = valid_echamham_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_multiple_gridded_variables_on_different_grids_WHEN_subset_THEN_subset_correctly(self):
        variable1 = 'v_1'
        variable2 = 'rh'
        filename = valid_1d_filename
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'y=[%s,%s]' % (lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        lat = ds.variables['latitude'][:]
        assert_that(min(lat), greater_than_or_equal_to(lat_min))
        assert_that(max(lat), less_than_or_equal_to(lat_max))
        lat_1 = ds.variables['latitude_1'][:]
        assert_that(min(lat_1), greater_than_or_equal_to(lat_min))
        assert_that(max(lat_1), less_than_or_equal_to(lat_max))
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, [variable1, variable2])

    def test_GIVEN_variables_specified_by_wildcard_WHEN_subset_THEN_subsetted_correctly(self):
        variable1 = 'surface_albedo???'
        variable2 = 'AOD*'
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        arguments = ['subset', variable1 + ',' + variable2 + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, ['AOD550', 'AOD870', 'surface_albedo550',
                                                                              'surface_albedo670', 'surface_albedo870'])


class TestTemporalSubsetAllProductsNamedVariables(BaseIntegrationTest):

    def do_subset(self, filename, time_min, time_max, variable):
        arguments = ['subset', variable + ':' + filename, 't=[%s,%s]' % (time_min, time_max), '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        subset_cmd(main_arguments)

    def check_temporal_subsetting(self, t_min, t_max, gridded):
        import datetime
        if gridded:
            output_path = self.GRIDDED_OUTPUT_FILENAME
        else:
            output_path = self.UNGRIDDED_OUTPUT_FILENAME
        ds = Dataset(output_path)
        cis_standard = datetime.datetime(1600, 1, 1, 0, 0, 0)
        time = ds.variables['time']
        datetime_min = datetime.datetime.strptime(t_min, "%Y-%m-%dT%H:%M:%S")
        datetime_max = datetime.datetime.strptime(t_max, "%Y-%m-%dT%H:%M:%S")
        # Expand the search by a second either way to avoid rounding problems
        datetime_min -= datetime.timedelta(seconds=1.5)
        datetime_max += datetime.timedelta(seconds=1.5)
        time_vals = convert_time_since_to_std_time(time[:], time.units)
        for time_val in time_vals:
            delta = datetime.timedelta(days=time_val)
            datetime_value = cis_standard + delta
            assert_that(datetime_value, greater_than_or_equal_to(datetime_min))
            assert_that(datetime_value, less_than_or_equal_to(datetime_max))

    def test_subset_Cloud_CCI(self):
        # Takes 312 s
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        time_min, time_max = '2008-07', '2008-08'
        # This is a single timestamp so the best we can do is exclude it and confirm no data is returned.
        try:
            sys.stderr = MagicMock()
            self.do_subset(filename, time_min, time_max, variable)
            assert False
        except SystemExit as e:
            assert e.code == 1
            msg = sys.stderr.write.call_args_list[0][0][0].strip()
            assert msg == 'No output created - constraints exclude all data'

    def test_subset_Aerosol_CCI(self):
        # Takes 26s
        variable = 'lat,lon,time,AOD550,AOD870,pixel_number'
        filename = valid_aerosol_cci_filename
        time_min, time_max = '2008-06-12T10:15:00', '2008-06-12T10:35:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_NCAR_RAF(self):
        # Takes 13s
        filename = valid_NCAR_NetCDF_RAF_filename
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        time_min, time_max = '2009-01-14T20:15:00', '2009-01-15T02:45:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_GASSP(self):
        # Takes 13s
        filename = valid_GASSP_aeroplane_filename
        variable = ",".join(valid_GASSP_aeroplane_vars)
        time_min, time_max = '2006-09-27T19:15:00', '2006-09-27T20:45:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_GASSP_not_entirely_valid(self):
        # see issue JASCIS-145
        filename = valid_GASSP_not_entirely_correct_filename
        variable = valid_GASSP_not_entirely_correct_variable
        time_min, time_max = '1993-10-27T00:00:00', '1993-11-27T00:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_Caliop_L1(self):
        # Takes 1470s
        variable = 'Perpendicular_Attenuated_Backscatter_532,Attenuated_Backscatter_1064,' \
                   'Total_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        time_min, time_max = '2009-12-31T23:40:00', '2010-01-01T00:17:17'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_Aeronet(self):
        # Takes 30s
        variable = 'Date(dd-mm-yy),Julian_Day,AOT_1640,AOT_1020,AOT_870,AOT_675,AOT_667,AOT_555,AOT_551,' \
                   'AOT_532,AOT_531,AOT_500,AOT_490,AOT_443,AOT_440,AOT_412,AOT_380,AOT_340,Water(cm),TripletVar_1640,' \
                   'TripletVar_1020,TripletVar_870,TripletVar_675,TripletVar_667,TripletVar_555,TripletVar_551,' \
                   'TripletVar_532,TripletVar_531,TripletVar_500,TripletVar_490,TripletVar_443,TripletVar_440,' \
                   'TripletVar_412,TripletVar_380,TripletVar_340,WaterError,440-870Angstrom,380-500Angstrom,' \
                   '440-675Angstrom,500-870Angstrom,340-440Angstrom,440-675Angstrom(Polar),Last_Processing_Date,' \
                   'Solar_Zenith_Angle'
        filename = valid_aeronet_filename
        time_min, time_max = '2003-09-24T07:00:00', '2003-11-04T07:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_MODIS_L2(self):
        # Takes 16s
        variable = 'Solar_Zenith,Latitude,Sensor_Azimuth,Optical_Depth_Ratio_Small_Land_And_Ocean,Sensor_Zenith,' \
                   'Scan_Start_Time,Image_Optical_Depth_Land_And_Ocean,Cloud_Fraction_Land,' \
                   'Number_Pixels_Used_Ocean,Longitude'
        filename = valid_modis_l2_filename
        time_min, time_max = '2010-01-01T22:55:19', '2010-01-01T22:58:44'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_MODIS_L3(self):
        # Takes 5s
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        time_min, time_max = '2010-01-13T00:00:01', '2010-01-13T00:01:44'
        # This is a single timestamp so the best we can do is exclude it and confirm no data is returned.
        try:
            sys.stderr = MagicMock()
            self.do_subset(filename, time_min, time_max, variable)
            assert False
        except SystemExit as e:
            assert e.code == 1
            msg = sys.stderr.write.call_args_list[0][0][0].strip()
            assert msg == 'No output created - constraints exclude all data'

    def test_subset_CloudSatPRECIP(self):
        # Takes 17s
        variable = 'Profile_time,Latitude,Longitude,DEM_elevation,Data_quality'
        filename = valid_cloudsat_PRECIP_file
        time_min, time_max = '2008-02-14T00:57:36', '2008-02-14T02:09:36'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_Caliop_L2(self):
        # Takes 56s
        variable = 'Perpendicular_Backscatter_Coefficient_532,' \
                   'Perpendicular_Backscatter_Coefficient_Uncertainty_532,Pressure'
        filename = valid_caliop_l2_filename
        time_min, time_max = '2009-12-31T23:42:43', '2010-01-01T00:17:17'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_CloudSatRVOD(self):

        variable = "RVOD_liq_water_content,RVOD_ice_water_path"
        filename = valid_cloudsat_RVOD_file
        time_min, time_max = '2007-06-29T13:12:00', '2007-06-29T14:29:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_cis_gridded(self):
        # Takes 1s
        variable = 'TAU_2D_550nm'
        filename = valid_cis_gridded_output_filename
        time_min, time_max = '2007-06-04T10:18:37', '2007-06-28T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_cis_ungridded(self):
        # Takes 1s
        variable = 'AOD550,AOD870,latitude,time'
        filename = valid_cis_ungridded_output_filename
        time_min, time_max = '2008-06-12T10:18:37', '2008-06-12T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        time_min, time_max = '2007-06-02T10:18:37', '2007-06-12T10:19:47'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, True)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_subset_ASCII(self):
        variable = 'value'
        filename = valid_ascii_filename
        time_min, time_max = '2012-08-23T15:32:03', '2012-08-28T00:00:00'
        self.do_subset(filename, time_min, time_max, variable)
        self.check_temporal_subsetting(time_min, time_max, False)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(','))


class TestSpatialSubsetAllProductsAllValidVariables(BaseIntegrationTest):

    def do_subset(self, filename, lat_max, lat_min, lon_max, lon_min, variable):
        arguments = ['subset', variable + ':' + filename,
                     'x=[%s,%s],y=[%s,%s]' % (lon_min, lon_max, lat_min, lat_max), '-o', self.OUTPUT_NAME]
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
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_Aerosol_CCI(self):
        # Takes 135s
        variable = '*'
        filename = valid_aerosol_cci_filename
        lon_min, lon_max = -15, 5
        lat_min, lat_max = -30, 45
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_NCAR_RAF(self):
        # Takes 170s
        variable = '*'
        filename = valid_NCAR_NetCDF_RAF_filename
        lon_min, lon_max = -160, -157
        lat_min, lat_max = 30, 50
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_Caliop_L1(self):
        # Takes 473s
        variable = '*'
        filename = valid_caliop_l1_filename
        lon_min, lon_max = 0, 60
        lat_min, lat_max = -30, 30
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_Aeronet(self):
        # Takes 60s
        variable = '*'
        filename = valid_aeronet_filename
        lon_min, lon_max = -1.5, 1.4
        lat_min, lat_max = 15, 15.5
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_MODIS_L2(self):
        # Takes 35s
        variable = '*'
        filename = valid_modis_l2_filename
        lon_min, lon_max = -150, 150
        lat_min, lat_max = -72, -63
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_MODIS_L3(self):
        # (All variables takes 23 mins)
        variable = '*'  # Would like to run this but it takes up a lot of memory on Jenkins.
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)

    def test_subset_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = '*'
        filename = valid_hadgem_filename
        lon_min, lon_max = 0, 120
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_Caliop_L2(self):
        # Takes 40s
        variable = '*'
        filename = valid_caliop_l2_filename
        lon_min, lon_max = 0, 60
        lat_min, lat_max = -30, 30
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_CloudSatPRECIP(self):
        #Takes 100s
        variable = '*'
        filename = valid_cloudsat_PRECIP_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_cis_gridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_gridded_output_filename
        lon_min, lon_max = 0, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, True)

    def test_subset_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max = 1, 3
        lat_min, lat_max = 41, 42
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_CloudSatRVOD(self):
        #257s exit code 137
        variable = '*'  # Gets killed by Jenkins
        variable = "RVOD_liq_water_content,RVOD_ice_water_path"
        filename = valid_cloudsat_RVOD_file
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 40, 60
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_GASP(self):
        #257s exit code 137
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        lon_min, lon_max = -94, 95
        lat_min, lat_max = 30, 31
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)

    def test_subset_ASCII(self):
        variable = '*'
        filename = valid_ascii_filename
        lon_min, lon_max = -10, 10
        lat_min, lat_max = 1, 6
        self.do_subset(filename, lat_max, lat_min, lon_max, lon_min, variable)
        self.check_latlon_subsetting(lat_max, lat_min, lon_max, lon_min, False)
