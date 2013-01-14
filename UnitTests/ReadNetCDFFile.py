# Module to test the reading of NetCDF files
import nose
from nose.tools import istest, eq_

@istest
def x_equals_0():
    x = 0
    eq_(x, 0)
    
