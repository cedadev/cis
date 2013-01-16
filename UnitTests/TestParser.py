# TestParsers.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the parser
from nose.tools import istest, raises
import Parser
from UnitTests.StringsUsedInTests import valid_filename, valid_variable, invalid_filename, netcdf_file_with_incorrect_file_extension
import Controller

@istest
def can_specify_one_valid_filename():
    args = [valid_filename, "-v", valid_variable]
    Parser.parse_args(args)
    
@istest
def should_raise_invalidfilenameerror_with_one_invalid_filename():
    try:
        args = [invalid_filename, "-v", valid_variable]
        Parser.parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e
    
@istest
def can_specify_more_than_one_valid_filename():
    args = [valid_filename, netcdf_file_with_incorrect_file_extension, "-v", valid_variable]
    Parser.parse_args(args)
    
@istest
def should_raise_invalidfilenameerror_with_a_mixture_of_valid_and_invalid_filenames():
    try:
        args = [valid_filename, invalid_filename, "-v", valid_variable]
        Parser.parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e        
    
@istest
def can_specify_valid_chart_type():
    args = [valid_filename, "-v", valid_variable, "--type", Controller.chart_types[0]]
    Parser.parse_args(args)

@istest
def should_raise_invalidcharttypeerror_with_an_invalid_chart_type():
    try:
        args = [valid_filename, "-v", valid_variable, "--type", "dfgdfgdfgdfgdfgdf"]
        Parser.parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e    
    
@istest
def should_raise_error_with_more_than_one_chart_type():
    try:
        args = [valid_filename, "-v", valid_variable, "--type", Controller.chart_types[0], Controller.chart_types[1]]
        Parser.parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e

@istest
def can_specify_more_than_one_variable():
    args = [valid_filename, "-v", valid_variable, valid_variable]
    Parser.parse_args(args)
    
@istest
def should_raise_novariablesspecifiederror_when_no_variable_is_specified():
    try:
        args = [valid_filename]
        Parser.parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e    

#how to specify more than one variable