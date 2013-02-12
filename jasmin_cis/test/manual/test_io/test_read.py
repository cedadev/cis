'''
Module to test the reading of NetCDF files
These tests have to be run manually 
'''
from nose.tools import nottest
import jasmin_cis.data_io.read as cis_read
from jasmin_cis.test.test_files.data import *

@nottest # Too big to store in Git repository, can still be run manually
def can_read_15GB_file_when_reading_variables():
    from jasmin_cis.info import info
    filename = large_15GB_file_filename
    info(filename)

@nottest # Too big to store in Git repository, can still be run manually
def can_read_15GB_file_when_loading_a_cube():
    filename = large_15GB_file_filename
    cis_read.read_data(filename, valid_variable_in_valid_filename)

if __name__ == "__main__":
    can_read_15GB_file_when_reading_variables()
    can_read_15GB_file_when_loading_a_cube()
    print("Finished")