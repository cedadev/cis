'''
Module to test the col command of the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Some tests therefore ignore SystemExit exceptions with code 2 if they are expected.
'''
from nose.tools import istest, eq_
from jasmin_cis.parse import parse_args
from jasmin_cis.test.test_files.data import *

@istest
def can_specify_one_valid_samplefile_and_one_complete_datagroup():
    args = ["col", valid_1d_filename, "variable:"+valid_1d_filename+":col:con:nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup)
    eq_([{"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : ("col",{}), "constraint" : ("con",{}), "kernel" : ("nn",{}), "product" : None}],
        args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_other_options():
    args = ["col", valid_1d_filename, "variable:"+valid_1d_filename]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup)
    eq_([{"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : None, "constraint" : None, "kernel" : None, "product" : None}],
        args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_many_datagroups():
    args = ["col", valid_1d_filename, 
            "variable:"+valid_1d_filename,
            "variable:"+valid_1d_filename+':col',
            "variable:"+valid_1d_filename+'::con',
            "variable:"+valid_1d_filename+':::nn',
            "variable:"+valid_1d_filename+':col::nn']
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup)
    eq_([{"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : None, "constraint" : None, "kernel" : None, "product" : None},
         {"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : ('col',{}), "constraint" : None, "kernel" : None, "product" : None},
         {"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : None, "constraint" : ('con',{}), "kernel" : None, "product" : None},
         {"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : None, "constraint" : None, "kernel" : ('nn',{}), "product" : None},
         {"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : ('col',{}), "constraint" : None, "kernel" : ('nn',{}), "product" : None}],
        args.datagroups)


@istest
def can_specify_one_valid_samplefile_and_one_datafile_with_internal_options():
    args = ["col", valid_1d_filename, "variable:"+valid_1d_filename+"::SepConstraint,h_sep=1500,v_sep=22000,t_sep=5000:nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup)
    eq_([{"filenames" : [valid_1d_filename], "variable" : "variable", "colocator" : None,
          "constraint" : ('SepConstraint',{'h_sep':'1500','v_sep':'22000','t_sep':'5000'}), "kernel" : ('nn',{}), "product" : None}], args.datagroups)


@istest
def should_raise_error_with_missing_arguments():
    try:
        args = ["col", valid_1d_filename]
        args = parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e