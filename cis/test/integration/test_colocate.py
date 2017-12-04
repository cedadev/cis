import unittest

from cis.cis_main import col_cmd
from cis.test.integration.base_integration_test import BaseIntegrationTest
from cis.parse import parse_args
from cis.test.integration_test_data import *


class TestUngriddedGriddedCollocate(BaseIntegrationTest):
    def test_GIVEN_single_variable_WHEN_collocate_THEN_successful_collocation(self):
        variable = cis_test_files["NCAR_NetCDF_RAF"].data_variable_name
        filename = cis_test_files["NCAR_NetCDF_RAF"].master_filename
        sample_file = valid_hadgem_filename
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['ATX'])

    def test_GIVEN_multiple_variables_on_same_coords_WHEN_collocate_THEN_successful_collocation(self):
        variables = valid_aerosol_cci_variable, valid_aerosol_cci_variable_2,
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ','.join(variables) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variables)

    def test_GIVEN_multiple_variables_on_same_coords_plus_dim_vars_WHEN_collocate_THEN_successful_collocation(self):
        variables = valid_aerosol_cci_variable, valid_aerosol_cci_variable_2, 'time'
        filename = valid_aerosol_cci_filename
        sample_file = valid_echamham_filename
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ','.join(variables) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variables)

    def test_Aeronet_onto_NetCDF_Gridded(self):
        # JASCIS-120
        # Takes 6s
        vars = ["AOT_440", "AOT_870"]
        filename = valid_aeronet_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_GASSP_plane_onto_NetCDF_Gridded(self):
        # Takes 15s
        vars = valid_GASSP_aeroplane_vars
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_GASSP_aux_onto_NetCDF_Gridded(self):
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        var = cis_test_files['GASSP_aux_coord'].data_variable_name
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', var + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [var])
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, [var])

    def test_GASSP_ship_onto_NetCDF_Gridded(self):
        # Takes 10mins
        vars = valid_GASSP_ship_vars
        filename = valid_GASSP_ship_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_GASSP_station_onto_NetCDF_Gridded(self):
        # Takes 1s
        var = valid_GASSP_station_vars[0]
        filename = valid_GASSP_station_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', var + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, [var])
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, [var])

    def test_cis_output_onto_NetCDF_Gridded(self):
        # Takes 5s
        vars = [valid_cis_ungridded_output_variable]
        filename = valid_cis_ungridded_output_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_ASCII_onto_NetCDF_Gridded(self):
        # Takes 5s
        vars = ["values"]
        filename = valid_ascii_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ["value"])
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, ["value"])

    def test_cloud_cci_onto_NetCDF_Gridded(self):
        """
        Takes ~80s on aopposxlap18. This test mirrors the test_aggregate_Cloud_CCI_for_comparison_with_collocation
        test in test_aggregate.py.
        """
        variables = [valid_cloud_cci_variable, valid_cloud_cci_8_bit_variable]
        filename = valid_cloud_cci_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(variables) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variables)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, variables)

    @skip_pyhdf
    def test_cloudsat_PRECIP_onto_NetCDF_Gridded(self):
        # Takes 15s
        vars = [valid_cloudsat_PRECIP_variable]
        filename = valid_cloudsat_PRECIP_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=nn_h,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_cloudsat_PRECIP_onto_NetCDF_Gridded_using_moments_kernel(self):
        # Takes 15s
        vars = [valid_cloudsat_PRECIP_variable]
        filename = valid_cloudsat_PRECIP_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = [valid_cloudsat_PRECIP_variable, valid_cloudsat_PRECIP_variable + '_std_dev',
                    valid_cloudsat_PRECIP_variable + '_num_points']
        self.check_output_contains_variables(self.OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_cloudsat_RVOD_onto_NetCDF_Gridded(self):
        # Takes 290s
        vars = [valid_cloudsat_RVOD_sdata_variable, valid_cloudsat_RVOD_vdata_variable]
        filename = valid_cloudsat_RVOD_file
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_CALIOP_L1_onto_NetCDF_Gridded(self):
        vars = [valid_caliop_l1_variable]
        filename = valid_caliop_l1_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @unittest.skip("Very resource intensive")
    def test_CALIOP_L2_onto_NetCDF_Gridded(self):
        vars = [valid_caliop_l2_variable]
        filename = valid_caliop_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_MODIS_L2_onto_NetCDF_Gridded(self):
        # Takes 20s
        vars = ['Solar_Zenith', 'Optical_Depth_Ratio_Small_Land_And_Ocean']
        filename = valid_modis_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=mean,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_MODIS_L2_onto_NetCDF_Gridded_with_moments_kernel(self):
        # Takes 20s
        vars = ['Solar_Zenith', 'Optical_Depth_Ratio_Small_Land_And_Ocean']
        filename = valid_modis_l2_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'bin,kernel=moments,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = []
        for var in vars:
            out_vars.extend([var, var + '_std_dev', var + '_num_points'])
        self.check_output_contains_variables(self.OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, out_vars)


class TestGriddedGriddedCollocate(BaseIntegrationTest):
    """
        The HadGEM test file (os550aer) has three extended dimensions lon (192), lat(145) and t(240)
         The ECHAMHAM test file (ECHAMHAM_AOT550_670) has two extended dimensions lon (192) and lat(96) and a scalar
         t coordinate.
    """

    def test_HadGem_onto_cis_gridded_output_lin(self):
        # Takes 1s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_cis_gridded_output_filename
        sample_var = valid_cis_gridded_output_variable
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_HadGem_onto_ECHAMHAM_lin(self):
        # Sampling HadGEM (higher dimensionality) with ECHAMHAM (lower dimensionality) results in a lower dimensional
        #  dataset
        # Takes 2s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_HadGem_onto_ECHAMHAM_nn(self):
        # Sampling HadGEM (higher dimensionality) with ECHAMHAM (lower dimensionality) results in a lower dimensional
        #  dataset
        # Takes 51s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_file = valid_echamham_filename
        sample_var = valid_echamham_variable_1
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_ECHAMHAM_onto_HadGem_lin(self):
        # Sampling ECHAMHAM (lower dimensionality) with HadGEM (higher dimensionality) results in a lower dimensional
        #  dataset
        # Uses the default kernel which for gridded gridded is lin
        # Takes 2s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars, (192, 145))

    def test_ECHAMHAM_onto_HadGem_nn(self):
        # Sampling ECHAMHAM (lower dimensionality) with HadGEM (higher dimensionality) results in a lower dimensional
        #  dataset
        # Takes 2s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars, (192, 145))

    @unittest.skip("Ths takes a very long time and is a pretty unlikely usage")
    def test_ECHAMHAM_onto_HadGem_box(self):
        # Sampling ECHAMHAM (lower dimensionality) with HadGEM (higher dimensionality) results in a lower dimensional
        #  dataset
        # Takes 1224s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'box[h_sep=500],variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars, (192, 145))

    @skip_pyhdf
    def test_MODIS_L3_onto_NetCDF_Gridded(self):
        # Takes 3s
        vars = [valid_modis_l3_variable]
        filename = valid_modis_l3_filename
        sample_file = valid_hadgem_filename
        sample_var = valid_hadgem_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        # The hadgem file has an extended time coord, which is ignored in the collocation because the
        #  MODIS L3 file only has a scalar time (so you can't resample it).
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars, (145, 192))

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_MODIS_L3(self):
        # Takes 5s
        vars = [valid_hadgem_variable]
        filename = valid_hadgem_filename
        sample_var = valid_modis_l3_variable
        sample_file = valid_modis_l3_filename
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        # The hadgem file has an extended time coord, which is sampled in the collocation from the
        #  MODIS L3 scalar time.
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)


