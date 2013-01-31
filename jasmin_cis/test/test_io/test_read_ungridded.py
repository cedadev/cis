'''
module to test the reading of ungridded data files
'''
from nose.tools import istest, eq_
from jasmin_cis.test.test_files.data import *
from jasmin_cis.data_io.read_ungridded import *

@istest
def test_that_can_get_coordinates_from_file():
    filename = valid_hdf_sd_file
    data = get_file_coordinates(filename)
    
    eq_(data[0].shape,data[1].shape)
    eq_(data[0].shape,(203,135))
    eq_(data[1].shape,(203,135))

def test_read_hdf4():
    filename = valid_hdf_sd_file
    sds_vds = read_hdf4(filename,['someBizarreVariableNobodyKnowsAbout','Solution_Ocean','Path_Radiance_Land','Mean_Reflectance_Land'])
    sds = sds_vds[0]
    vds = sds_vds[1]

    # VD variable are listed in the VD part of the tuple, but not in the SD part
    eq_(True,vds.has_key('Solution_Ocean'))
    eq_(False,sds.has_key('Solution_Ocean'))

    # SD variable are listed in the SD part of the tuple, but not in the VD part
    eq_(True,sds.has_key('Path_Radiance_Land'))
    eq_(False,vds.has_key('Path_Radiance_Land'))
    eq_(True,sds.has_key('Mean_Reflectance_Land'))
    eq_(False,vds.has_key('Mean_Reflectance_Land'))

    # unknown variable are not listed anywhere
    eq_(False,sds.has_key('someBizarreVariableNobodyKnowsAbout'))
    eq_(False,vds.has_key('someBizarreVariableNobodyKnowsAbout'))
