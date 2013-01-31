'''
module to test the hdf4 utility function of hdf_vd.py
'''
from nose.tools import istest, eq_
from jasmin_cis.test.test_files.data import *
import jasmin_cis.data_io.hdf_vd as hdf_vd


@istest
def test_that_can_read_all_variables():
    filename = valid_hdf_vd_file
    dict = hdf_vd.get_hdf_VD_file_variables(filename)
    eq_(len(dict),37)
    eq_(True,dict.has_key('Longitude'))

@istest
def test_that_can_get_data():
    filename = valid_hdf_vd_file
    vds_dict = hdf_vd.read_vds(filename,['DEM_elevation'])
    vds = vds_dict['DEM_elevation']
    data = hdf_vd.get_data(vds)
    eq_(37081,len(data))
