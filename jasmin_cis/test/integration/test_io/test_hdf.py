from nose.tools import eq_, istest, raises

from jasmin_cis.data_io.hdf import __read_hdf4
from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.test.test_files.data import *


@istest
@raises(IOError)
def should_raise_io_error_with_non_hdf_file():
    __read_hdf4(valid_cloud_cci_filename, valid_cloud_cci_variable)

@istest
def test_read_hdf4():
    filename = valid_hdf_sd_file
    sds, vds = __read_hdf4(filename,['Solution_Ocean','Path_Radiance_Land','Mean_Reflectance_Land'])

    # VD variable are listed in the VD part of the tuple, but not in the SD part
    eq_(True,vds.has_key('Solution_Ocean'))
    eq_(False,sds.has_key('Solution_Ocean'))

    # SD variable are listed in the SD part of the tuple, but not in the VD part
    eq_(True,sds.has_key('Path_Radiance_Land'))
    eq_(False,vds.has_key('Path_Radiance_Land'))
    eq_(True,sds.has_key('Mean_Reflectance_Land'))
    eq_(False,vds.has_key('Mean_Reflectance_Land'))

@istest
@raises(InvalidVariableError)
def test_that_cannot_read_unknown_variables():
    filename = valid_hdf_sd_file
    sds, vds = __read_hdf4(filename,['athing','unechose','einding'])

@istest
@raises(InvalidVariableError)
def test_that_cannot_read_unknown_variables_and_valid_variables():
    filename = valid_hdf_sd_file
    sds, vds = __read_hdf4(filename,['someBizarreVariableNobodyKnowsAbout','Solution_Ocean','Path_Radiance_Land','Mean_Reflectance_Land'])
