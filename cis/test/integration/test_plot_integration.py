"""
Module to do integration tests of plots to files. Does not check the graph created is correct, only that a graph is
created without errors.
"""
from cis.exceptions import UserPrintableException
from cis.cis_main import plot_cmd, subset_cmd, aggregate_cmd
from cis.parse import parse_args
from cis.test.integration_test_data import *
from cis.test.integration.base_integration_test import BaseIntegrationTest
from nose.tools import raises


class TestPlotIntegration(BaseIntegrationTest):

    def test_should_do_scatter_plot_of_file_valid_aerosol_cci_file(self):
        # Actual file name: 20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc
        arguments = ['plot', valid_aerosol_cci_variable+':'+escape_colons(valid_aerosol_cci_filename), '--output',
                     valid_aerosol_cci_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_aerosol_cci_filename+'.png')

    def test_should_do_scatter_plot_of_valid_2d_file(self):
        # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
        arguments = ['plot', valid_1d_variable+':'+escape_colons(valid_2d_filename), '--output', valid_2d_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_2d_filename+'.png')

    def test_should_do_scatter_plot_of_valid_2d_file_with_x_as_lat_y_as_long(self):
        # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
        # Trac issue #153
        arguments = ['plot', valid_1d_variable+':'+escape_colons(valid_2d_filename), '--xaxis', 'latitude', '--yaxis', 'longitude',
                     '--output', valid_2d_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_2d_filename+'.png')

    def test_should_do_heatmap_plot_of_valid_1d_file(self):
        # Actual file name: xglnwa.pm.k8dec-k9nov.vprof.tm.nc
        # Trac issue #145
        arguments = ['plot', valid_1d_variable+':'+escape_colons(valid_1d_filename), '--output',
                     valid_1d_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_1d_filename+'.png')

    def test_should_do_line_plot_of_valid_zonal_time_mean_cmip5_file(self):
        # Actual file name: rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.CMIP5.tm.zm.nc
        # Trac issue #130
        arguments = ['plot',
                     valid_zonal_time_mean_CMIP5_variable+':'+escape_colons(valid_zonal_time_mean_CMIP5_filename),
                     '--output', valid_zonal_time_mean_CMIP5_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_zonal_time_mean_CMIP5_filename+'.png')

    def test_should_do_plot_of_hybrid_height_when_formula_terms_not_marked_as_coordinates(self):
        # Actual file name: hybrid-height.nc
        # Trac issue #417 (fixed in IRIS v.1.7.1)
        arguments = ['plot', valid_hybrid_height_flat_variable+':'+escape_colons(valid_hybrid_height_flat_filename),
                     '--output', valid_hybrid_height_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_hybrid_height_filename+'.png')

    def test_should_do_plot_of_hybrid_pressure_using_calculated_air_pressure_variable(self):
        # Actual file name: hybrid-pressure.nc
        # Trac issue #416 (fixed in IRIS v.1.7.1)
        arguments = ['plot', valid_hybrid_pressure_variable+':'+escape_colons(valid_hybrid_pressure_filename),
                     '--xaxis', 'air_pressure', '--output', valid_hybrid_pressure_filename+'.png']
        main_arguments = parse_args(arguments)
        plot_cmd(main_arguments)

        # Remove plotted file, will throw an OSError if file was not created
        os.remove(valid_hybrid_pressure_filename+'.png')

    def test_subset_ECHAM_over_0_360_boundary_plots_OK(self):
        var = valid_echamham_variable_1
        filename = valid_echamham_filename
        args = ['subset', var + ':' + escape_colons(filename) + ":product=NetCDF_Gridded", 'x=[-10,10]', '-o', self.OUTPUT_FILENAME]
        args = parse_args(args)
        subset_cmd(args)
        out_name = 'subset_echam_boundary.png'
        args = ['plot', var + ":" + self.OUTPUT_FILENAME + ":product=NetCDF_Gridded", '--type', 'contourf', '-o', out_name]
        args = parse_args(args)
        plot_cmd(args)

        os.remove(out_name)

    @raises(ValueError)
    def test_plot_gridded_3d_exits_with_ValueError(self):
        variable = valid_cis_gridded_output_variable
        filename = valid_cis_gridded_output_filename
        out_name = '3d_out.png'
        args = ['plot', variable + ':' + escape_colons(filename) + ":product=NetCDF_Gridded", '-o', out_name]
        main_arguments = parse_args(args)
        plot_cmd(main_arguments)

    def test_plot_gridded_2d_with_flattened_time(self):
        variable = valid_cis_gridded_output_variable
        filename = valid_cis_gridded_output_filename
        args = ['subset', variable + ':' + escape_colons(filename) + ":product=NetCDF_Gridded",
                't=[2007-06-07T15]', '-o', self.OUTPUT_FILENAME]
        args = parse_args(args)
        subset_cmd(args)
        out_name = '3d_out.png'
        args = ['plot', variable + ':' + self.OUTPUT_FILENAME + ":product=NetCDF_Gridded", '-o', out_name]
        main_arguments = parse_args(args)
        plot_cmd(main_arguments)

        os.remove(out_name)

    def test_plot_aggregated_aeronet(self):
        # Aggregated aeronet has multiple length 1 dimensions, so we want to make sure we can plot it OK.
        # JASCIS-183
        variable = 'Solar_Zenith_Angle'
        filename = valid_aeronet_filename
        agg_args = ['aggregate', variable + ':' + escape_colons(filename),
                    't=[2003-09-24T07:00:00,2003-11-04T07:00:00,P1D]', '-o', self.OUTPUT_FILENAME]
        args = parse_args(agg_args)
        aggregate_cmd(args)
        out_name = 'aeronet_out.png'
        args = ['plot', variable + ':' + self.OUTPUT_FILENAME,
                '--xaxis', 'time', '--yaxis', variable, '-o', out_name]
        main_arguments = parse_args(args)
        plot_cmd(main_arguments)

        os.remove(out_name)

    def test_plot_ungridded_histogram(self):
        filename = valid_GASSP_station_filename
        variable = valid_GASSP_station_vars[0]
        out_name = 'histogram.png'
        args = ['plot', variable + ':' + escape_colons(filename), '--type', 'histogram', '-o', out_name]
        args = parse_args(args)
        plot_cmd(args)

        os.remove(out_name)

    @raises(UserPrintableException)
    def test_plot_ungridded_heatmap(self):
        filename = valid_GASSP_station_filename
        variable = valid_GASSP_station_vars[0]
        args = ['plot', variable + ':' + escape_colons(filename), '--type', 'heatmap']
        args = parse_args(args)
        plot_cmd(args)

    def test_plot_heatmap_horizontal_cbar(self):
        var = valid_echamham_variable_1
        filename = valid_echamham_filename
        out_name = 'cbarh.png'
        args = ['plot', var + ':' + escape_colons(filename), '--cbarorient', 'horizontal', '-o', out_name]
        args = parse_args(args)
        plot_cmd(args)

        os.remove(out_name)

    def test_plot_heatmap_vertical_cbar(self):
        var = valid_echamham_variable_1
        filename = valid_echamham_filename
        out_name = 'cbarv.png'
        args = ['plot', var + ':' + escape_colons(filename), '--cbarorient', 'vertical', '-o', out_name]
        args = parse_args(args)
        plot_cmd(args)

        os.remove(out_name)

    def test_plot_heatmap_cbar_scale(self):
        var = valid_echamham_variable_1
        filename = valid_echamham_filename
        out_name = 'cbarscale.png'
        args = ['plot', var + ':' + escape_colons(filename), '--cbarscale', '0.75', '-o', out_name]
        args = parse_args(args)
        plot_cmd(args)

        os.remove(out_name)
