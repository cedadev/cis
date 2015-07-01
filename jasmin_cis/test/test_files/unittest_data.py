'''
Module that contains various strings that are used in tests
'''
from os.path import join, dirname

data_directory = dirname(__file__)

def make_pathname(filename):
    return join(data_directory, filename)

test_directory = make_pathname('test_directory_for_parser')
test_directory_file1 = test_directory + "/test_file_for_parser_1"
test_directory_file2 = test_directory + "/test_file_for_parser_2"
test_directory_file3 = test_directory + "/test_file_for_parser_3"
test_directory_files = [test_directory_file1, test_directory_file2, test_directory_file3]

# Note that the below is only used as a filename to test the product matching routines - there is no need for the actual
#  file to be present
valid_caliop_l2_filename = make_pathname("CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf")

single_valid_file = make_pathname("single_data_file")

multiple_valid_files = [make_pathname("data_file_1"), make_pathname("data_file_2")]

dummy_cis_out = make_pathname('out.nc')

invalid_filename = "invalidfilename"

out_filename = "cube_image.png"
