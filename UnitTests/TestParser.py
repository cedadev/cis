# TestParsers.py
# Created by WALDM on 14th Jan 2013
# Copyright TODO
#
# Module to test the parser
from nose.tools import *
import Parser

@istest
def can_get_help():       
    Controller.parse_args("-h")