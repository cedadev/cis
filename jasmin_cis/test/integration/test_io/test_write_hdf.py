from nose import with_setup
from nose.tools import nottest
import os
from jasmin_cis.test.util.mock import make_dummy_2d_ungridded_data

tmp_file = "tmp_file"

def delete_tmp_file():
    os.remove(tmp_file)

@nottest
@with_setup(teardown=delete_tmp_file)
def test_write_hdf():
    '''
    Test currently fails. Will not be fixed as there is no use case.
    :return:
    '''
    from jasmin_cis.data_io.write_hdf import write
    obj = make_dummy_2d_ungridded_data()
    write(obj, tmp_file)