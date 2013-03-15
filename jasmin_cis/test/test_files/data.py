'''
Module that contains various strings that are used in tests
'''

import os

def make_pathname(filename):
    return os.path.join(os.path.dirname(__file__), filename)

valid_hdf_vd_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_hdf_sd_file = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")

valid_modis_l2_filename = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")
valid_modis_l2_variable = 'Asymmetry_Factor_Average_Ocean'

valid_modis_l3_filename = make_pathname("MOD08_E3.A2010009.005.2010026072315.hdf")
valid_modis_l3_variable = "Pressure_Level"

valid_cloudsat_RVOD_file = make_pathname("2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
valid_cloudsat_RVOD_variable = "RVOD_liq_water_content"

valid_aerosol_cci_filename = make_pathname("20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc")
valid_aerosol_cci_variable = "AOD550"
valid_cloud_cci_filename = make_pathname("20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc")
valid_cloud_cci_variable = "stemp"

valid_aeronet_filename = make_pathname("920801_091128_Agoufou_small.lev20")
another_valid_aeronet_filename = make_pathname("920801_091128_Abracos_Hill_small.lev20")
valid_aeronet_variable = "AOT_440"

valid_caliop_l2_filename = make_pathname("CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_caliop_l2_variable = "Tropopause_Temperature"

valid_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_second_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2010-01-01T00-22-28ZD.hdf")
valid_caliop_l1_variable = "Tropopause_Temperature"

valid_xenida_filename = make_pathname("xenida.pah9440.nc")
valid_xenida_variable = "mass_fraction_of_cloud_liquid_water_in_air"

valid_1d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.vprof.tm.nc")
valid_2d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.col.tm.nc")

valid_cis_col_file = make_pathname("cis-col-Agoufou_seasonal_average.nc")

valid_ascii_filename = make_pathname("my_dummy_points_with_values.txt")
ascii_filename_with_no_values = make_pathname("my_dummy_points.txt")
valid_ascii_variable = 0

valid_NCAR_NetCDF_RAF_filename = make_pathname("RF04.20090114.192600_035100.PNI.nc")
valid_NCAR_NetCDF_RAF_variable = 'ATX'

test_directory = make_pathname('test_directory_for_parser')
test_directory_file1 = test_directory + "/test_file_for_parser_1"
test_directory_file2 = test_directory + "/test_file_for_parser_2"
test_directory_file3 = test_directory + "/test_file_for_parser_3"
test_directory_files = [test_directory_file1, test_directory_file2, test_directory_file3]

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