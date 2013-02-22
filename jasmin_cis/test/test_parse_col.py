'''
Module to test the col command of the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Some tests therefore ignore SystemExit exceptions with code 2 if they are expected.
'''
from nose.tools import istest, eq_
from jasmin_cis.parse import parse_args
from test_files.data import *

@istest
def can_specify_one_valid_samplefile_and_one_complete_datagroup():
    args = ["col", valid_1d_filename, "variable:"+valid_1d_filename+":col:con:nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplefilename)
    eq_([{"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : ("col",{}), "constraint" : ("con",{}), "kernel" : ("nn",{}) }], args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_other_options():
    args = ["col", valid_1d_filename, "variable:"+valid_1d_filename]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplefilename)
    eq_([{"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : None, "constraint" : None, "kernel" : None}], args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_many_datafiles():
    args = ["col", valid_1d_filename, 
            "variable:"+valid_1d_filename,
            "variable:"+valid_1d_filename+':col',
            "variable:"+valid_1d_filename+'::con',
            "variable:"+valid_1d_filename+':::nn',
            "variable:"+valid_1d_filename+':col::nn']
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplefilename)
    eq_([{"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : None, "constraint" : None, "kernel" : None},
         {"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : ('col',{}), "constraint" : None, "kernel" : None},
         {"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : None, "constraint" : ('con',{}), "kernel" : None},
         {"filenames" : {valid_1d_filename}, "variable" : "variable", "colocator" : ('col',{}), "constraint" : None, "kernel" : ('nn',{})}], args.datagroups)

@istest
def should_raise_error_with_missing_arguments():
    try:
        args = ["col", valid_1d_filename]
        args = parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e