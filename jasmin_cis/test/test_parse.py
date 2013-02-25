'''
Module to test the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
'''
from nose.tools import istest
from jasmin_cis.parse import parse_args
from test_files.data import *
from plotting.plot import Plotter
import argparse
from nose.tools import istest, eq_
from jasmin_cis.parse import parse_args, expand_file_list
from jasmin_cis.test.test_files.data import *
from jasmin_cis.plot import Plotter

@istest
def can_specify_one_valid_filename_and_a_directory():
    parser = argparse.ArgumentParser()
    files = expand_file_list(valid_1d_filename+','+test_directory, parser)
    eq_(len(files),4)

@istest
def can_specify_a_directory():
    parser = argparse.ArgumentParser()
    files = expand_file_list(test_directory, parser)
    eq_(len(files),3)

@istest
def can_specify_a_file_with_wildcards():
    parser = argparse.ArgumentParser()
    files = expand_file_list(os.path.join(test_directory,'test_*'), parser)
    eq_(len(files),3)
    files = expand_file_list(os.path.join(test_directory,'*_1'), parser)
    eq_(len(files),1)
    files = expand_file_list(os.path.join(test_directory,'test_?'), parser)
    eq_(len(files),3)
    files = expand_file_list(os.path.join(test_directory,'test_[0-9]'), parser)
    eq_(len(files),3)

@istest
def can_specify_one_valid_filename_and_a_wildcarded_file():
    parser = argparse.ArgumentParser()
    files = expand_file_list(valid_1d_filename+','+os.path.join(test_directory,'test_[0-9]'), parser)
    eq_(len(files),4)

@istest
def duplicate_files_are_not_returned_from_expand_file_list():
    parser = argparse.ArgumentParser()
    files = expand_file_list(os.path.join(test_directory,'test_1')+','+os.path.join(test_directory,'test_[0-9]'), parser)
    eq_(len(files),3)

@istest
def can_specify_one_valid_filename():
    args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename]
    parse_args(args)
    
@istest
def should_raise_error_with_one_invalid_filename():
    try:
        args = ["plot", valid_variable_in_valid_filename+":"+invalid_filename]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e
    
@istest
def can_specify_more_than_one_valid_filename():
    args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename+','+netcdf_file_with_incorrect_file_extension]
    parse_args(args)
    
@istest
def should_raise_error_with_a_mixture_of_valid_and_invalid_filenames():
    try:
        args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename+','+invalid_filename]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e        
    
@istest
def can_specify_valid_chart_type():
    args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, "--type", Plotter.plot_types.keys()[0]]
    parse_args(args)

@istest
def should_raise_error_with_an_invalid_chart_type():
    try:
        args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, "--type", "dfgdfgdfgdfgdfgdf"]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e    
    
@istest
def should_raise_error_with_more_than_one_chart_type():
    try:
        args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, "--type", Plotter.plot_types.keys()[0], Plotter.plot_types.keys()[1]]
        parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e

@istest
def can_specify_more_than_one_variable():
    args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, valid_variable_in_valid_filename+":"+valid_1d_filename]
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
        args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, "--itemwidth", "4a0"]
        parse_args(args) 
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e  
        
@istest
def should_raise_error_with_invalid_line_style():   
    try:   
        args = ["plot", valid_variable_in_valid_filename+":"+valid_1d_filename, "--linestyle", "4a0"]
        parse_args(args) 
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e 

#how to specify more than one variable