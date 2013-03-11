from jasmin_cis.data_io.read import read_data
from nose.tools import istest
from jasmin_cis.test.test_files.data import *
from jasmin_cis.parse import parse_args

def __read_file_using_all_products(filename, variable):
    from jasmin_cis.data_io.products.AProduct import AProduct
    import jasmin_cis.plugin as plugin
    from jasmin_cis.exceptions import InvalidVariableError

    product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products.products')
    product_names = [cls().__class__.__name__ for cls in product_classes]

    for product_name in product_names:
        try:
            read_data([filename], variable, product_name)
        except (IOError, InvalidVariableError):
            pass

@istest
def can_read_xglnwa_file_with_invalid_filename():
    filename = netcdf_file_with_incorrect_file_extension
    read_data([filename], valid_variable_in_valid_filename, "Xglnwa")

@istest
def should_raise_io_error_or_invalid_variable_error_with_invalid_product_for_modis_l2_file_specified():
    __read_file_using_all_products(valid_modis_l2_variable, valid_modis_l2_filename)

@istest
def should_raise_io_error_or_invalid_variable_error_with_invalid_product_for_aeronet_file_specified():
    __read_file_using_all_products(valid_aeronet_filename, valid_aeronet_variable)

@istest
def should_raise_io_error_or_invalid_variable_error_with_invalid_product_for_xglnwa_file_specified():
    __read_file_using_all_products(netcdf_file_with_incorrect_file_extension, valid_variable_in_valid_filename)

@istest
def should_raise_error_with_unknown_product_specified():
    filename = netcdf_file_with_incorrect_file_extension
    try:
        parse_args(["plot", valid_variable_in_valid_filename + ":" + filename + "::::unknownproduct"])
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e

