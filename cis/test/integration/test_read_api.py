from nose.tools import istest, raises
from cis.data_io.products.AProduct import ProductPluginException
from cis.test.integration_test_data import cis_test_files, invalid_filename
from cis import read_data, read_data_list


@istest
@raises(ProductPluginException)
def test_read_data_raises_error_on_invalid_variable():
    file = cis_test_files['Aerosol_CCI'].master_filename
    read_data(file, 'invalid_variable')


@istest
@raises(ValueError)
def test_read_data_raises_error_on_more_than_one_variable_returned():
    file = cis_test_files['Aerosol_CCI'].master_filename
    read_data(file, cis_test_files['Aerosol_CCI'].all_variable_names)


@istest
@raises(IOError)
def test_read_data_raises_error_on_invalid_file():
    read_data(invalid_filename, cis_test_files['Aerosol_CCI'].all_variable_names)


@istest
@raises(IOError)
def test_read_data_raises_error_on_invalid_file_wildcard():
    read_data(invalid_filename + '*', cis_test_files['Aerosol_CCI'].all_variable_names)


@istest
@raises(ProductPluginException)
def test_read_data_list_raises_error_on_invalid_variable():
    file = cis_test_files['Aerosol_CCI'].master_filename
    read_data_list(file, 'invalid_variable')


@istest
@raises(IOError)
def test_read_data_list_raises_error_on_invalid_file():
    read_data_list(invalid_filename, cis_test_files['Aerosol_CCI'].all_variable_names)


@istest
@raises(IOError)
def test_read_data_list_raises_error_on_invalid_file_wildcard():
    read_data_list(invalid_filename + '*', cis_test_files['Aerosol_CCI'].all_variable_names)
