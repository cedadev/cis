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
                       "data_variable_standard_name",
                       "data_variable_properties"])

def make_pathname(filename):
    return os.path.join(os.path.dirname(__file__), filename)

valid_hdf_vd_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_hdf_sd_file = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")

valid_modis_l2_filename = make_pathname("MOD04_L2.A2010001.2255.005.2010005215814.hdf")
valid_modis_l2_variable = 'Cloud_Fraction_Ocean'

valid_modis_l2_variables = \
    ['Deep_Blue_Angstrom_Exponent_Land',
     'Cloud_Fraction_Ocean',
     'Corrected_Optical_Depth_Land_wav2p1',
     'Mass_Concentration_Land',
     'Solar_Zenith',
     'Latitude',
     'Sensor_Azimuth',
     'Optical_Depth_Ratio_Small_Land_And_Ocean',
     'Sensor_Zenith',
     'Scan_Start_Time',
     'Image_Optical_Depth_Land_And_Ocean',
     'Cloud_Fraction_Land',
     'Number_Pixels_Used_Ocean',
     'Longitude',
     'Aerosol_Type_Land',
     'Cloud_Mask_QA',
     'Optical_Depth_Ratio_Small_Land',
     'Scattering_Angle',
     'Solar_Azimuth',
     'Angstrom_Exponent_Land',
     'Deep_Blue_Aerosol_Optical_Depth_550_Land',
     'Fitting_Error_Land',
     'Optical_Depth_Land_And_Ocean']
cis_test_files["modis_L2"] = TestFileTestData(
    master_filename=valid_modis_l2_filename,
    file_format="HDF4/ModisL2",
    product_name="MODIS_L2",
    start_datetime=datetime(2010, 1, 1, 22, 55, 8),
    end_datetime=datetime(2010, 1, 1, 23, 00, 6),
    lat_min=-80.405128,
    lat_max=-56.644821,
    lon_min=-179.99913,
    lon_max=179.99573,
    valid_vars_count=len(valid_modis_l2_variables),
    all_variable_names=valid_modis_l2_variables,
    data_variable_name=valid_modis_l2_variable,
    data_variable_standard_name=valid_modis_l2_variables,
    data_variable_properties={}
    )

valid_modis_l3_filename = make_pathname("MOD08_E3.A2010009.005.2010026072315.hdf")
valid_modis_l3_variable = "Solar_Zenith_Std_Deviation_Mean"
cis_test_files["modis_L3"] = TestFileTestData(
    master_filename=valid_modis_l3_filename,
    file_format="HDF4/ModisL3",
    product_name="MODIS_L3",
    start_datetime=datetime(2010, 1, 13, 0, 0, 0),
    end_datetime=datetime(2010, 1, 13, 0, 0, 0),
    lat_min=-89.5,
    lat_max=89.5,
    lon_min=-179.5,
    lon_max=179.5,
    valid_vars_count=700,
    all_variable_names=None,
    data_variable_name="Solar_Zenith_Mean_Mean",
    data_variable_standard_name="Solar_Zenith_Mean_Mean",
    data_variable_properties={}
    )

cloudsat_file_format = "HDF4/CloudSat"
valid_cloudsat_RVOD_file = make_pathname("2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf")
valid_cloudsat_RVOD_sdata_variable = "RVOD_liq_water_content"
valid_cloudsat_RVOD_vdata_variable = "RVOD_ice_water_path"
valid_cloudsat_RVOD_file_format = cloudsat_file_format

cis_test_files["CloudsatRVODsdata"] = TestFileTestData(
    master_filename=valid_cloudsat_RVOD_file,
    file_format=cloudsat_file_format,
    product_name="CloudSat",
    start_datetime=datetime(2007, 6, 29, 12, 55, 3),
    end_datetime=datetime(2007, 6, 29, 14, 33, 56),
    lat_min=-81.84876,
    lat_max=81.849,
    lon_min=-180,
    lon_max=180,
    valid_vars_count=69,
    all_variable_names=None,
    data_variable_name=valid_cloudsat_RVOD_sdata_variable,
    data_variable_standard_name=valid_cloudsat_RVOD_sdata_variable,
    data_variable_properties={}
    )

valid_cloudsat_PRECIP_file = make_pathname("2008045004519_09563_CS_2C-PRECIP-COLUMN_GRANULE_P_R04_E02.hdf")
valid_cloudsat_PRECIP_variable = "Precip_rate"
valid_cloudsat_PRECIP_file_format = cloudsat_file_format

valid_aerosol_cci_filename = make_pathname("20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc")
valid_aerosol_cci_variable = "AOD550"
valid_aerosol_cci_variable_2 = "AOD870"

cis_test_files["Aerosol_CCI"] = TestFileTestData(
    master_filename=valid_aerosol_cci_filename,
    file_format="NetCDF/Aerosol_CCI",
    product_name="Aerosol_CCI",
    start_datetime=datetime(2008, 6, 12, 10, 1, 23),
    end_datetime=datetime(2008, 6, 12, 10, 43, 37),
    lat_min=-44.91,
    lat_max=83.80,
    lon_min=-22.25,
    lon_max=160.48,
    valid_vars_count=32,
    all_variable_names=None,
    data_variable_name=valid_aerosol_cci_variable,
    data_variable_standard_name='atmosphere_optical_thickness_due_to_aerosol',
    data_variable_properties={}
    )


