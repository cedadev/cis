from nose import with_setup
import os
from jasmin_cis.test.test_util.mock import make_dummy_2d_ungridded_data

tmp_file = "tmp_file"

def delete_tmp_file():
    os.remove(tmp_file)

@with_setup(teardown=delete_tmp_file)
def test_write_netcdf():
    from jasmin_cis.data_io.write_netcdf import write
    data_object = make_dummy_2d_ungridded_data()
    write(data_object, tmp_file)
