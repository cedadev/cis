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
    args = ["col", "variable:"+valid_1d_filename, valid_1d_filename+":colocator=col,constraint=con,kernel=nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup['filenames'][0])
    eq_(('col', {}), args.samplegroup['colocator'])
    eq_(('con', {}), args.samplegroup['constraint'])
    eq_(('nn', {}), args.samplegroup['kernel'])
    eq_([{'variable': 'variable', 'product': None, 'filenames': [valid_1d_filename]}], args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_one_datafile_without_other_options():
    args = ["col", "variable:"+valid_1d_filename, valid_1d_filename]
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup['filenames'][0])
    eq_(None, args.samplegroup['colocator'])
    eq_(None, args.samplegroup['constraint'])
    eq_(None, args.samplegroup['kernel'])
    eq_([{'variable': 'variable', 'product': None, 'filenames': [valid_1d_filename]}], args.datagroups)

@istest
def can_specify_one_valid_samplefile_and_many_datagroups():
    args = ["col", "variable1:"+valid_1d_filename,
            "variable2:"+valid_1d_filename,
            "variable3:"+valid_1d_filename,
            valid_1d_filename+':variable=variable4,colocator=col,kernel=nn']
    args = parse_args(args)
    eq_(valid_1d_filename, args.samplegroup['filenames'][0])
    eq_("variable4", args.samplegroup['variable'])
    eq_(('col', {}), args.samplegroup['colocator'])
    eq_(None, args.samplegroup['constraint'])
    eq_(('nn', {}), args.samplegroup['kernel'])
    eq_(valid_1d_filename, args.datagroups[0]['filenames'][0])
    eq_("variable1", args.datagroups[0]['variable'])
    eq_(valid_1d_filename, args.datagroups[1]['filenames'][0])
    eq_("variable2", args.datagroups[1]['variable'])
    eq_(valid_1d_filename, args.datagroups[2]['filenames'][0])
    eq_("variable3", args.datagroups[2]['variable'])


@istest
def can_specify_one_valid_samplefile_and_one_datafile_with_internal_options():
    args = ["col", "var1:"+valid_1d_filename,
            valid_1d_filename+":variable=var2,constraint=SepConstraint[h_sep=1500,v_sep=22000,t_sep=5000],kernel=nn"]
    args = parse_args(args)
    eq_(valid_1d_filename, args.datagroups[0]['filenames'][0])
    eq_("var1", args.datagroups[0]['variable'])
    eq_(valid_1d_filename, args.samplegroup['filenames'][0])
    eq_("var2", args.samplegroup['variable'])
    eq_(('SepConstraint',{'h_sep':'1500','v_sep':'22000','t_sep':'5000'}), args.samplegroup['constraint'])
    eq_(('nn',{}), args.samplegroup['kernel'])
    eq_(None, args.samplegroup['colocator'])
    eq_(None, args.samplegroup['product'])


@istest
def should_raise_error_with_missing_arguments():
    try:
        args = ["col", valid_1d_filename]
        args = parse_args(args)
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e