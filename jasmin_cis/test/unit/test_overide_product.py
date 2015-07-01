from nose.tools import istest, eq_
from jasmin_cis.data_io.products.caliop import Caliop_L2

from jasmin_cis.data_io.products.AProduct import __get_class
from jasmin_cis.test.test_files.unittest_data import valid_caliop_l2_filename
from jasmin_cis.parse import parse_args


@istest
def can_overide_default_product():
    from jasmin_cis.data_io.products.products import NetCDF_Gridded
    filename = valid_caliop_l2_filename
    eq_(__get_class(filename), Caliop_L2)
    eq_(__get_class(filename, "NetCDF_Gridded"), NetCDF_Gridded)


@istest
def should_raise_error_with_unknown_product_specified():
    filename = valid_caliop_l2_filename
    try:
        parse_args(["plot", "var:" + filename + "::::unknownproduct"])
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e
