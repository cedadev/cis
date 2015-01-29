import unittest
import os

from jasmin_cis.test.util.mock import make_dummy_2d_ungridded_data
from jasmin_cis.test.test_files.data import make_pathname, valid_cloud_cci_8_bit_variable, valid_cloud_cci_filename


tmp_file = "tmp_file"


class TestWriteNetcdf(unittest.TestCase):

    def tearDown(self):
        os.remove(tmp_file)

    def test_write_netcdf(self):
        from jasmin_cis.data_io.write_netcdf import write
        data_object = make_dummy_2d_ungridded_data()
        write(data_object, tmp_file)

    def test_write_col_and_reload_1(self):
        # Copy a colocated file and try to reload it.  This exposes a bug where
        # var.shape is set in the NetCDF metadata
        from jasmin_cis.data_io.write_netcdf import write
        from jasmin_cis.data_io.products import Aerosol_CCI
        import netCDF4 as nc

        prod = Aerosol_CCI()
        data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
        write(data_object, tmp_file)

        d = nc.MFDataset([tmp_file], aggdim='pixel_number')

        v = d.variables['AOT_440']

        # This will fail because var.shape is in the file
        print v[:2]

    def test_write_col_and_reload_2(self):
        # Copy a colocated file and try to reload it.  This exposes a bug where
        # latitude and longitude aren't recognised on reload
        from jasmin_cis.data_io.write_netcdf import write
        from jasmin_cis.data_io.products import Aerosol_CCI

        prod = Aerosol_CCI()
        data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
        write(data_object, tmp_file)

        data_object2 = prod.create_data_object([tmp_file], 'AOT_440')