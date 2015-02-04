import unittest

from jasmin_cis.cis import col_cmd
from jasmin_cis.test.integration.base_integration_test import BaseIntegrationTest
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *


class TestUngriddedGriddedColocate(BaseIntegrationTest):

    def test_GIVEN_single_variable_WHEN_colocate_THEN_successful_colocation(self):
        variable = cis_test_files["NCAR_NetCDF_RAF"].data_variable_name
        filename = cis_test_files["NCAR_NetCDF_RAF"].master_filename
        sample_file = valid_hadgem_filename
        colocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['ATX'])

    def test_GIVEN_single_variable_WHEN_colocate_box_THEN_successful_colocation(self):
        variable = cis_test_files["NCAR_NetCDF_RAF"].data_variable_name
        filename = cis_test_files["NCAR_NetCDF_RAF"].master_filename
        sample_file = valid_hadgem_filename
        colocator_and_opts = 'box[h_sep=10],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['ATX'])

    def test_GIVEN_multiple_variables_on_same_coords_WHEN_colocate_THEN_successful_colocation(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        colocator_and_opts = 'bin,kernel=mean,variable=TAU_2D_550nm'
        arguments = ['col', variable1 + ',' + variable2 + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD550', 'AOD870'])

    def test_GIVEN_multiple_datagroups_on_same_coords_WHEN_colocate_THEN_successful_colocation(self):
        variable1 = valid_aerosol_cci_variable
        variable2 = valid_aerosol_cci_variable_2
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        colocator_and_opts = 'bin,kernel=mean,variable=TAU_2D_550nm'
        arguments = ['col', variable1 + ':' + filename,
                     variable2 + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ['AOD550', 'AOD870'])

    def test_Aeronet_onto_NetCDF_Gridded(self):
        # JASCIS-120
        # Takes 6s
        vars = ["AOT_440", "AOT_870"]
        filename = valid_aeronet_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_GASSP_plane_onto_NetCDF_Gridded(self):
        # Takes 15s
        vars = valid_GASSP_aeroplane_vars
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_GASSP_ship_onto_NetCDF_Gridded(self):
        # Takes 10mins
        vars = valid_GASSP_ship_vars
        filename = valid_GASSP_ship_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_GASSP_station_onto_NetCDF_Gridded(self):
        # Takes 27s
        vars = valid_GASSP_station_vars
        filename = valid_GASSP_station_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_cis_output_onto_NetCDF_Gridded(self):
        # Takes 5s
        vars = [valid_cis_ungridded_output_variable]
        filename = valid_cis_ungridded_output_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_ASCII_onto_NetCDF_Gridded(self):
        # Takes 5s
        vars = ["values"]
        filename = valid_ascii_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, ["value"])
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, ["value"])

    def test_cloud_cci_onto_NetCDF_Gridded(self):
        # Takes 460 s
        vars = [valid_cloud_cci_variable, valid_cloud_cci_8_bit_variable]
        filename = valid_cloud_cci_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_cloudsat_PRECIP_onto_NetCDF_Gridded(self):
        # Takes 15s
        vars = [valid_cloudsat_PRECIP_variable]
        filename = valid_cloudsat_PRECIP_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=nn_h,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_cloudsat_PRECIP_onto_NetCDF_Gridded_using_moments_kernel(self):
        # Takes 15s
        vars = [valid_cloudsat_PRECIP_variable]
        filename = valid_cloudsat_PRECIP_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = [valid_cloudsat_PRECIP_variable, valid_cloudsat_PRECIP_variable+'_std_dev',
                    valid_cloudsat_PRECIP_variable+'_num_points']
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_cloudsat_RVOD_onto_NetCDF_Gridded(self):
        # Takes 290s
        vars = [valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable]
        filename = valid_cloudsat_RVOD_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_CALIOP_L1_onto_NetCDF_Gridded(self):
        vars = [valid_caliop_l1_variable]
        filename = valid_caliop_l1_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_CALIOP_L2_onto_NetCDF_Gridded(self):
        vars = [valid_caliop_l2_variable]
        filename = valid_caliop_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_MODIS_L2_onto_NetCDF_Gridded(self):
        # Takes 20s
        vars = ['Solar_Zenith', 'Optical_Depth_Ratio_Small_Land_And_Ocean']
        filename = valid_modis_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_MODIS_L2_onto_NetCDF_Gridded_with_moments_kernel(self):
        # Takes 20s
        vars = ['Solar_Zenith', 'Optical_Depth_Ratio_Small_Land_And_Ocean']
        filename = valid_modis_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = []
        for var in vars:
            out_vars.extend([var, var + '_std_dev', var + '_num_points'])
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, out_vars)

    def test_MODIS_L3_onto_NetCDF_Gridded(self):
        # Takes 27s
        vars = [valid_modis_l3_variable]
        filename = valid_modis_l3_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)


