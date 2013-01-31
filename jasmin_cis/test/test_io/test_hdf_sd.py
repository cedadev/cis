'''
module to test the hdf4 utility function of hdf_sd.py
'''
from nose.tools import istest,raises, eq_
from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_sd as hdf_sd
from pyhdf.error import HDF4Error
import numpy as np

@istest
def test_that_can_read_all_variables():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename)
    eq_(len(dict),67)

@istest
def test_that_can_read_known_variables():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename,['Latitude','Longitude'])
    eq_(len(dict),2)

@istest
@raises(HDF4Error)
def test_that_cannot_read_unknown_variables():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename,['athing','unechose','einding'])

@istest
def test_that_can_get_data_from():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename)
    data = hdf_sd.get_data(dict['Latitude'])
    eq_(data.shape,(203,135))

@istest
def test_that_can_get_metadata_for_known_variable():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename)
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

@istest
@raises(KeyError)
def test_that_cannot_get_metadata_for_unknown_variable():
    filename = valid_hdf_sd_file
    dict = hdf_sd.read_sds(filename)
    hdf_sd.get_metadata(dict['incognito'])

