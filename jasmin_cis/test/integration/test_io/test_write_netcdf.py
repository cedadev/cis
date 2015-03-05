import unittest
import os
from netCDF4 import Dataset
from data_io.gridded_data import make_from_cube

from jasmin_cis.test.util.mock import make_dummy_2d_ungridded_data, make_mock_cube
from jasmin_cis.test.test_files.data import make_pathname
from jasmin_cis.data_io.write_netcdf import write

tmp_file = "tmp_file.nc"


class TestWriteNetcdf(unittest.TestCase):

    def tearDown(self):
        os.remove(tmp_file)

    def test_write_netcdf(self):
        data_object = make_dummy_2d_ungridded_data()
        write(data_object, tmp_file)

    def test_write_col_and_reload_1(self):
        # Copy a colocated file and try to reload it.  This exposes a bug where
        # var.shape is set in the NetCDF metadata
        from jasmin_cis.data_io.products import Aerosol_CCI

        prod = Aerosol_CCI()
        data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
        write(data_object, tmp_file)

        d = Dataset(tmp_file)

        v = d.variables['AOT_440']

        # This will fail because var.shape is in the file
        print v[:2]

    def test_write_col_and_reload_2(self):
        # Copy a colocated file and try to reload it.  This exposes a bug where
        # latitude and longitude aren't recognised on reload
        from jasmin_cis.data_io.products import cis

        prod = cis()
        data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
        write(data_object, tmp_file)

        data_object2 = prod.create_data_object([tmp_file], 'AOT_440')

    def test_ungridded_write_attributes(self):
        data = make_dummy_2d_ungridded_data()
        attrs = {'attr_name': 'attr_val',
                 'standard_name': 'std_val',
                 'long_name': 'lg_val',
                 'units': 'units'}
        data.add_attributes(attrs)
        write(data, tmp_file)
        d = Dataset(tmp_file)
        for key, val in attrs.iteritems():
            assert getattr(d.variables['rain'], key) == val

    def test_gridded_write_attributes(self):
        data = make_from_cube(make_mock_cube())
        data.var_name = 'rain'
        attrs = {'attr_name': 'attr_val',
                 'standard_name': 'convective_rainfall_amount',
                 'long_name': 'lg_val',
                 'units': 'units'}
        data.add_attributes(attrs)
        data.save_data(tmp_file)
        d = Dataset(tmp_file)
        for key, val in attrs.iteritems():
            assert getattr(d.variables['rain'], key) == val

    def test_ungridded_write_units(self):
        data = make_dummy_2d_ungridded_data()
        data.units = 'kg'
        write(data, tmp_file)
        d = Dataset(tmp_file)
        assert d.variables['rain'].units == 'kg'

    def test_gridded_write_units(self):
        data = make_from_cube(make_mock_cube())
        data.var_name = 'rain'
        data.units = 'ppm'
        data.save_data(tmp_file)
        d = Dataset(tmp_file)
        assert d.variables['rain'].units == 'ppm'
