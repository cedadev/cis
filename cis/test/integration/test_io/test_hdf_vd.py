"""
module to test the hdf4 utility function of hdf_vd.py
"""
from nose.tools import istest, eq_

import cis.data_io.hdf_vd as hdf_vd
from cis.test.integration_test_data import valid_hdf_vd_file, escape_colons, skip_pyhdf


@istest
@skip_pyhdf
def test_that_can_read_all_variables():
    dict = hdf_vd.get_hdf_VD_file_variables(escape_colons(valid_hdf_vd_file))
    eq_(len(dict), 37)
    eq_(True, 'Longitude' in dict)


@istest
@skip_pyhdf
def test_that_can_get_data():
    vds_dict = hdf_vd.read(escape_colons(valid_hdf_vd_file), 'DEM_elevation')
    vds = vds_dict['DEM_elevation']
    data = hdf_vd.get_data(vds)
    eq_(37081, len(data))


@istest
@skip_pyhdf
def test_that_can_get_variable_metadata():
    vd = hdf_vd.read(escape_colons(valid_hdf_vd_file), 'DEM_elevation')['DEM_elevation']
    metadata = hdf_vd.get_metadata(vd)
    eq_(metadata._name, "DEM_elevation")
    eq_(metadata.long_name, "Digital Elevation Map")
    eq_(metadata.shape, [37081])
    eq_(metadata.units, "meters")
    eq_(metadata.factor, 1.0)
    eq_(metadata.offset, 0.0)
    eq_(metadata.missing_value, 9999)
    eq_(metadata.misc['valid_range'], [-9999, 8850])


@istest
@skip_pyhdf
def test_that_can_get_coord_metadata():
    vd = hdf_vd.read(escape_colons(valid_hdf_vd_file), 'Longitude')['Longitude']
    metadata = hdf_vd.get_metadata(vd)
    eq_(metadata._name, "Longitude")
    eq_(metadata.standard_name, "longitude")
    eq_(metadata.long_name, "Spacecraft Longitude")
    eq_(metadata.shape, [37081])
    eq_(metadata.units, "degrees")
    eq_(metadata.factor, 1.0)
    eq_(metadata.offset, 0.0)
    eq_(metadata.missing_value, None)
    eq_(metadata.misc['valid_range'], [-180.0, 180.0])