valid_cloud_cci_filename = make_pathname("20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc")
valid_cloud_cci_variable = "stemp"
valid_cloud_cci_8_bit_variable = "illum"

cis_test_files["Cloud_CCI"] = TestFileTestData(
    master_filename=valid_cloud_cci_filename,
    file_format="NetCDF/Cloud_CCI",
    product_name="Cloud_CCI",
    start_datetime=datetime(2007, 6, 29, 12, 55, 3),
    end_datetime=datetime(2007, 6, 29, 14, 33, 56),
    lat_min=-81.84876,
    lat_max=81.849,
    lon_min=-180,
    lon_max=180,
    valid_vars_count=30,
    all_variable_names=None,
    data_variable_name=valid_cloud_cci_variable,
    data_variable_standard_name=valid_cloud_cci_variable,
    data_variable_properties={}
    )

valid_hadgem_filename = make_pathname('od550aer.nc')
valid_hadgem_variable = 'od550aer'

valid_aeronet_filename = make_pathname("920801_091128_Agoufou_small.lev20")
another_valid_aeronet_filename = make_pathname("920801_091128_Abracos_Hill_small.lev20")
valid_aeronet_variable = "AOT_440"
all_aeronet_variables = [
    "AOT_551",
    "TripletVar_532",
    "AOT_532",
    "AOT_667",
    "AOT_531",
    "TripletVar_412",
    "440-675Angstrom(Polar)",
    "AOT_1640",
    "WaterError",
    "AOT_380",
    "500-870Angstrom",
    "Date(dd-mm-yy)",
    "AOT_412",
    "AOT_555",
    "AOT_490",
    "TripletVar_1640",
    "Solar_Zenith_Angle",
    "340-440Angstrom",
    "TripletVar_340",
    "AOT_675",
    "TripletVar_531",
    "TripletVar_380",
    "TripletVar_440",
    "TripletVar_500",
    "380-500Angstrom",
    "AOT_443",
    "AOT_440",
    "TripletVar_667",
    "440-675Angstrom",
    "Time(hh:mm:ss)",
    "TripletVar_675",
    "Julian_Day",
    "TripletVar_1020",
    "TripletVar_870",
    "TripletVar_443",
    "Water(cm)",
    "AOT_500",
    "AOT_1020",
    "440-870Angstrom",
    "AOT_870",
    "TripletVar_490",
    "Last_Processing_Date",
    "TripletVar_551",
    "AOT_340",
    "TripletVar_555"
]

cis_test_files["aeronet"] = TestFileTestData(
    master_filename=valid_aeronet_filename,
    file_format="Aeronet",
    product_name="Aeronet",
    start_datetime=datetime(2003, 9, 25, 6, 47, 9),
    end_datetime=datetime(2003, 12, 31, 9, 24, 4),
    lat_min=15.345,
    lat_max=15.345,
    lon_min=-1.479,
    lon_max=-1.479,
    valid_vars_count=len(all_aeronet_variables),
    all_variable_names=all_aeronet_variables,
    data_variable_name="AOT_440",
    data_variable_standard_name="AOT_440",
    data_variable_properties={}
    )

