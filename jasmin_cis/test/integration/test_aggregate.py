from netCDF4 import Dataset
import datetime as dt
from hamcrest import assert_that
import numpy as np

import unittest

from jasmin_cis.cis import aggregate_cmd
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest
from jasmin_cis.test.test_files.data import *
from jasmin_cis.test.utils_for_testing import *
from jasmin_cis.parse import parse_args


class BaseAggregationTest(BaseIntegrationTest):

    def check_grid_aggregation(self, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta,
                               lat_name='lat', lon_name='lon'):
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        expected_lat_bnds = np.array([[y, y + lat_delta] for y in np.arange(lat_start, lat_end, lat_delta)])
        expected_lon_bnds = np.array([[x, x + lon_delta] for x in np.arange(lon_start, lon_end, lon_delta)])
        lat_bnds = ds.variables[lat_name + '_bnds']
        lon_bnds = ds.variables[lon_name + '_bnds']
        try:
            assert_that(np.allclose(lat_bnds[:], expected_lat_bnds))
        except AssertionError:
            # For some reason we occasionally need to reverse the order...
            expected_lat_bnds = np.array(([[y + lat_delta, y] for y in np.arange(lat_start, lat_end, lat_delta)]))[::-1]
            assert_that(np.allclose(lat_bnds[:], expected_lat_bnds))
        try:
            assert_that(np.allclose(lon_bnds[:], expected_lon_bnds))
        except AssertionError:
            expected_lon_bnds = np.array([[x + lon_delta, x] for x in np.arange(lon_start, lon_end, lon_delta)])[::-1]
            assert_that(np.allclose(lon_bnds[:], expected_lon_bnds))

    def check_temporal_aggregation(self, time_start, time_end, time_delta, time_name='time'):
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        # Convert from time to days after..

        def convert_to_days_since_cis_epoch(date_time):
            cis_standard = dt.datetime(1600, 1, 1, 0, 0, 0)
            return (date_time - cis_standard).total_seconds() / dt.timedelta(days=1).total_seconds()

        time_start = convert_to_days_since_cis_epoch(time_start)
        time_end = convert_to_days_since_cis_epoch(time_end)
        time_delta = time_delta.total_seconds() / dt.timedelta(days=1).total_seconds()

        expected_time_bnds = np.array([[t, t + time_delta] for t in np.arange(time_start, time_end, time_delta)
                                       if t + time_delta <= time_end * (1 + 1e-13)])
        time_bnds = ds.variables[time_name + '_bnds']
        assert_that(np.allclose(time_bnds[:], expected_time_bnds))

    def do_spatial_aggregate(self, variable, filename, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta):
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_start, lon_end, lon_delta, lat_start, lat_end, lat_delta)
        arguments = ['aggregate', variable + ':' + filename + ':kernel=mean', grid, '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)

    def do_temporal_aggregate(self, variable, filename, t_start, t_end, str_delta):
        grid = 't=[%s,%s,%s]' % (t_start.isoformat(), t_end.isoformat(), str_delta)
        arguments = ['aggregate', variable + ':' + filename + ':kernel=mean', grid, '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)


class TestAggregation(BaseAggregationTest):
    """
    This class provides integration testing for the Aggregation command, ensuring that for one specific product
    (Aerosol CCI), the aggregation is correct and the results are what we expect.
    """

    def test_aggregation_over_latlon(self):
        # Takes 20s
        variable = 'AOD550,AOD870'
        filename = valid_aerosol_cci_filename
        lat_start, lat_end, lat_delta = -40, 80, 10
        lon_start, lon_end, lon_delta = -20, 140, 10
        self.do_spatial_aggregate(variable, filename, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta)
        self.check_grid_aggregation(lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

        # Test some specific values: these are previous outputs from this aggregate command which have been compared
        # against the original data and found to 'look about right' and therefore used as a baseline. If these values
        # change we should consider being concerned.
        i = float('inf')
        arr_550 = np.array([[0.1096153093624289, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.03419682030959262, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.06063271913586593, 0.08715646206228822, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.09970282124016773, 0.1629985723514454, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.19553465147813162, 0.40563457332879743, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.7052307901349156, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.5859629385860146, 0.4436802918665714, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.29588747474573723, 0.2914036842614198, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.13670555069561927, 0.1756245641523532, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, 0.1524867860807313, 0.15664356061755572, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, i, 0.3850824283435941, 0.929232015972957, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, i, i, 0.18689890454212824, i, i, i, i, i, i, i, i, i, i, 0.17285842509710625]])
        arr_870 = np.array([[0.0869540874214068, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.0184880101156111, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.0363671136111385, 0.0521519258756329, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.0626557093240659, 0.0976959701925822, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [0.110700003802776, 0.239833255113166, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.639897634027878, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.533210717307752, 0.386442222587703, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.226935877285485, 0.228134018585045, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, 0.0762777089351608, 0.106399147962141, i, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, 0.087257672391004, 0.0883575717452914, i, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, i, 0.189694136753678, 0.680416197050363, i, i, i, i, i, i, i, i, i, i, i],
                            [i, i, i, i, 0.127948367761241, i, i, i, i, i, i, i, i, i, i, 0.0958142693422429]])
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        data_550 = ds.variables['AOD550']
        assert_that(np.allclose(data_550[:], arr_550))
        data_870 = ds.variables['AOD870']
        assert_that(np.allclose(data_870[:], arr_870))

    def test_aggregation_over_time(self):
        # Takes 14s
        variable = 'AOD550,AOD870'
        filename = valid_aerosol_cci_filename
        t_start, t_end, t_delta = dt.datetime(2008, 6, 12, 10, 15, 0), dt.datetime(2008, 6, 12, 10, 35, 0), \
            dt.timedelta(minutes=1)
        str_delta = 'PT1M'
        self.do_temporal_aggregate(variable, filename, t_start, t_end, str_delta)
        self.check_temporal_aggregation(t_start, t_end, t_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

        # Test some specific values: these are previous outputs from this aggregate command which have been compared
        # against the original data and found to 'look about right' and therefore used as a baseline. If these values
        # change we should consider being concerned.
        arr_550 = np.array([0.265919434976705, 0.291416287011767, 0.185936305122921,
                            0.199944377828853, 0.15285093049075, 0.216908279904344,
                            0.319887993484934, 0.331330444179776, 0.425076846698876,
                            0.691283313656729, 1.09974754591203, 0.762054610928834,
                            0.414713773233051, 0.229065481573343, 0.565648063149267,
                            0.372544446844707, 0.200231967265146, 0.126068490624287,
                            0.100389930256642, 0.0887082928584682])
        arr_870 = np.array([0.15076443526022, 0.185600860517914, 0.113000460229053,
                            0.123627671143187, 0.0904176585404653, 0.135286251594717,
                            0.24707830522551, 0.29575691650184, 0.383941471034688,
                            0.62935187193469, 0.993525493281297, 0.695747778782674,
                            0.373931448211543, 0.207438293844461, 0.336047132128795,
                            0.220540801986261, 0.118595280574826, 0.0763243285563936,
                            0.0623867045505904, 0.0538315528589818])
        ds = Dataset(self.GRIDDED_OUTPUT_FILENAME)
        data_550 = ds.variables['AOD550']
        assert_arrays_almost_equal(data_550[:], arr_550)
        data_870 = ds.variables['AOD870']
        assert_arrays_almost_equal(data_870[:], arr_870)


class TestSpatialAggregationByDataProduct(BaseAggregationTest):
    """
    These tests are necessarily limited in scope - we can't check the output is correct for all of them (this is done
    for one specific product in the above class 'TestAggregation') so the best we can reasonably do is:
    - Check the aggregation completes with no errors.
    - Check that the output coordinates reflect the correct aggregation bins.
    - Check that all variables requested are in the output file.
    """

    def test_aggregate_Aerosol_CCI(self):
        # This is tested in the TestAggregation class above
        pass

    def test_aggregate_Cloud_CCI(self):
        # Takes 826s
        variable = '*'  # Would like to run this but it takes up a lot of memory on Jenkins.
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        lon_min, lon_max, lon_delta = 84, 99, 1
        lat_min, lat_max, lat_delta = -6, 6, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_NCAR_RAF(self):
        # Takes 513s
        variable = '*'
        filename = valid_NCAR_NetCDF_RAF_filename
        lon_min, lon_max, lon_delta = -160, -157, 1
        lat_min, lat_max, lat_delta = 30, 50, 5
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')

    def test_aggregate_GASSP(self):
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        lon_min, lon_max, lon_delta = -94, 95, 0.1
        lat_min, lat_max, lat_delta = 30, 31, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')

    def test_aggregate_GASSP2(self):
        # see issue JASCIS-144
        variable = valid_GASSP_not_entirely_correct_variable
        filename = valid_GASSP_not_entirely_correct_filename
        lon_min, lon_max, lon_delta = -180, 180, 10
        lat_min, lat_max, lat_delta = -90, 90, 10
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')

    def test_aggregate_Aeronet(self):
        # Takes 50s
        variable = '*'
        filename = valid_aeronet_filename
        lon_min, lon_max, lon_delta = -1.5, 1.4, 0.01
        lat_min, lat_max, lat_delta = 15, 15.5, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')

    def test_aggregate_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = '*'
        filename = valid_hadgem_filename
        arguments = ['aggregate', variable + ':' + filename + ':kernel=mean', 'x,y', '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['od550aer'])

    def test_aggregate_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')

    def test_aggregate_MODIS_L2(self):
        # Takes 66s
        variable = '*'
        filename = valid_modis_l2_filename
        lon_min, lon_max, lon_delta = -150, 150, 25
        lat_min, lat_max, lat_delta = -72, -63, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')

    def test_aggregate_MODIS_L3(self):
        # (All variables takes 23 mins)
        # Takes 27s
        variable = '*'  # Would like to run this but it takes up a lot of memory on Jenkins.
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 40, 60, 2
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_CloudSatPRECIP(self):
        #Takes 190s
        variable = '*'
        filename = valid_cloudsat_PRECIP_file
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 40, 60, 2
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')

    @unittest.skip("Very resource intensive")
    def test_aggregate_Caliop_L1(self):
        variable = '*'  # This takes over 4 hrs (but does work)
        variable = 'Perpendicular_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        lon_min, lon_max, lon_delta = 0, 60, 20
        lat_min, lat_max, lat_delta = -30, 30, 20
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')

    def test_aggregate_CloudSatRVOD(self):
        # Takes 200s
        variable = '*'  # Slow and runs out of memory
        variable = 'RVOD_liq_water_content,RVOD_ice_water_path'
        filename = valid_cloudsat_RVOD_file
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 40, 60, 2
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Caliop_L2(self):
        # Takes 37 mins
        variable = '*'
        filename = valid_caliop_l2_filename
        lon_min, lon_max, lon_delta = 0, 60, 6
        lat_min, lat_max, lat_delta = -30, 30, 6
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='Latitude', lon_name='Longitude')

    def test_subset_ASCII(self):
        # Takes 1s
        variable = '*'
        filename = valid_ascii_filename
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 1, 6, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')

    def test_aggregate_cis_gridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_gridded_output_filename
        arguments = ['aggregate', variable + ':' + filename + ':kernel=mean', 'x,y', '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['TAU_2D_550nm'])


class TestTemporalAggregationByDataProduct(BaseAggregationTest):
    """
    These tests are necessarily limited in scope - we can't check the output is correct for all of them (this is done
    for one specific product in the above class 'TestAggregation') so the best we can reasonably do is:
    - Check the aggregation completes with no errors.
    - Check that the output coordinates reflect the correct aggregation bins.
    - Check that all variables requested are in the output file.
    """

    def test_aggregate_Aerosol_CCI(self):
        # This is tested in the TestAggregation class above
        pass

    def test_aggregate_Cloud_CCI(self):
        # Takes 826s
        variable = '*'  # Would like to run this but it's slow
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        time_min, time_max, time_delta = dt.datetime(2008, 7, 1,), dt.datetime(2008, 8, 1),\
            dt.timedelta(days=5)
        str_delta = 'P5D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='Time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_NCAR_RAF(self):
        # Takes 28s
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        filename = valid_NCAR_NetCDF_RAF_filename
        time_min, time_max, time_delta = dt.datetime(2009, 1, 14, 20, 15), dt.datetime(2009, 1, 15, 2, 45),\
            dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_GASSP(self):
        variable = ",".join(valid_GASSP_aeroplane_vars)
        filename = valid_GASSP_aeroplane_filename
        time_min, time_max, time_delta = dt.datetime(2006, 9, 27, 20, 15), dt.datetime(2006, 9, 27, 22, 45),\
            dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Aeronet(self):
        # Takes 2s
        variable = 'Dateddmmyy,Timehhmmss,Julian_Day,AOT_1640,AOT_1020,AOT_870,AOT_675,AOT_667,AOT_555,AOT_551,' \
                   'AOT_532,AOT_531,AOT_500,AOT_490,AOT_443,AOT_440,AOT_412,AOT_380,AOT_340,Watercm,TripletVar_1640,' \
                   'TripletVar_1020,TripletVar_870,TripletVar_675,TripletVar_667,TripletVar_555,TripletVar_551,' \
                   'TripletVar_532,TripletVar_531,TripletVar_500,TripletVar_490,TripletVar_443,TripletVar_440,' \
                   'TripletVar_412,TripletVar_380,TripletVar_340,WaterError,440870Angstrom,380500Angstrom,' \
                   '440675Angstrom,500870Angstrom,340440Angstrom,440675AngstromPolar,Last_Processing_Date,' \
                   'Solar_Zenith_Angle'
        variable = 'Solar_Zenith_Angle'
        filename = valid_aeronet_filename
        time_min, time_max, time_delta = dt.datetime(2003, 9, 24, 7, 0, 0), dt.datetime(2003, 11, 04, 7, 0, 0),\
            dt.timedelta(days=1)
        str_delta = 'P1D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='DateTime')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        arguments = ['aggregate', variable + ':' + filename + ':kernel=mean', 't', '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_cis_ungridded(self):
        # Takes 2s
        variable = 'AOD550,AOD870,latitude,time'
        filename = valid_cis_ungridded_output_filename
        time_min, time_max, time_delta = dt.datetime(2008, 6, 12, 10, 18, 37), dt.datetime(2008, 6, 12, 10, 19, 47),\
            dt.timedelta(seconds=1)
        str_delta = 'PT1S'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_MODIS_L2(self):
        # Takes 20 mins
        variable = 'Solar_Zenith,Latitude,Sensor_Azimuth,Longitude'
        filename = valid_modis_l2_filename
        time_min, time_max, time_delta = dt.datetime(2010, 1, 1, 22, 55, 19), dt.datetime(2010, 1, 1, 22, 58, 44),\
            dt.timedelta(minutes=1)
        str_delta = 'PT1M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='Scan_Start_Time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_MODIS_L3(self):
        # Takes 8s
        variable = 'Optical_Depth_Ratio_Small_Land_And_Ocean_Std_Deviation_Mean,Solar_Zenith_Std_Deviation_Mean,' \
                   'Solar_Azimuth_Std_Deviation_Mean,Optical_Depth_Ratio_Small_Land_And_Ocean_Pixel_Counts,' \
                   'Optical_Depth_Ratio_Small_Land_QA_Std_Deviation_Mean'
        filename = valid_modis_l3_filename
        time_min, time_max, time_delta = dt.datetime(2010, 1, 13, 0, 0, 1), dt.datetime(2010, 1, 13, 0, 1, 44),\
            dt.timedelta(seconds=20)
        str_delta = 'PT20S'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='DateTime')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_CloudSatPRECIP(self):
        # Takes 28s
        # RuntimeError: NetCDF: String match to name in use
        variable = 'Profile_time,Latitude,Longitude,DEM_elevation,Data_quality'
        filename = valid_cloudsat_PRECIP_file
        time_min, time_max, time_delta = dt.datetime(2008, 2, 14, 0, 57, 36), dt.datetime(2008, 2, 14, 2, 9, 36),\
            dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_CloudSatRVOD(self):
        # Takes 41s
        variable = 'RVOD_liq_water_content,RVOD_ice_water_path'
        filename = valid_cloudsat_RVOD_file
        time_min, time_max, time_delta = dt.datetime(2007, 6, 29, 13, 12, 0), dt.datetime(2007, 6, 29, 14, 29, 0),\
            dt.timedelta(minutes=23)
        str_delta = 'PT23M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='Profile_time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    @unittest.skip("Very resource intensive")
    def test_aggregate_Caliop_L1(self):
        # This takes a long time to run (we've never seen it complete, even on sci-1).
        variable = 'Perpendicular_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        time_min, time_max, time_delta = dt.datetime(2009, 12, 31, 23, 40, 0), dt.datetime(2010, 1, 1, 0, 17, 17),\
            dt.timedelta(minutes=15)
        str_delta = 'PT15M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='Profile_Time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Caliop_L2(self):
        # Takes 20s
        variable = 'Perpendicular_Backscatter_Coefficient_532,' \
                   'Perpendicular_Backscatter_Coefficient_Uncertainty_532,Pressure'
        filename = valid_caliop_l2_filename
        time_min, time_max, time_delta = dt.datetime(2009, 12, 31, 23, 40, 0), dt.datetime(2010, 1, 1, 0, 17, 17),\
            dt.timedelta(minutes=15)
        str_delta = 'PT15M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta, time_name='Profile_Time')
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_ASCII(self):
        # Takes 1s
        variable = 'value'
        filename = valid_ascii_filename
        time_min, time_max, time_delta = dt.datetime(2012, 8, 23, 15, 0, 0), dt.datetime(2012, 8, 28),\
            dt.timedelta(days=1)
        str_delta = 'P1D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, variable.split(','))


class TestMomentsKernel(BaseAggregationTest):

    def test_GIVEN_no_kernel_specified_WHEN_aggregate_THEN_moments_used_as_default(self):
        # Takes 1s
        variable = 'AOD550'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_min, lon_max, lon_delta, lat_min, lat_max, lat_delta)
        arguments = ['aggregate', variable + ':' + filename, grid, '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')
        expected_vars = ['AOD550', 'AOD550_std_dev', 'AOD550_num_points']
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, expected_vars)

    def test_aggregate_netCDF_gridded_HadGem(self):
        # Takes 1s
        variable = 'od550aer'
        filename = valid_hadgem_filename
        grid = 'x,y'
        arguments = ['aggregate', variable + ':' + filename + ':kernel=moments', grid, '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        expected_vars = ['od550aer', 'od550aer_std_dev', 'od550aer_num_points']
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, expected_vars)

    def test_moments_kernel_aggregate_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_min, lon_max, lon_delta, lat_min, lat_max, lat_delta)
        arguments = ['aggregate', variable + ':' + filename + ':kernel=moments', grid, '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')
        expected_vars = ['AOD870', 'AOD870_std_dev', 'AOD870_num_points',
                         'AOD550', 'AOD550_std_dev', 'AOD550_num_points']
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, expected_vars)
