'''
module to test the hdf4 utility function of hdf_vd.py
'''
from nose.tools import istest, eq_

from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_vd as hdf_vd


@istest
def test_that_can_read_all_variables():
    dict = hdf_vd.get_hdf_VD_file_variables(valid_hdf_vd_file)
    eq_(len(dict),37)
    eq_(True,dict.has_key('Longitude'))

@istest
def test_that_can_get_data():
    vds_dict = hdf_vd.read(valid_hdf_vd_file,'DEM_elevation')
    vds = vds_dict['DEM_elevation']
    data = hdf_vd.get_data(vds)
    eq_(37081,len(data))

@istest
def test_that_can_get_metadata():
    vd = hdf_vd.read(valid_hdf_vd_file,'DEM_elevation')['DEM_elevation']
    metadata = hdf_vd.get_metadata(vd)
    eq_(metadata._name,"DEM_elevation")
    # No standard name, so gets _name by default
    eq_(metadata.standard_name,"DEM_elevation")
    eq_(metadata.long_name,"Digital Elevation Map")
    eq_(metadata.shape,[37081])
    eq_(metadata.units,"meters")
    eq_(metadata.range,[-9999, 8850])
    eq_(metadata.factor,1.0)
    eq_(metadata.offset,0.0)
    eq_(metadata.missing_value,9999)

    vd = hdf_vd.read(valid_hdf_vd_file,'Longitude')['Longitude']
    metadata = hdf_vd.get_metadata(vd)
    eq_(metadata._name,"Longitude")
    eq_(metadata.standard_name,"longitude")
    eq_(metadata.long_name,"Spacecraft Longitude")
    eq_(metadata.shape,[37081])
    eq_(metadata.units,"degrees")
    eq_(metadata.range,[-180.0, 180.0])
    eq_(metadata.factor,1.0)
    eq_(metadata.offset,0.0)
    eq_(metadata.missing_value,None)