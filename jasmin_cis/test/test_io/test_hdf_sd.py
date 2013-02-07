'''
module to test the hdf4 utility function of hdf_sd.py
'''
from nose.tools import istest,raises, eq_
from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_sd as hdf_sd
import numpy as np

@istest
def test_that_can_read_all_variables():
    dict = hdf_sd.read(valid_hdf_sd_file)
    eq_(len(dict),67)

@istest
def test_that_can_read_known_variables():
    dict = hdf_sd.read(valid_hdf_sd_file,['Latitude','Longitude'])
    eq_(len(dict),2)

@istest
def test_that_can_get_data():
    dict = hdf_sd.read(valid_hdf_sd_file)
    data = hdf_sd.get_data(dict['Latitude'])
    eq_(data.shape,(203,135))

@istest
def test_that_can_get_metadata_for_known_variable():
    dict = hdf_sd.read(valid_hdf_sd_file)
    metadata = hdf_sd.get_metadata(dict['Latitude'])
    eq_(len(metadata),3)

    info = metadata['info']
    eq_(len(info),5)

    attr = metadata['attributes']
    eq_(len(attr),10)
    eq_(attr['_FillValue'],-999.0)
    eq_(attr['Parameter_Type'],"MODIS Input")
    eq_(attr['long_name'],"Geodetic Latitude")
    eq_(attr['units'],"Degrees_north")
    eq_(attr['valid_range'],[-90.0, 90.0])
