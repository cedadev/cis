'''
module to test the NetCDF module
'''
from nose.tools import istest,raises, eq_
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.netcdf import *

@istest
def test_that_can_read_all_variables():
    dict = read(valid_2d_filename)
    eq_(len(dict),426)

@istest
def test_that_can_read_known_variables():
    dict = read(valid_2d_filename,['latitude','longitude'])
    eq_(len(dict),2)

@istest
def test_that_can_get_data():
    dict = read(valid_2d_filename)
    data = get_data(dict['latitude'])
    eq_(data.shape,(145,))

@istest
def test_that_can_get_metadata_for_known_variable():
    import math
    dict = read(valid_2d_filename)
    metadata = get_metadata(dict['rain'])
    eq_(len(metadata),3)

    info = metadata['info']

    attr = metadata['attributes']
    eq_(len(attr),9)
    eq_(str(attr['_FillValue']),"2e+20")
    eq_(attr['long_name'],"TOTAL RAINFALL RATE: LS+CONV KG/M2/S")
    eq_(attr['units'],"kg m-2 s-1")
    eq_(attr['source'],"Unified Model Output (Vn 7.3):")
