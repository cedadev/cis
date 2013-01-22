'''
Module to test the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
'''
from nose.tools import istest
from jasmin_cis.parse import parse_args
from data import *
from jasmin_cis.plot import plot_types

@istest
def can_specify_one_valid_filename():
    args = ["plot", valid_1d_filename, "-v", valid_variable]
    parse_args(args)
    
@istest
def should_raise_error_with_one_invalid_filename():
    try:
        args = ["plot", invalid_filename, "-v", valid_variable]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e
    
@istest
def can_specify_more_than_one_valid_filename():
    args = ["plot", valid_1d_filename, netcdf_file_with_incorrect_file_extension, "-v", valid_variable]
    parse_args(args)
    
@istest
def should_raise_error_with_a_mixture_of_valid_and_invalid_filenames():
    try:
        args = ["plot", valid_1d_filename, invalid_filename, "-v", valid_variable]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e        
    
@istest
def can_specify_valid_chart_type():
    args = ["plot", valid_1d_filename, "-v", valid_variable, "--type", plot_types.keys()[0]]
    parse_args(args)

@istest
def should_raise_error_with_an_invalid_chart_type():
    try:
        args = ["plot", valid_1d_filename, "-v", valid_variable, "--type", "dfgdfgdfgdfgdfgdf"]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e    
    
@istest
def should_raise_error_with_more_than_one_chart_type():
    try:
        args = ["plot", valid_1d_filename, "-v", valid_variable, "--type", plot_types.keys()[0], plot_types.keys()[1]]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e

@istest
def can_specify_more_than_one_variable():
    args = ["plot", valid_1d_filename, "-v", valid_variable, valid_variable]
    parse_args(args)
    
@istest
def should_raise_error_when_no_variable_is_specified():
    try:
        args = ["plot", valid_1d_filename]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e    
        
@istest
def should_raise_error_with_invalid_line_width():
    try:   
        args = ["plot", valid_1d_filename, "-v", valid_variable, "--linewidth", "4a0"]
        parse_args(args) 
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e  
        
@istest
def should_raise_error_with_invalid_line_style():   
    try:   
        args = ["plot", valid_1d_filename, "-v", valid_variable, "--linestyle", "4a0"]
        parse_args(args) 
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e 

#how to specify more than one variable