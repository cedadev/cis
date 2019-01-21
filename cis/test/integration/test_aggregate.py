from netCDF4 import Dataset
import datetime as dt
import unittest

import numpy as np

from cis.cis_main import aggregate_cmd
from cis.test.integration.base_integration_test import BaseIntegrationTest
from cis.test.integration_test_data import *
from cis.test.utils_for_testing import *
from cis.parse import parse_args


class BaseAggregationTest(BaseIntegrationTest):
    def check_grid_aggregation(self, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta,
                               lat_name='latitude', lon_name='longitude'):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        expected_lat_bnds = np.array([[y, y + lat_delta] for y in np.arange(lat_start, lat_end, lat_delta)])
        expected_lon_bnds = np.array([[x, x + lon_delta] for x in np.arange(lon_start, lon_end, lon_delta)])
        lat_bnds = self.ds.variables[lat_name + '_bnds']
        lon_bnds = self.ds.variables[lon_name + '_bnds']
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
        self.ds.close()

    def check_temporal_aggregation(self, time_start, time_end, time_delta, time_name='time'):
        self.ds = Dataset(self.OUTPUT_FILENAME)
        # Convert from time to days after..

        def convert_to_days_since_cis_epoch(date_time):
            cis_standard = dt.datetime(1600, 1, 1, 0, 0, 0)
            return (date_time - cis_standard).total_seconds() / dt.timedelta(days=1).total_seconds()

        time_start = convert_to_days_since_cis_epoch(time_start)
        time_end = convert_to_days_since_cis_epoch(time_end)
        time_delta = time_delta.total_seconds() / dt.timedelta(days=1).total_seconds()

        expected_time_bnds = np.array([[t, t + time_delta] for t in np.arange(time_start, time_end, time_delta)])
        time_bnds = self.ds.variables[time_name + '_bnds']
        assert_that(time_bnds.shape == expected_time_bnds.shape)
        assert_that(np.allclose(time_bnds[:], expected_time_bnds))
        self.ds.close()

    def do_spatial_aggregate(self, variable, filename, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta):
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_start, lon_end, lon_delta, lat_start, lat_end, lat_delta)
        arguments = ['aggregate', variable + ':' + escape_colons(filename) + ':kernel=mean', grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)

    def do_temporal_aggregate(self, variable, filename, t_start, t_end, str_delta):
        grid = 't=[%s,%s,%s]' % (t_start.isoformat(), t_end.isoformat(), str_delta)
        arguments = ['aggregate', variable + ':' + escape_colons(filename) + ':kernel=mean', grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)


