"""
Module to do integration tests of plots to files. Does not check the graph created is correct, only that a graph is
created without errors.
"""

from nose.tools import istest
from jasmin_cis.cis import plot_cmd
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
    arguments = ['plot', valid_1d_variable+':'+valid_2d_filename, '--output', valid_2d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    #os.remove(valid_2d_filename+'.png')


@istest
def should_do_scatter_plot_of_valid_2d_file_with_x_as_lat_y_as_long():
    # Actual file name: xglnwa.pm.k8dec-k9nov.col.tm.nc
    # Trac issue #153
    arguments = ['plot', valid_1d_variable+':'+valid_2d_filename, '--xaxis', 'latitude', '--yaxis', 'longitude',
                 '--output', valid_2d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_2d_filename+'.png')


@istest
def should_do_heatmap_plot_of_valid_1d_file():
    # Actual file name: xglnwa.pm.k8dec-k9nov.vprof.tm.nc
    # Trac issue #145
    arguments = ['plot', valid_1d_variable+':'+valid_1d_filename, '--output',
                 valid_1d_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_1d_filename+'.png')


@istest
def should_do_line_plot_of_valid_zonal_time_mean_cmip5_file():
    # Actual file name: rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.CMIP5.tm.zm.nc
    # Trac issue #130
    arguments = ['plot',
            valid_zonal_time_mean_CMIP5_variable+':'+valid_zonal_time_mean_CMIP5_filename,
                 '--output', valid_zonal_time_mean_CMIP5_filename+'.png']
    main_arguments = parse_args(arguments)
    plot_cmd(main_arguments)

    # Remove plotted file, will throw an OSError if file was not created
    os.remove(valid_zonal_time_mean_CMIP5_filename+'.png')
