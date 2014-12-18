'''
Module that contains various strings that are used in tests
'''
from collections import namedtuple
from datetime import datetime

import os

# A dictionary of test file tuples indexed by characteristic name
cis_test_files = {}

# values are None for not applicable
TestFileTestData = namedtuple('TestFile',
                      ["master_filename",
                       "file_format",
                       "product_name",
                       "start_datetime",
                       "end_datetime",
                       "lat_min",
                       "lat_max",
                       "lon_min",
                       "lon_max",
                       "valid_vars_count",
                       "all_variable_names",
                       "data_variable_name",
                       "data_variable_properties"])

def make_pathname(filename):
    return os.path.join(os.path.dirname(__file__), filename)

valid_hdf_vd_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_hdf_sd_file = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")

valid_modis_l2_filename = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")
valid_modis_l2_variable = 'Asymmetry_Factor_Average_Ocean'

valid_modis_l3_filename = make_pathname("MOD08_E3.A2010009.005.2010026072315.hdf")
valid_modis_l3_variable = "Pressure_Level"

cloudsat_file_format = "HDF4/CloudSat"
valid_cloudsat_RVOD_file = make_pathname("2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
valid_cloudsat_RVOD_sdata_variable = "RVOD_liq_water_content"
valid_cloudsat_RVOD_vdata_variable = "RVOD_ice_water_path"
valid_cloudsat_RVOD_file_format = cloudsat_file_format

valid_cloudsat_PRECIP_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_cloudsat_PRECIP_variable = "Precip_rate"
valid_cloudsat_PRECIP_file_format = cloudsat_file_format

valid_aerosol_cci_filename = make_pathname("20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc")
valid_aerosol_cci_variable = "AOD550"
valid_aerosol_cci_variable_2 = "AOD870"

valid_cloud_cci_filename = make_pathname("20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc")
valid_cloud_cci_variable = "stemp"
valid_cloud_cci_8_bit_variable = "illum"

valid_hadgem_filename = make_pathname('HadGEM_AOT550.nc')
valid_hadgem_variable = 'od550aer'

valid_aeronet_filename = make_pathname("920801_091128_Agoufou_small.lev20")
another_valid_aeronet_filename = make_pathname("920801_091128_Abracos_Hill_small.lev20")
valid_aeronet_variable = "AOT_440"

valid_caliop_l2_filename = make_pathname("CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_caliop_l2_variable = "Tropopause_Temperature"

valid_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_second_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2010-01-01T00-22-28ZD.hdf")
valid_caliop_l1_variable = "Tropopause_Temperature"

valid_echamham_filename = make_pathname("ECHAMHAM_AOT550_670.nc")
valid_echamham_variable_1 = "TAU_2D_550nm"
valid_echamham_variable_2 = "TAU_2D_670nm"

valid_xenida_filename = make_pathname("xenida.pah9440.nc")
valid_xenida_variable = "specific_humidity"

valid_1d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.vprof.tm.nc")
valid_1d_variable = "q"
valid_2d_filename = make_pathname("xglnwa.pm.k8dec-k9nov.col.tm.nc")

cis_test_files["2D_GRIDDED"] = TestFileTestData(
    master_filename=valid_2d_filename,
    file_format="NetCDF",
    product_name="defaultNetCDF",
    start_datetime=None,
    end_datetime=None,
    lat_min=None,
    lat_max=None,
    lon_min=None,
    lon_max=None,
    valid_vars_count=None,
    all_variable_names=None,
    data_variable_name=None,
    data_variable_properties=None
    )

valid_cis_col_file = make_pathname("cis-col-latlon-renamed.nc")
valid_cis_col_variable = 'AOT_440'

valid_cis_gridded_output_filename = make_pathname("subset-gridded-out.nc")
valid_cis_gridded_output_variable = 'TAU_2D_550nm'

valid_cis_ungridded_output_filename = make_pathname('cis-subset-ungridded-out.nc')
valid_cis_ungridded_output_variable = 'AOD550'

valid_ascii_filename = make_pathname("my_dummy_points_with_values.txt")
ascii_filename_with_no_values = make_pathname("my_dummy_points.txt")
valid_ascii_variable = 0

dummy_cis_out = make_pathname('out.nc')

valid_NCAR_NetCDF_RAF_filename = make_pathname("RF04.20090114.192600_035100.PNI.nc")
valid_NCAR_NetCDF_RAF_variable = 'ATX'

cis_test_files["NCAR_NetCDF_RAF"] = TestFileTestData(
    master_filename=make_pathname("RF04.20090114.192600_035100.PNI.nc"),
    file_format="NetCDF/NCAR-RAF/nimbus/1.3",
    product_name="NCAR_NetCDF_RAF",
    start_datetime=datetime(2009, 1, 14, 19, 26, 00),
    end_datetime=datetime(2009, 1, 15, 3, 51, 30),
    lat_min=29.4966,
    lat_max=31.0048,
    lon_min=20,
    lon_max=62,
#    alt_min=20.5,
#    alt_max=3678.5,
    valid_vars_count=117,
    all_variable_names=None,
    data_variable_name='ATX',
    data_variable_properties={
        "units": "ng/kg",
        "missing_value": -9999}
    )


valid_GASSP_aeroplane_filename = make_pathname("SP2_mrg60_NP3_20060927_R1.ict.nc")
valid_GASSP_aeroplane_vars = ['BC_ng_kg', "BC_ng_m3", "UTC_mid", "GpsAlt", "GpsLat", "GpsLon"]
valid_GASSP_aeroplane_variable = valid_GASSP_aeroplane_vars[0]

cis_test_files["GASSP_aeroplane"] = TestFileTestData(
    master_filename=valid_GASSP_aeroplane_filename,
    file_format="NetCDF/GASSP/1.0",
    product_name="NCAR_NetCDF_RAF",
    start_datetime=datetime(2006, 9, 27, 18, 43, 30),
    end_datetime=datetime(2006, 9, 27, 23, 53, 30),
    lat_min=29.4966,
    lat_max=31.0048,
    lon_min=-96.0271,
    lon_max=-93.4528,
#    alt_min=20.5,
#    alt_max=3678.5,
    all_variable_names=valid_GASSP_aeroplane_vars,
    valid_vars_count=len(valid_GASSP_aeroplane_vars),
    data_variable_name=valid_GASSP_aeroplane_variable,
    data_variable_properties={
        "units": "ng/kg",
        "missing_value": -9999}
    )


cis_test_files["GASSP_ship"] = TestFileTestData(
    master_filename=make_pathname("AMSpmel_RHB_20081020_R0.ict.nc"),
    file_format="NetCDF/GASSP/1.0",
    product_name="NCAR_NetCDF_RAF",
    start_datetime=datetime(2008, 10, 23, 00, 00, 00),
    end_datetime=datetime(2008, 10, 27, 00, 00, 00),
    lat_min=29.4966,
    lat_max=31.0048,
    lon_min=-96.0271,
    lon_max=-93.4528,
#    alt_min=20.5,
#    alt_max=3678.5,
    all_variable_names=['NRno3', "Start_UTC", "LAT_Deg", "LONGT_Deg", "NRso4", "NRpom", "NRnh4"],
    valid_vars_count=7,
    data_variable_name='NRno3',
    data_variable_properties=None
)

valid_GASSP_attribute = 'Time_Coordinate'



cis_test_files["GASSP_station"] = TestFileTestData(
    master_filename=make_pathname("TrinidadHead.US6005G.20110101.20140222.aerosol_number_concentration.aerosol.1y.1h."
    "US06L_TSI_3760_THD.US06L_cpc_ref.nas.txt.nc"),
    file_format="NetCDF/GASSP/1.0",
    product_name="NCAR_NetCDF_RAF",
    start_datetime=datetime(2008, 10, 23, 00, 00, 00),
    end_datetime=datetime(2008, 10, 27, 00, 00, 00),
    lat_min=29.4966,
    lat_max=31.0048,
    lon_min=-96.0271,
    lon_max=-93.4528,
#    alt_min=20.5,
#    alt_max=3678.5,
    all_variable_names=['aerosol_number_concentration',
     "start_time",
     "end_time",
     "aerosol_number_concentration_statistics_percentile_84.13",
     "aerosol_number_concentration_statistics_percentile_15.87",
     "numflag"],
    valid_vars_count=6,
    data_variable_name='aerosol_number_concentration',
    data_variable_properties=None
    )

valid_GASSP_station_filename = cis_test_files["GASSP_ship"].master_filename
valid_GASSP_station_vars =cis_test_files["GASSP_ship"].all_variable_names

valid_zonal_time_mean_CMIP5_filename = \
    make_pathname('rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.CMIP5.tm.zm.nc')
valid_zonal_time_mean_CMIP5_variable = "rsutcs"

valid_hybrid_pressure_filename = make_pathname('hybrid-pressure.nc')
valid_hybrid_pressure_variable = 'mass_fraction_of_black_carbon_dry_aerosol_in_air'

valid_hybrid_height_filename = make_pathname('hybrid-height.nc')
valid_hybrid_height_variable = 'mass_fraction_of_black_carbon_dry_aerosol_in_air'

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