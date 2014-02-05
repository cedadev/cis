"""
Module to do integration tests of plots to files. Does not check the graph created is correct, only that a graph is
created without errors.
"""

from nose.tools import istest
from jasmin_cis.cis import plot_cmd, col_cmd
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *


@istest
def should_do_scatter_plot_of_file_valid_aerosol_cci_file():
    # Actual file name: 20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc
    arguments = ['plot', valid_aerosol_cci_variable+':'+valid_aerosol_cci_filename, '--output',
                 valid_aerosol_cci_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_aerosol_cci_filename+'.png')

@istest
def should_do_contour_plot_of_valid_aerosol_cci_file():
    # Actual file name: 20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc
    # Trac issue #98
    arguments = ['plot', valid_aerosol_cci_variable+':'+valid_aerosol_cci_filename, '--output',
                 valid_aerosol_cci_filename+'.png', '--type', 'contour']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_aerosol_cci_filename+'.png')


@istest
def should_do_contourf_plot_of_valid_aerosol_cci_file():
    # Actual file name: 20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc
    # Trac issue #98
    arguments = ['plot', valid_aerosol_cci_variable+':'+valid_aerosol_cci_filename, '--output',
                 valid_aerosol_cci_filename+'.png', '--type', 'contourf']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_aerosol_cci_filename+'.png')


@istest
def should_do_scatter_plot_of_valid_2d_file():
    # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
    arguments = ['plot', valid_1d_vairable+':'+valid_2d_filename+'::::Xglnwa', '--output', valid_2d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    #os.remove(valid_2d_filename+'.png')


@istest
def should_do_scatter_plot_of_valid_2d_file_with_x_as_lat_y_as_long():
    # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
    # Trac issue #153
    arguments = ['plot', valid_1d_vairable+':'+valid_2d_filename+'::::Xglnwa', '--xaxis', 'latitude', '--yaxis', 'longitude',
                 '--output', valid_2d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_2d_filename+'.png')


@istest
def should_do_heatmap_plot_of_valid_1d_file():
    # Actual file name: xglnwa.pm.k8dec-k9nov.vprof.tm.nc
    # Trac issue #145
    arguments = ['plot', valid_1d_vairable+':'+valid_1d_filename+'::::Xglnwa_vprof', '--output', valid_1d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_1d_filename+'.png')


@istest
def should_do_line_plot_of_valid_zonal_time_mean_cmip5_file():
    # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
    # Trac issue #130
    arguments = ['plot',
                 valid_zonal_time_mean_CMIP5_filename+':'+valid_zonal_time_mean_CMIP5_filename+'::::NetCDF_CF_Gridded',
                 '--output', valid_zonal_time_mean_CMIP5_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_zonal_time_mean_CMIP5_filename+'.png')


@istest
def should_do_colocation_and_plot_of_valid_lev20_file():
    # Actual file name:
    # Trac issue #139
    arguments = ['col', valid_lev20_filename, valid_lev20_variable+':'+valid_lev20_filename+':::nn_time',
                 '-o', 'AERONET']
    main_arguments = parse_args(arguments)
    col_cmd(main_arguments)

    arguments = ['plot', valid_lev20_variable+':'+valid_lev20_filename+'::dotted',
                 valid_lev20_variable+':'+valid_lev20_col_filename+'::dashed']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file and colocated file, will throw an OSError if file was not created
    os.remove(valid_lev20_col_filename)
    os.remove(valid_lev20_filename+'.png')
