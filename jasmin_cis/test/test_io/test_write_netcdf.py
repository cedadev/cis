from nose import with_setup
import os
from jasmin_cis.test.test_util.mock import make_dummy_2d_ungridded_data
from jasmin_cis.test.test_files.data import make_pathname

tmp_file = "tmp_file"

def delete_tmp_file():
    os.remove(tmp_file)

@with_setup(teardown=delete_tmp_file)
def test_write_netcdf():
    from jasmin_cis.data_io.write_netcdf import write
    data_object = make_dummy_2d_ungridded_data()
    write(data_object, tmp_file)


@with_setup(teardown=delete_tmp_file)
def test_write_col_and_reload_1():
    # Copy a colocated file and try to reload it.  This exposes a bug where
    # var.shape is set in the NetCDF metadata
    from jasmin_cis.data_io.write_netcdf import write
    from jasmin_cis.data_io.products.products import Aerosol_CCI
    import netCDF4 as nc

    prod = Aerosol_CCI()
    data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
    write(data_object, tmp_file)

    d = nc.MFDataset([tmp_file], aggdim='pixel_number')

    v = d.variables['AOT_440']

    # This will fail because var.shape is in the file
    print v[:2]


@with_setup(teardown=delete_tmp_file)
def test_write_col_and_reload_2():
    # Copy a colocated file and try to reload it.  This exposes a bug where
    # latitude and longitude aren't recognised on reload
    from jasmin_cis.data_io.write_netcdf import write
    from jasmin_cis.data_io.products.products import Aerosol_CCI
    import netCDF4 as nc

    prod = Aerosol_CCI()
    data_object = prod.create_data_object([make_pathname('cis-col-latlon-renamed.nc')], 'AOT_440')
    write(data_object, tmp_file)

    data_object2 = prod.create_data_object([tmp_file], 'AOT_440')

