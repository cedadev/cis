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

    eq_(metadata['name'],"Latitude")
    eq_(metadata['long_name'],"Geodetic Latitude")
    eq_(metadata['shape'],[203, 135])
    eq_(metadata['units'],"Degrees_north")
    eq_(metadata['range'],[-90.0, 90.0])
    eq_(metadata['factor'],1.0)
    eq_(metadata['offset'],0.0)
    eq_(metadata['missing'],-999.0)


    attr = metadata['misc']
    eq_(len(attr),10)
    eq_(attr['_FillValue'],-999.0)
    eq_(attr['Parameter_Type'],"MODIS Input")