class TestUngriddedUngriddedCollocate(BaseIntegrationTest):
    @unittest.skip("Very resource intensive")
    def test_GASSP_onto_CALIOP_L1(self):
        # Ran for 14hr, not finished. (with no h_sep)
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_caliop_l1_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

    @unittest.skip("Very resource intensive")
    def test_GASSP_onto_CALIOP_L2(self):
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_caliop_l2_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)

    def test_Aeronet_onto_GASSP(self):
        # Takes 81 s
        # Two vars takes 160s - shouldn't?
        variable = "AOT_440,AOT_870"
        filename = valid_aeronet_filename
        sample_file = valid_GASSP_aeroplane_filename
        collocator_and_opts = 'box[h_sep=10m],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(","))

    def test_GASSP_onto_Aeronet(self):
        # Takes 73s
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_aeronet_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(","))

    def test_GASSP_aux_coord_onto_Aeronet(self):
        # Takes 73s
        filename = cis_test_files['GASSP_aux_coord'].master_filename
        variable = cis_test_files['GASSP_aux_coord'].data_variable_name
        sample_file = valid_aeronet_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(","))

    def test_GASSP_onto_Aeronet_using_moments_kernel(self):
        # Takes 73s
        variable = valid_GASSP_aeroplane_variable
        filename = valid_GASSP_aeroplane_filename
        sample_file = valid_aeronet_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=moments'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        out_vars = [variable, variable + '_std_dev', variable + '_num_points']
        self.check_output_contains_variables(self.OUTPUT_FILENAME, out_vars)
        self.check_output_col_grid(sample_file, valid_aeronet_variable, self.OUTPUT_FILENAME, out_vars)

    def test_GASSP_onto_GASSP(self):
        # Takes 6.5mins
        vars = valid_GASSP_station_vars[:2]
        filename = valid_GASSP_station_filename
        sample_file = valid_GASSP_aeroplane_filename
        collocator_and_opts = 'box[h_sep=10km],kernel=mean'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_Aeronet_onto_CloudSat_nn(self):
        # Takes 5hrs
        variable = "AOT_440,AOT_870"
        filename = valid_aeronet_filename
        sample_file = valid_cloudsat_PRECIP_file
        collocator_and_opts = 'box[h_sep=700km],kernel=nn_horizontal_kdtree'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(","))

    @skip_pyhdf
    def test_Aeronet_onto_CloudSat(self):
        # Takes 5hrs
        variable = "AOT_440,AOT_870"
        filename = valid_aeronet_filename
        sample_file = valid_cloudsat_PRECIP_file
        collocator_and_opts = 'box[h_sep=700km],kernel=mean'
        arguments = ['col', variable + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, variable.split(","))


