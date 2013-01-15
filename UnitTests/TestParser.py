# TestParsers.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the parser
from nose.tools import istest, eq_
import Parser
import UnitTests.ReadNetCDFFile
import UnitTests.Plot1DNetCDFFile

@istest
def can_get_help(): 
    Parser.parse_args("-h")
    Parser.parse_args("--help")

@istest
def can_specify_one_filename():
    filename = ["myfilename"]
    args = Parser.parse_args(filename)
    eq_(args.filenames, filename)
    
@istest
def can_specify_more_than_one_filename():
    filenames = ["one", "two", "three", "four"]
    args = Parser.parse_args(filenames)
    eq_(args.filenames, filenames)
    
@istest
def can_validate_if_one_filename_exists():
    filename = [UnitTests.ReadNetCDFFile.valid_filename, "-v", UnitTests.Plot1DNetCDFFile.valid_variable]
    args = Parser.parse_args(filename)
    Parser.validate_args(args)
    
#can_validate_if_one_filename_exists()