class TestAggregation(BaseAggregationTest):
    """
    This class provides integration testing for the Aggregation command, ensuring that for one specific product
    (Aerosol CCI), the aggregation is correct and the results are what we expect.
    """

    def test_aggregation_over_latlon(self):
        import numpy.ma as ma
        # Takes 20s
        variable = 'AOD550,AOD870'
        filename = valid_aerosol_cci_filename
        lat_start, lat_end, lat_delta = -40, 80, 10  # 12
        lon_start, lon_end, lon_delta = -20, 140, 10  # 16
        self.do_spatial_aggregate(variable, filename, lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta)
        self.check_grid_aggregation(lat_start, lat_end, lat_delta, lon_start, lon_end, lon_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

        # Test some specific values: these are previous outputs from this aggregate command which have been compared
        # against the original data and found to 'look about right' and therefore used as a baseline. If these values
        # change we should consider being concerned.
        i = float('inf')
        arr_550 = np.array([[[0.1096153093624289, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.405634596128, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.175624571614, 0.152486790551, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.09970282124016773, 0.1629985723514454, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.19553465147813162, 0.405634596128, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.7052307901349156, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.5859629385860146, 0.4436802918665714, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.29588747474573723, 0.2914036842614198, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.13670555069561927, 0.1756245641523532, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, 0.1524867860807313, 0.15664356061755572, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, i, 0.1415671800312243, 0.8644281417604477, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, i, i, 0.18689890454212824, i, i, i, i, i, i, i, i, i, i, 0.17285842509710625]]])
        arr_870 = np.array([[[0.0869540874214068, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.239833246086, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.106763551248, 0.0872576713562, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.0626557093240659, 0.0976959701925822, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [0.110700003802776, 0.239833255113166, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.639897634027878, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.533210717307752, 0.386442222587703, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.226935877285485, 0.228134018585045, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, 0.0762777089351608, 0.106399147962141, i, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, 0.087257672391004, 0.0883575717452914, i, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, i, 0.189694136753678, 0.680416197050363, i, i, i, i, i, i, i, i, i, i, i],
                             [i, i, i, i, 0.127948367761241, i, i, i, i, i, i, i, i, i, i, 0.0958142693422429]]])
        arr_550 = ma.masked_invalid(arr_550)
        arr_870 = ma.masked_invalid(arr_870)
        self.ds = Dataset(self.OUTPUT_FILENAME)
        data_550 = self.ds.variables['AOD550']
        assert_arrays_almost_equal(data_550[:], arr_550.reshape((16,12,1)))
        data_870 = self.ds.variables['AOD870']
        assert_arrays_almost_equal(data_870[:], arr_870.reshape((16,12,1)))

    def test_aggregation_over_time(self):
        import numpy.ma as ma
        # Takes 14s
        variable = 'AOD550,AOD870'
        filename = valid_aerosol_cci_filename
        t_start, t_end = dt.datetime(2008, 6, 12, 10, 15, 0), dt.datetime(2008, 6, 12, 10, 35, 0)
        t_delta = dt.timedelta(minutes=1)
        str_delta = 'PT1M'
        self.do_temporal_aggregate(variable, filename, t_start, t_end, str_delta)
        self.check_temporal_aggregation(t_start, t_end, t_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

        # Test some specific values: these are previous outputs from this aggregate command which have been compared
        # against the original data and found to 'look about right' and therefore used as a baseline. If these values
        # change we should consider being concerned.
        i = float('inf')
        arr_550 = np.array( [[[0.2724732138893821, 0.2845287322998047, 0.18888297843565602,
                               0.1977633680318641, 0.1528509303068309, 0.21690222715974708,
                               0.3218141342953317, 0.3296216605627661, 0.42861915269278755,
                               0.6922391289425149, 1.1032210622605763, 0.7501978423274019,
                               0.4114444071076453, i, 0.5656480511415352, 0.3725444489875726,
                               0.20023197438583437, 0.12606849266025288, 0.10038993358612061,
                               0.08870828946431478]]])
        arr_870 = np.array([[[0.15527870871803978, 0.177825194138747, 0.11566017769478462,
                               0.12211483395949896, 0.09108650039336486, 0.139907898276485,
                               0.24998173519681813, 0.29386406702711093, 0.38747846944250536,
                               0.6303785410104443, 0.999659818761489, 0.6851485338292652,
                               0.37053351032777904, 0.2074383, 0.336047126251517, 0.22054079781591365,
                               0.11859528582197681, 0.07632432809566862, 0.062386703491210935,
                               0.053831556108262804]]])
        arr_550 = ma.masked_invalid(arr_550)
        self.ds = Dataset(self.OUTPUT_FILENAME)
        data_550 = self.ds.variables['AOD550']
        assert_arrays_almost_equal(data_550[:], arr_550, 1.0e-2)
        data_870 = self.ds.variables['AOD870']
        assert_arrays_almost_equal(data_870[:], arr_870, 1.0e-2)

    def test_aggregation_of_multiple_variables_gives_same_result(self):
        # JASCIS-281
        variable = 'AOT_440'
        filename = another_valid_aeronet_filename
        t_start, t_end = dt.datetime(1999, 0o1, 0o1), dt.datetime(1999, 12, 29)
        t_delta = dt.timedelta(hours=6)
        str_delta = 'PT6H'
        self.do_temporal_aggregate(variable, filename, t_start, t_end, str_delta)
        self.check_temporal_aggregation(t_start, t_end, t_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

        # Read the aggregated data
        self.ds = Dataset(self.OUTPUT_FILENAME)
        aot_440 = self.ds.variables['AOT_440'][:]

        # Clean up the old aggregation
        self.ds.close()
        os.remove(self.OUTPUT_FILENAME)

        # Now redo the aggregation, but for all AOT variables
        self.do_temporal_aggregate('AOT*', filename, t_start, t_end, str_delta)

        # Read the new data in
        self.ds = Dataset(self.OUTPUT_FILENAME)
        aot_440_multi_var = self.ds.variables['AOT_440'][:]

        # And check they are the same...
        assert_arrays_almost_equal(aot_440, aot_440_multi_var)


class TestSpatialAggregationByDataProduct(BaseAggregationTest):
    """
    These tests are necessarily limited in scope - we can't check the output is correct for all of them (this is done
    for one specific product in the above class 'TestAggregation') so the best we can reasonably do is:
    - Check the aggregation completes with no errors.
    - Check that the output coordinates reflect the correct aggregation bins.
    - Check that all variables requested are in the output file.
    """

    def test_aggregate_Aerosol_CCI_with_lon_wraparound(self):
        variable = valid_aerosol_cci_variable
        filename = valid_aerosol_cci_filename
        lon_min, lon_max, lon_delta = 10, 350, 10
        lat_min, lat_max, lat_delta = -90, 90, 30
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Cloud_CCI_with_dimension_vars(self):
        variable = 'time,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        lon_min, lon_max, lon_delta = 84, 99, 1
        lat_min, lat_max, lat_delta = -6, 6, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['aggregated_time', 'solar_zenith_view_no1'])

    def test_aggregate_Cloud_CCI(self):
        variable = 'satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        lon_min, lon_max, lon_delta = 84, 99, 1
        lat_min, lat_max, lat_delta = -6, 6, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Cloud_CCI_for_comparison_with_collocation(self):
        """
        Takes ~80s on aopposxlap18. This test is primarily to compare the speed of ungridded->gridded collocation and
        aggregation, which should in principle be just as quick as each other. This test mirrors the
        test_cloud_cci_onto_NetCDF_Gridded test in test_colocate.py.
        """
        variables = ','.join([valid_cloud_cci_variable, valid_cloud_cci_8_bit_variable])
        filename = valid_cloud_cci_filename
        grid = 'x=[0, 358.125, 1.875],y=[-90, 90, 1.25],t=[2007-06-01,2007-06-30,PT3H]'
        arguments = ['aggregate', variables + ':' + escape_colons(filename) + ':kernel=mean', grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)

        # This check can't deal with the combined temporal and spatial aggregation so skip it
        #self.check_grid_aggregation(0, 358.125, 1.875, -90, 90, 1.25)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variables.split(','))

    def test_aggregate_NCAR_RAF(self):
        # Takes 513s
        variable = valid_NCAR_NetCDF_RAF_variable
        filename = valid_NCAR_NetCDF_RAF_filename
        lon_min, lon_max, lon_delta = -160, -157, 1
        lat_min, lat_max, lat_delta = 30, 50, 5
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    def test_aggregate_GASSP(self):
        variable = '*'
        filename = valid_GASSP_aeroplane_filename
        lon_min, lon_max, lon_delta = -94, 95, 0.1
        lat_min, lat_max, lat_delta = 30, 31, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    def test_aggregate_GASSP2(self):
        # see issue JASCIS-144
        variable = valid_GASSP_not_entirely_correct_variable
        filename = valid_GASSP_not_entirely_correct_filename
        lon_min, lon_max, lon_delta = -180, 180, 10
        lat_min, lat_max, lat_delta = -90, 90, 10
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    def test_aggregate_Aeronet(self):
        # Takes 50s
        variable = 'AOT_*'
        filename = valid_aeronet_filename
        lon_min, lon_max, lon_delta = -1.5, 1.4, 0.01
        lat_min, lat_max, lat_delta = 15, 15.5, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    def test_aggregate_netCDF_gridded_HadGem(self):
        # Test aggregating a gridded file, it should work but throw a deprecation
        # Takes 1s
        variable = '*'
        filename = valid_hadgem_filename
        arguments = ['aggregate', variable + ':' + escape_colons(filename) + ':kernel=mean', 'x,y', '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)

        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['od550aer'])

    def test_aggregate_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    @skip_pyhdf
    def test_aggregate_MODIS_L2(self):
        # Takes 66s
        variable = '*'
        filename = valid_modis_l2_filename
        lon_min, lon_max, lon_delta = -150, 150, 25
        lat_min, lat_max, lat_delta = -72, -63, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    @skip_pyhdf
    def test_aggregate_CloudSatPRECIP(self):
        # Takes 190s
        variable = '*'
        filename = valid_cloudsat_PRECIP_file
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 40, 60, 2
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    @unittest.skip("Very resource intensive")
    def test_aggregate_Caliop_L1(self):
        variable = '*'  # This takes over 4 hrs (but does work)
        variable = 'Perpendicular_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        lon_min, lon_max, lon_delta = 0, 60, 20
        lat_min, lat_max, lat_delta = -30, 30, 20
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    @skip_pyhdf
    def test_aggregate_CloudSatRVOD(self):
        # Takes 200s
        variable = '*'  # Slow and runs out of memory
        variable = 'RVOD_liq_water_path,RVOD_ice_water_path'
        filename = valid_cloudsat_RVOD_file
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 40, 60, 2
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_aggregate_Caliop_L2(self):
        # Takes 37 mins
        variable = '*'
        filename = valid_caliop_l2_filename
        lon_min, lon_max, lon_delta = 0, 60, 6
        lat_min, lat_max, lat_delta = -30, 30, 6
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)

    def test_subset_ASCII(self):
        # Takes 1s
        variable = '*'
        filename = valid_ascii_filename
        lon_min, lon_max, lon_delta = -10, 10, 2
        lat_min, lat_max, lat_delta = 1, 6, 1
        self.do_spatial_aggregate(variable, filename, lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta)


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

    def test_aggregate_Cloud_CCI_with_dimension_vars(self):
        # Takes 826s
        variable = 'time,lon,lat,satellite_zenith_view_no1,solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        time_min, time_max = dt.datetime(2008, 7, 1, ), dt.datetime(2008, 8, 1)

        time_delta = dt.timedelta(days=5)
        str_delta = 'P5D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Cloud_CCI(self):
        variable = 'solar_zenith_view_no1'
        filename = valid_cloud_cci_filename
        time_min, time_max = dt.datetime(2008, 7, 1, ), dt.datetime(2008, 8, 1)

        time_delta = dt.timedelta(days=5)
        str_delta = 'P5D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_NCAR_RAF(self):
        # Takes 28s
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        filename = valid_NCAR_NetCDF_RAF_filename
        time_min, time_max = dt.datetime(2009, 1, 14, 20, 15), dt.datetime(2009, 1, 15, 2, 45)

        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_NCAR_RAF_with_named_time_variable_standard_name(self):
        # Takes 28s
        variable = "LATC,LONC,GGALTC,Time,PSXC,WSC,ATX,ATHR2,CONCD_LWI"
        filename = valid_NCAR_NetCDF_RAF_filename
        time_min, time_max = dt.datetime(2009, 1, 14, 20, 15), dt.datetime(2009, 1, 15, 2, 45)

        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'

        grid = 'time=[%s,%s,%s]' % (time_min.isoformat(), time_max.isoformat(), str_delta)
        arguments = ['aggregate', variable + ':' + escape_colons(filename) + ':kernel=mean', grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)

        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_GASSP(self):
        variable = ",".join(valid_GASSP_aeroplane_vars)
        filename = valid_GASSP_aeroplane_filename
        time_min, time_max = dt.datetime(2006, 9, 27, 20, 15), dt.datetime(2006, 9, 27, 22, 45)
        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_GASSP_aux_coord(self):
        # Takes 1.3s
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        variable = cis_test_files['GASSP_aux_coord'].data_variable_name
        time_min, time_max = dt.datetime(2006, 9, 27, 20, 15), dt.datetime(2006, 9, 27, 22, 45)
        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Aeronet(self):
        # Takes 2s
        variable = 'AOT_440'
        filename = valid_aeronet_filename
        time_min, time_max = dt.datetime(1999, 1, 1, 0, 0, 0), dt.datetime(1999, 12, 29, 0, 0, 0)
        time_delta = dt.timedelta(hours=6)
        str_delta = 'PT6H'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_Aeronet_multi_var(self):
        # Takes 2s
        variable = 'AOT_1640,AOT_1020,AOT_870,AOT_675,AOT_667,AOT_555,AOT_551,' \
                   'AOT_532,AOT_531,AOT_500,AOT_490,AOT_443,AOT_440,AOT_412,AOT_380,AOT_340'
        filename = valid_aeronet_filename
        time_min, time_max = dt.datetime(1999, 1, 1), dt.datetime(1999, 12, 29)
        time_delta = dt.timedelta(hours=6)
        str_delta = 'PT6H'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))
        self.check_output_vars_are_different(self.OUTPUT_FILENAME, variable.split(',')[:5])

    def test_aggregate_cis_ungridded(self):
        # Takes 2s
        variable = 'AOD550,AOD870,latitude,time'
        filename = valid_cis_ungridded_output_filename
        time_min, time_max = dt.datetime(2008, 6, 12, 10, 18, 37), dt.datetime(2008, 6, 12, 10, 19, 47)
        time_delta = dt.timedelta(seconds=1)
        str_delta = 'PT1S'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_aggregate_MODIS_L2(self):
        # Takes 20 mins
        variable = 'Solar_Zenith,Latitude,Sensor_Azimuth,Longitude'
        filename = valid_modis_l2_filename
        time_min, time_max = dt.datetime(2010, 1, 1, 22, 55, 19), dt.datetime(2010, 1, 1, 22, 58, 44)
        time_delta = dt.timedelta(minutes=1)
        str_delta = 'PT1M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_aggregate_CloudSatPRECIP_with_dimension_variables(self):
        # Takes 28s
        # RuntimeError: NetCDF: String match to name in use
        variable = 'Profile_time,Latitude,Longitude,DEM_elevation,Data_quality'
        filename = valid_cloudsat_PRECIP_file
        time_min, time_max = dt.datetime(2008, 2, 14, 0, 57, 36), dt.datetime(2008, 2, 14, 2, 9, 36)
        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(',') +
                                             ['aggregated_Profile_time'])

    @skip_pyhdf
    def test_aggregate_CloudSatPRECIP(self):
        variable = valid_cloudsat_PRECIP_variable
        filename = valid_cloudsat_PRECIP_file
        time_min, time_max = dt.datetime(2008, 2, 14, 0, 57, 36), dt.datetime(2008, 2, 14, 2, 9, 36)
        time_delta = dt.timedelta(minutes=30)
        str_delta = 'PT30M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [valid_cloudsat_PRECIP_variable])

    @skip_pyhdf
    def test_aggregate_CloudSatRVOD(self):
        # Takes 41s
        variable = 'RVOD_liq_water_path,RVOD_ice_water_path'
        filename = valid_cloudsat_RVOD_file
        time_min, time_max = dt.datetime(2007, 6, 29, 13, 12, 0), dt.datetime(2007, 6, 29, 14, 29, 0)
        time_delta = dt.timedelta(minutes=23)
        str_delta = 'PT23M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @unittest.skip("Very resource intensive")
    def test_aggregate_Caliop_L1(self):
        # This takes a long time to run (we've never seen it complete, even on sci-1).
        variable = 'Perpendicular_Attenuated_Backscatter_532'
        filename = valid_caliop_l1_filename
        time_min, time_max = dt.datetime(2009, 12, 31, 23, 40, 0), dt.datetime(2010, 1, 1, 0, 17, 17)
        time_delta = dt.timedelta(minutes=15)
        str_delta = 'PT15M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    @skip_pyhdf
    def test_aggregate_Caliop_L2(self):
        # Takes 20s
        variable = 'Perpendicular_Backscatter_Coefficient_532,' \
                   'Perpendicular_Backscatter_Coefficient_Uncertainty_532,Pressure'
        filename = valid_caliop_l2_filename
        time_min, time_max = dt.datetime(2009, 12, 31, 23, 40, 0), dt.datetime(2010, 1, 1, 0, 17, 17)
        time_delta = dt.timedelta(minutes=15)
        str_delta = 'PT15M'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))

    def test_aggregate_ASCII(self):
        # Takes 1s
        variable = 'value'
        filename = valid_ascii_filename
        time_min, time_max = dt.datetime(2012, 8, 23, 15, 0, 0), dt.datetime(2012, 8, 28)
        time_delta = dt.timedelta(days=1)
        str_delta = 'P1D'
        self.do_temporal_aggregate(variable, filename, time_min, time_max, str_delta)
        self.check_temporal_aggregation(time_min, time_max, time_delta)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(','))


