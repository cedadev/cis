'''
Module that contains various strings that are used in tests
'''

import os

def make_pathname(filename):
    return os.path.join(os.path.dirname(__file__), filename)

valid_hdf_vd_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_cloudsat_RVOD_file = make_pathname("2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
valid_cloudsat_RVOD_variable = "RVOD_liq_water_content"
valid_hdf_sd_file = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")
valid_1d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.vprof.tm.nc")
valid_2d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.col.tm.nc")
large_15GB_file_filename = "/run/media/daniel/Storage/xglnwa.pm.k8dec-k9nov.nc"
invalid_filename = "invalidfilename"
non_netcdf_file = make_pathname("notanetcdffile")
file_without_read_permissions = make_pathname("Unreadable Folder/xglnwa.pm.k8dec-k9nov.vprof.tm.nc")
netcdf_file_with_incorrect_file_extension = make_pathname("xglnwa.pm.k8dec-k9nov.vprof.tm.waldm")
non_netcdf_file_with_netcdf_file_extension = make_pathname("notarealnetcdffile.nc")
not1Dvariable = "u" 
valid_variable_in_valid_filename = "rain"
out_filename = "cube_image.png"
valid_colour = "green"
invalid_colour = "greenn"
valid_width = 40
valid_line_style = "dashed"
valid_colour_map = "RdBu"
invalid_colour_map = "invalid"
valid_font_size = 10
valid_height = 40
valid_ymin = 0
valid_ymax = 1