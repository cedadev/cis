'''
module to test the hdf4 utility function of hdf_sd.py
'''
from nose.tools import istest, eq_

from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_sd as hdf_sd


@istest
def test_that_can_read_all_variables():
    data_dict = hdf_sd.read(valid_hdf_sd_file)
    eq_(len(data_dict),67)

@istest
def test_that_can_read_known_variables():
    data_dict = hdf_sd.read(valid_hdf_sd_file,['Latitude','Longitude'])
    eq_(len(data_dict),2)

@istest
def test_that_can_get_data():
    data_dict = hdf_sd.read(valid_hdf_sd_file)
    data = hdf_sd.get_data(data_dict['Latitude'])
    eq_(data.shape,(203,135))

@istest
def test_that_can_get_metadata_for_known_variable():
    data_dict = hdf_sd.read(valid_hdf_sd_file)
    metadata = hdf_sd.get_metadata(data_dict['Latitude'])

    eq_(metadata._name,"Latitude")
    eq_(metadata.standard_name,"latitude")
    eq_(metadata.long_name,"Geodetic Latitude")
    eq_(metadata.shape,[203, 135])
    eq_(metadata.units,"Degrees_north")
    eq_(metadata.range,[-90.0, 90.0])
    eq_(metadata.factor,1.0)
    eq_(metadata.offset,0.0)
    eq_(metadata.missing_value,-999.0)


    attr = metadata.misc
    eq_(len(attr),10)
    eq_(attr['_FillValue'],-999.0)
    eq_(attr['Parameter_Type'],"MODIS Input")
