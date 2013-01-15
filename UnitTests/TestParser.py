# TestParsers.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the parser
from nose.tools import istest, raises
import Parser
from UnitTests.StringsUsedInTests import valid_filename, valid_variable, invalid_filename, netcdf_file_with_incorrect_file_extension
from Exceptions.InvalidFilenameError import InvalidFilenameError

@istest
def can_specify_one_valid_filename():
    args = [valid_filename, "-v", valid_variable]
    Parser.parse_args(args)
    
@istest
@raises(InvalidFilenameError)
def should_raise_error_with_one_invalid_filename():
    args = [invalid_filename, "-v", valid_variable]
    Parser.parse_args(args)   
    
@istest
def can_specify_more_than_one_valid_filename():
    args = [valid_filename, netcdf_file_with_incorrect_file_extension, "-v", valid_variable]
    Parser.parse_args(args)