from nose.tools import istest, eq_
from cis.data_io.products.caliop import Caliop_L2

from cis.data_io.products.AProduct import __get_class
from cis.parse import parse_args

# Note that the below is only used as a filename to test the product matching routines - there is no need for the actual
#  file to be present
example_caliop_l2_filename = "CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf"

@istest
def can_overide_default_product():
    from data_io.products import NetCDF_Gridded
    eq_(__get_class(example_caliop_l2_filename), Caliop_L2)
    eq_(__get_class(example_caliop_l2_filename, "NetCDF_Gridded"), NetCDF_Gridded)


@istest
def should_raise_error_with_unknown_product_specified():
    try:
        parse_args(["plot", "var:" + example_caliop_l2_filename + "::::unknownproduct"])
        assert False
    except SystemExit as e:
        if e.code != 2:
            raise e
