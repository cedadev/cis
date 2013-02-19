from nose import with_setup
import os
from test.test_util.mock import make_dummy_2d_ungridded_data

tmp_file = "tmp_file"

def delete_tmp_file():
    os.remove(tmp_file)

@with_setup(teardown=delete_tmp_file)
def test_write_hdf():
    from jasmin_cis.data_io.write_hdf import write
    obj = make_dummy_2d_ungridded_data()
    write(obj, tmp_file)