class TestGriddedGriddedColocate(BaseIntegrationTest):

    def test_HadGem_onto_ECHAMHAM(self):
        # Takes 2s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_HadGem_onto_cis_gridded_output(self):
        # Takes 1s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_cis_gridded_output_filename
        sample_var = valid_cis_gridded_output_variable
        colocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_ECHAMHAM_onto_HadGem(self):
        # Takes 2s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

    def test_ECHAMHAM_onto_HadGem_using_moments_kernel(self):
        # Takes 2s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        colocator_and_opts = 'bin,kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = []
        for var in vars:
            out_vars.extend([var, var + '_std_dev', var + '_num_points'])
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, out_vars)

    def test_HadGem_onto_ECHAMHAM_nn(self):
        # Takes
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.GRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.GRIDDED_OUTPUT_FILENAME, vars)

class TestUngriddedUngriddedColocate(BaseIntegrationTest):

    @unittest.skip("Very resource intensive")
    def test_GASSP_onto_CALIOP_L1(self):
        # Ran for 14hr, not finished. (with no h_sep)
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_caliop_l1_filename
        colocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

    @unittest.skip("Very resource intensive")
    def test_GASSP_onto_CALIOP_L2(self):
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_caliop_l2_filename
        colocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

    def test_Aeronet_onto_GASSP(self):
        # Takes 81 s
        # Two vars takes 160s - shouldn't?
        variable = "AOT_440,AOT_870"
        filename = valid_aeronet_filename
        sample_file = valid_GASSP_aeroplane_filename
        colocator_and_opts = 'box[h_sep=10m],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(","))

    def test_GASSP_onto_Aeronet(self):
        # Takes 73s
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_aeronet_filename
        colocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(","))

    def test_GASSP_onto_Aeronet_using_moments_kernel(self):
        # Takes 73s
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_aeronet_filename
        colocator_and_opts = 'box[h_sep=10km],kernel=moments'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = [variable, variable + '_std_dev', variable + '_num_points']
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, valid_aeronet_variable, self.UNGRIDDED_OUTPUT_FILENAME, out_vars)

    def test_GASSP_onto_GASSP(self):
        # Takes 6.5mins
        vars = valid_GASSP_station_vars[:2]
        filename = valid_GASSP_station_filename
        sample_file = valid_GASSP_aeroplane_filename
        colocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_Aeronet_onto_CloudSat(self):
        # Takes 5hrs
        variable = "AOT_440,AOT_870"
        filename = valid_aeronet_filename
        sample_file = valid_cloudsat_PRECIP_file
        colocator_and_opts = 'box[h_sep=10m],kernel=mean'
        arguments = ['col', variable + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, variable.split(","))


class TestGriddedUngriddedColocate(BaseIntegrationTest):

    def test_NetCDF_Gridded_onto_Aeronet(self):
        # Takes 4s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_aeronet_filename
        sample_var = valid_aeronet_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP_using_moments_kernel(self):
        # Takes 850s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        colocator_and_opts = 'box[h_sep=100km],kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = []
        for var in vars:
            out_vars.extend([var, var + '_std_dev', var + '_num_points'])
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, out_vars)

    def test_NetCDF_Gridded_onto_MODIS_L2(self):
        # Takes 16s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_modis_l2_filename
        sample_var = valid_modis_l2_variable
        colocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_MODIS_L3(self):
        # Takes 47s
        vars = valid_hadgem_variable,
        filename = valid_hadgem_filename
        sample_file = valid_modis_l3_filename
        sample_var = valid_modis_l3_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_NetCDF_Gridded_onto_CALIOP_L1(self):
        vars = valid_hadgem_variable,
        filename = valid_hadgem_filename
        sample_file = valid_caliop_l1_filename
        sample_var = valid_caliop_l1_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_NetCDF_Gridded_onto_CALIOP_L2(self):
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_caliop_l2_filename
        sample_var = valid_caliop_l2_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cloudsat_PRECIP(self):
        # Takes 23s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloudsat_PRECIP_file
        sample_var = valid_cloudsat_PRECIP_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cloudsat_RVOD(self):
        # Takes 125s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloudsat_RVOD_file
        sample_var = valid_cloudsat_RVOD_sdata_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cloud_cci(self):
        # Takes 690s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloud_cci_filename
        sample_var = valid_cloud_cci_8_bit_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_aerosol_cci(self):
        # Takes 30s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_aerosol_cci_filename
        sample_var = valid_aerosol_cci_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_ASCII(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_ascii_filename
        sample_var = "values"
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_NCAR_RAF(self):
        # Takes 30s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_NCAR_NetCDF_RAF_filename
        sample_var = valid_NCAR_NetCDF_RAF_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cis_output_data(self):
        # Takes 3s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cis_ungridded_output_filename
        sample_var = valid_cis_ungridded_output_variable
        colocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + filename,
                     sample_file + ':colocator=' + colocator_and_opts,
                     '-o', self.OUTPUT_NAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.UNGRIDDED_OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.UNGRIDDED_OUTPUT_FILENAME, vars)

if __name__ == '__main__':
    unittest.main()
