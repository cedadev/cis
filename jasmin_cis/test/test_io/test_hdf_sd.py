'''
module to test the hdf4 utility function of hdf_sd.py
'''
from nose.tools import istest,raises, eq_
from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_sd as hdf_sd
from pyhdf.error import HDF4Error
import numpy as np

@istest
def test_that_can_read_all_variables_from_hdf4_SD():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename)
    eq_(len(dict),67)

@istest
def test_that_can_read_known_variables_from_hdf4_SD():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename,['Latitude','Longitude'])
    eq_(len(dict),2)

    lat_sds = hdf_sd.read_hdf4_SD_variable(filename,'Latitude')
    eq_(True,np.array_equal(lat_sds.get(),dict['Latitude'].get()))

@istest
@raises(HDF4Error)
def test_that_cannot_read_unknown_variables_from_hdf4_sd():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename,['athing','unechose','einding'])

@istest
def test_that_can_get_datasets_from_hdf4_sd():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename)

    dict2 = hdf_sd.get_hdf_SD_file_variables(filename)
    eq_(set(dict.keys()),set(dict2.keys()))

@istest
def test_that_can_get_metadata_for_known_variable():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename)
    metadata = hdf_sd.read_hdf4_SD_metadata(dict['Latitude'])
    eq_(metadata[0],"Geodetic Latitude")
    eq_(metadata[1],"Degrees_north")
    eq_(metadata[2],[-90.0, 90.0])

@istest
@raises(KeyError)
def test_that_cannot_get_metadata_for_unknown_variable():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_hdf4_SD(filename)
    hdf_sd.read_hdf4_SD_metadata(dict['incognito'])
