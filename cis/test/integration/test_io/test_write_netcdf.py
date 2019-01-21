import unittest
import os
from netCDF4 import Dataset

from cis.data_io.gridded_data import make_from_cube, GriddedDataList
from cis.test.util.mock import make_dummy_2d_ungridded_data, make_mock_cube
from cis.test.integration_test_data import valid_cis_col_file, valid_cis_col_variable
from cis.data_io.write_netcdf import write

tmp_file = "tmp_file.nc"


class TestWriteNetcdf(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, 'd') and self.d.isopen():
            self.d.close()
        os.remove(tmp_file)

    def test_write_netcdf(self):
        data_object = make_dummy_2d_ungridded_data()
        write(data_object, tmp_file)

    def test_write_col_and_reload_1(self):
        # Copy a collocated file and try to reload it.  This exposes a bug where
        # var.shape is set in the NetCDF metadata
        from cis.data_io.products import Aerosol_CCI_L2

        prod = Aerosol_CCI_L2()
        data_object = prod.create_data_object([valid_cis_col_file], valid_cis_col_variable)
        write(data_object, tmp_file)

        self.d = Dataset(tmp_file)

        v = self.d.variables['AOT_440']

        # This will fail because var.shape is in the file
        print(v[:2])

    def test_write_col_and_reload_2(self):
        # Copy a collocated file and try to reload it.  This exposes a bug where
        # latitude and longitude aren't recognised on reload
        from cis.data_io.products import cis

        prod = cis()
        data_object = prod.create_data_object([valid_cis_col_file], valid_cis_col_variable)
        write(data_object, tmp_file)

        data_object2 = prod.create_data_object([tmp_file], valid_cis_col_variable)

    def test_ungridded_write_attributes(self):
        data = make_dummy_2d_ungridded_data()
        attrs = {'attr_name': 'attr_val',
                 'standard_name': 'std_val',
                 'long_name': 'lg_val',
                 'units': 'units'}
        data.add_attributes(attrs)
        write(data, tmp_file)
        self.d = Dataset(tmp_file)
        for key, val in attrs.items():
            assert getattr(self.d.variables['rainfall_flux'], key) == val

    def test_gridded_write_attributes(self):
        data = make_from_cube(make_mock_cube())
        data.var_name = 'rain'
        attrs = {'attr_name': 'attr_val',
                 'standard_name': 'convective_rainfall_amount',
                 'long_name': 'lg_val',
                 'units': 'units'}
        data.add_attributes(attrs)
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        for key, val in attrs.items():
            assert getattr(self.d.variables['rain'], key) == val

    def test_ungridded_write_units(self):
        data = make_dummy_2d_ungridded_data()
        data.units = 'kg'
        write(data, tmp_file)
        self.d = Dataset(tmp_file)
        assert self.d.variables['rainfall_flux'].units == 'kg'

    def test_gridded_write_units(self):
        data = make_from_cube(make_mock_cube())
        data.var_name = 'rain'
        data.units = 'ppm'
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        assert self.d.variables['rain'].units == 'ppm'

    def test_gridded_write_time_as_unlimited_dimension(self):
        data = make_from_cube(make_mock_cube(time_dim_length=7))
        data.var_name = 'rain'
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        assert self.d.dimensions['time'].isunlimited()

    def test_gridded_write_no_time_has_no_unlimited_dimension(self):
        data = make_from_cube(make_mock_cube())
        data.var_name = 'rain'
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        for d in self.d.dimensions.values():
            assert not d.isunlimited()

    def test_gridded_list_write_time_as_unlimited_dimension(self):
        data = GriddedDataList([make_from_cube(make_mock_cube(time_dim_length=7))])
        data[0].var_name = 'rain'
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        assert self.d.dimensions['time'].isunlimited()

    def test_gridded_list_write_no_time_has_no_unlimited_dimension(self):
        data = GriddedDataList([make_from_cube(make_mock_cube())])
        data[0].var_name = 'rain'
        data.save_data(tmp_file)
        self.d = Dataset(tmp_file)
        for d in self.d.dimensions.values():
            assert not d.isunlimited()

    # def test_can_write_hierarchical_group_variables(self):
    #     from cis.test.integration_test_data import valid_nested_groups_file
    #     from cis import read_data
    #     from hamcrest import assert_that, is_
    #     var_name = 'group1/group2/var4'
    #     data = read_data(valid_nested_groups_file, var_name, product='cis')
    #     assert_that(data.data, is_([12321]))
    #     data.save_data(tmp_file)
    #     self.d = Dataset(tmp_file)
    #     assert_that(self.d.variables[var_name][:], is_([12321]))
