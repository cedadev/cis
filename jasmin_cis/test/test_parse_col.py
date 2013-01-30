'''
Module to test the col command of the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
'''
from nose.tools import istest, eq_
from jasmin_cis.parse import parse_args
from test_files.data import *

@istest
def can_specify_one_valid_samplefile_and_one_complete_datafile():
    args = ["col", valid_1d_filename, valid_1d_filename + ":variable:method"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"}], args["datafiles"])
    
@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_a_method_if_default_set():
    args = ["col", valid_1d_filename, valid_1d_filename + ":variable:", "--method", "nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"}], args["datafiles"])
    
@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_a_variable_if_default_set():
    args = ["col", valid_1d_filename, valid_1d_filename + "::method", "--variable", "variable"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"}], args["datafiles"])
    
@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_a_variable_or_method_if_default_set():
    args = ["col", valid_1d_filename, valid_1d_filename + "::", "--variable", "variable", "--method", "method"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"}], args["datafiles"])
    
@istest
def can_specify_one_valid_samplefile_and_many_datafiles():
    args = ["col", valid_1d_filename, 
            valid_1d_filename + "::", 
            valid_1d_filename + "::", 
            valid_1d_filename + "::", 
            valid_1d_filename + "::",
            "--variable", "variable", "--method", "nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "nn"}], 
        args["datafiles"])
    
@istest
def can_specify_one_valid_samplefile_and_many_datafiles_with_varying_specifications():
    args = ["col", valid_1d_filename, 
            valid_1d_filename + "::", 
            valid_1d_filename + ":variable:", 
            valid_1d_filename + "::method", 
            valid_1d_filename + ":variable:method",
            "--variable", "variable", "--method", "method"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "variable", "method" : "method"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "method"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "method"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "method"}], 
        args["datafiles"])
    
@istest
def can_specify_default_variable_and_method():
    args = ["col", valid_1d_filename, 
            valid_1d_filename + "::", 
            valid_1d_filename + ":variable:", 
            valid_1d_filename + "::method", 
            valid_1d_filename + ":variable:method",
            "--variable", "defaultVariable",
            "--method", "defaultMethod"]
    args = parse_args(args)
    eq_(valid_1d_filename, args["samplefilename"])
    eq_([{"filename" : valid_1d_filename, "variable" : "defaultVariable", "method" : "defaultMethod"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "defaultMethod"},
         {"filename" : valid_1d_filename, "variable" : "defaultVariable", "method" : "method"},
         {"filename" : valid_1d_filename, "variable" : "variable", "method" : "method"}], 
        args["datafiles"])

@istest
def should_raise_error_with_missing_arguments():
    try:
        args = ["col", valid_1d_filename]
        args = parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e