class TestGriddedUngriddedCollocate(BaseIntegrationTest):
    def test_NetCDF_Gridded_onto_ASCII_with_variable(self):
        # Takes 4s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = cis_test_files["ascii"].master_filename
        sample_var = cis_test_files["ascii"].data_variable_name
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_ASCII_no_variable(self):
        # Takes 4s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = cis_test_files["ascii"].master_filename
        sample_var = cis_test_files["ascii"].data_variable_name
        collocator_and_opts = 'nn'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_Aeronet(self):
        # Takes 4s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_aeronet_filename
        sample_var = valid_aeronet_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_Aeronet_lin(self):
        # Takes 4s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_aeronet_filename
        sample_var = valid_aeronet_variable
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP_li(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)
        self.check_output_vars_are_different(self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP_aux_coord_li(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = cis_test_files['GASSP_aux_coord'].master_filename
        sample_var = cis_test_files['GASSP_aux_coord'].data_variable_name
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)
        self.check_output_vars_are_different(self.OUTPUT_FILENAME, vars)

    @unittest.skip("We don't have any hybrid height files to test this currently")
    def test_hybrid_height_onto_GASSP_nn(self):
        # Takes 1s
        vars = [valid_hybrid_height_flat_variable]
        filename = valid_hybrid_height_flat_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_hybrid_pressure_onto_GASSP_nn(self):
        # Takes 1s
        vars = [valid_hybrid_pressure_variable]
        filename = valid_hybrid_pressure_filename
        sample_file = valid_GASSP_aircraft_files_with_different_timestamps[0]
        sample_var = valid_GASSP_aircraft_var_with_different_timestamps
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['mmrbc'])
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, ['mmrbc'])

    @unittest.skip("We don't have any hybrid height files to test this currently")
    def test_hybrid_height_onto_GASSP_li(self):
        # Takes 1s
        vars = [valid_hybrid_height_flat_variable]
        filename = valid_hybrid_height_flat_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_hybrid_pressure_onto_GASSP_li(self):
        # Takes 1s
        vars = [valid_hybrid_pressure_variable]
        filename = valid_hybrid_pressure_filename
        sample_file = valid_GASSP_aircraft_files_with_different_timestamps[0]
        sample_var = valid_GASSP_aircraft_var_with_different_timestamps
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, ['mmrbc'])
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, ['mmrbc'])

    def test_NetCDF_Gridded_onto_GASSP_li_with_extrapolation(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'lin[extrapolate=True],variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_file_variable_attribute_contains_string(self.OUTPUT_FILENAME, vars[0], 'history',
                                                                  "'extrapolate': 'True'")
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP_li_with_nn_in_the_vertical(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'lin[nn_vertical=True],variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_file_variable_attribute_contains_string(self.OUTPUT_FILENAME, vars[0], 'history',
                                                                  "'nn_vertical': 'True'")
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_GASSP_li_with_nn_in_the_vertical_and_extrapolation(self):
        # Takes 1s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_GASSP_aeroplane_filename
        sample_var = valid_GASSP_aeroplane_variable
        collocator_and_opts = 'lin[nn_vertical=True,extrapolate=True],variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_file_variable_attribute_contains_string(self.OUTPUT_FILENAME, vars[0], 'history',
                                                                  "'extrapolate': 'True', 'nn_vertical': 'True'")
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_MODIS_L2(self):
        # Takes 16s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_modis_l2_filename
        sample_var = valid_modis_l2_variable
        collocator_and_opts = 'lin,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)
        self.check_output_vars_are_different(self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_MODIS_L2_nn(self):
        # Takes 16s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_modis_l2_filename
        sample_var = valid_modis_l2_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)
        self.check_output_vars_are_different(self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_MODIS_L3(self):
        # Takes 47s
        vars = valid_hadgem_variable,
        filename = valid_hadgem_filename
        sample_file = valid_modis_l3_filename
        sample_var = valid_modis_l3_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_CALIOP_L1(self):
        vars = valid_hadgem_variable,
        filename = valid_hadgem_filename
        sample_file = valid_caliop_l1_filename
        sample_var = valid_caliop_l1_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_CALIOP_L2(self):
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_caliop_l2_filename
        sample_var = valid_caliop_l2_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_cloudsat_PRECIP(self):
        # Takes 23s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloudsat_PRECIP_file
        sample_var = valid_cloudsat_PRECIP_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    @skip_pyhdf
    def test_NetCDF_Gridded_onto_cloudsat_RVOD(self):
        # Takes 125s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloudsat_RVOD_file
        sample_var = valid_cloudsat_RVOD_sdata_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cloud_cci(self):
        # Takes 690s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cloud_cci_filename
        sample_var = valid_cloud_cci_8_bit_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_aerosol_cci(self):
        # Takes 30s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_aerosol_cci_filename
        sample_var = valid_aerosol_cci_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_NCAR_RAF_with_var(self):
        # Takes 30s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_NCAR_NetCDF_RAF_filename
        sample_var = valid_NCAR_NetCDF_RAF_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_NCAR_RAF(self):
        # Takes 30s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_NCAR_NetCDF_RAF_filename
        sample_var = valid_NCAR_NetCDF_RAF_variable
        collocator_and_opts = 'nn'
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)

    def test_NetCDF_Gridded_onto_cis_output_data(self):
        # Takes 3s
        vars = valid_echamham_variable_1, valid_echamham_variable_2
        filename = valid_echamham_filename
        sample_file = valid_cis_ungridded_output_filename
        sample_var = valid_cis_ungridded_output_variable
        collocator_and_opts = 'nn,variable=%s' % sample_var
        arguments = ['col', ",".join(vars) + ':' + escape_colons(filename),
                     escape_colons(sample_file) + ':collocator=' + collocator_and_opts,
                     '-o', self.OUTPUT_FILENAME]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
        self.check_output_contains_variables(self.OUTPUT_FILENAME, vars)
        self.check_output_col_grid(sample_file, sample_var, self.OUTPUT_FILENAME, vars)


if __name__ == '__main__':
    unittest.main()