class TestMomentsKernel(BaseAggregationTest):
    def test_GIVEN_no_kernel_specified_WHEN_aggregate_THEN_moments_used_as_default(self):
        # Takes 1s
        variable = 'AOD550'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_min, lon_max, lon_delta, lat_min, lat_max, lat_delta)
        arguments = ['aggregate', variable + ':' + escape_colons(filename), grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')
        expected_vars = ['AOD550', 'AOD550_std_dev', 'AOD550_num_points']
        self.check_output_contains_variables(self.OUTPUT_FILENAME, expected_vars)

    def test_moments_kernel_aggregate_cis_ungridded(self):
        # Takes 1s
        variable = '*'
        filename = valid_cis_ungridded_output_filename
        lon_min, lon_max, lon_delta = 1, 3, 0.3
        lat_min, lat_max, lat_delta = 41, 42, 0.1
        grid = 'x=[%s,%s,%s],y=[%s,%s,%s]' % (lon_min, lon_max, lon_delta, lat_min, lat_max, lat_delta)
        arguments = ['aggregate', variable + ':' + escape_colons(filename) + ':kernel=moments', grid, '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        aggregate_cmd(main_arguments)
        self.check_grid_aggregation(lat_min, lat_max, lat_delta, lon_min, lon_max, lon_delta,
                                    lat_name='latitude', lon_name='longitude')
        expected_vars = ['AOD870', 'AOD870_std_dev', 'AOD870_num_points',
                         'AOD550', 'AOD550_std_dev', 'AOD550_num_points']
        self.check_output_contains_variables(self.OUTPUT_FILENAME, expected_vars)