valid_caliop_l2_filename = make_pathname("CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_caliop_l2_variable = "Pressure"
valid_caliop_l2_variables = ['Aerosol_Layer_Fraction',
                     'Aerosol_Multiple_Scattering_Profile_1064',
                     'Aerosol_Multiple_Scattering_Profile_532',
                     'Backscatter_Coefficient_1064',
                     'Backscatter_Coefficient_Uncertainty_1064',
                     'Cloud_Layer_Fraction',
                     'Extinction_Coefficient_1064',
                     'Extinction_Coefficient_532',
                     'Extinction_Coefficient_Uncertainty_1064',
                     'Extinction_Coefficient_Uncertainty_532',
                     'Molecular_Number_Density',
                     'Particulate_Depolarization_Ratio_Profile_532',
                     'Particulate_Depolarization_Ratio_Uncertainty_532',
                     'Perpendicular_Backscatter_Coefficient_532',
                     'Perpendicular_Backscatter_Coefficient_Uncertainty_532',
                     'Pressure',
                     'Relative_Humidity',
                     'Samples_Averaged',
                     'Temperature',
                     'Total_Backscatter_Coefficient_Uncertainty_532',
                     'Total_Backscatter_Coefficient_532']
cis_test_files["caliop_L2"] = TestFileTestData(
    master_filename=valid_caliop_l2_filename,
    file_format="HDF4/CaliopL2",
    product_name="Caliop_L2",
    start_datetime=datetime(2009, 12, 31, 23, 36, 12),
    end_datetime=datetime(2010, 1, 1, 0, 22, 25),
    lat_min=-61.37,
    lat_max=81.84,
    lon_min=-179.97,
    lon_max=179.93,
    valid_vars_count=len(valid_caliop_l2_variables),
    all_variable_names=valid_caliop_l2_variables,
    data_variable_name="Cloud_Layer_Fraction",
    data_variable_standard_name="Cloud_Layer_Fraction",
    data_variable_properties={}
    )

valid_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2009-12-31T23-36-08ZN.hdf")
valid_second_caliop_l1_filename = make_pathname("CAL_LID_L1-ValStage1-V3-01.2010-01-01T00-22-28ZD.hdf")
valid_caliop_l1_variable = "Attenuated_Backscatter_1064"
valid_caliop_l1_variables = ['Perpendicular_Attenuated_Backscatter_532',
                     'Attenuated_Backscatter_1064',
                     'Total_Attenuated_Backscatter_532']
cis_test_files["caliop_L1"] = TestFileTestData(
    master_filename=valid_caliop_l1_filename,
    file_format="HDF4/CaliopL1",
    product_name="Caliop_L1",
    start_datetime=datetime(2009, 12, 31, 23, 36, 12),
    end_datetime=datetime(2010, 1, 1, 0, 22, 25),
    lat_min=-61.37,
    lat_max=81.84,
    lon_min=-179.97,
    lon_max=179.93,
    valid_vars_count=len(valid_caliop_l1_variables),
    all_variable_names=valid_caliop_l1_variables,
    data_variable_name='Perpendicular_Attenuated_Backscatter_532',
    data_variable_standard_name='Perpendicular_Attenuated_Backscatter_532',
    data_variable_properties={}
    )

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
    file_format="NetCDF/Gridded",
    product_name="defaultNetCDF",
    start_datetime=None,
    end_datetime=None,
    lat_min=None,
    lat_max=None,
    lon_min=None,
    lon_max=None,
    valid_vars_count=None,
    all_variable_names=[],
    data_variable_name="SST_1",
    data_variable_standard_name="SST_1",
    data_variable_properties=None
    )

valid_cis_col_file = make_pathname("cis-col-latlon-renamed.nc")
valid_cis_col_variable = 'AOT_440'

valid_cis_gridded_output_filename = make_pathname("subset-gridded-out.nc")
valid_cis_gridded_output_variable = 'TAU_2D_550nm'

valid_cis_ungridded_output_filename = make_pathname('cis-subset-ungridded-out.nc')
valid_cis_ungridded_output_variable = 'AOD550'
valid_cis_ungridded_output_variables = ['pixel_number', 'latitude', 'longitude', 'time', 'AOD550', 'AOD870']

cis_test_files["CIS_Ungridded"] = TestFileTestData(
    master_filename=valid_cis_ungridded_output_filename,
    file_format="NetCDF/CIS",
    product_name="cis",
    start_datetime=datetime(2008, 6, 12, 10, 18, 17),
    end_datetime=datetime(2008, 6, 12, 10, 20, 10),
    lat_min=39.07,
    lat_max=45.0,
    lon_min=0,
    lon_max=6.0,
    valid_vars_count=len(valid_cis_ungridded_output_variables),
    all_variable_names=valid_cis_ungridded_output_variables,
    data_variable_name=valid_cis_ungridded_output_variable,
    data_variable_standard_name='atmosphere_optical_thickness_due_to_aerosol',
    data_variable_properties={}
    )

valid_ascii_filename = make_pathname("my_dummy_points_with_values.txt")
ascii_filename_with_no_values = make_pathname("my_dummy_points.txt")
cis_test_files["ascii"] = TestFileTestData(
    master_filename=valid_ascii_filename,
    file_format="ASCII/ASCIIHyperpoints",
    product_name="ASCII_Hyperpoints",
    start_datetime=datetime(2012, 8, 22, 15, 32, 3),
    end_datetime=datetime(2012, 8, 29, 15, 32, 3),
    lat_min=0,
    lat_max=7,
    lon_min=-10,
    lon_max=0,
    valid_vars_count=1,
    all_variable_names=['value'],
    data_variable_name='value',
    data_variable_standard_name='value',
    data_variable_properties={}
    )


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
    data_variable_standard_name="ATX",
    data_variable_properties={
        "units": "ng/kg",
        "missing_value": -9999}
    )

# this data is not entirely correct because there is an extra 1 length dimension in it
valid_GASSP_not_entirely_correct_filename = make_pathname("ACE1_aero_an.nc")
valid_GASSP_not_entirely_correct_variable = 'TIM_627'

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
    data_variable_standard_name=valid_GASSP_aeroplane_variable,
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
    data_variable_standard_name='NRno3',
    data_variable_properties=None
)
valid_GASSP_ship_vars = cis_test_files["GASSP_ship"].all_variable_names
valid_GASSP_ship_filename = cis_test_files["GASSP_ship"].master_filename

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
    data_variable_standard_name='aerosol_number_concentration',
    data_variable_properties=None
    )

valid_GASSP_station_filename = cis_test_files["GASSP_station"].master_filename
valid_GASSP_station_vars =cis_test_files["GASSP_station"].all_variable_names

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