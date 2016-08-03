from nose.tools import istest, eq_, raises
from cis.data_io.products.caliop import Caliop_L2
from cis.exceptions import ClassNotFoundError
from cis.data_io.products.AProduct import __get_class
from cis.parse import parse_args

# Note that the below is only used as a filename to test the product matching routines - there is no need for the actual
#  file to be present
example_caliop_l2_filename = "CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf"


@istest
def can_overide_default_product():
    from cis.data_io.products.gridded_NetCDF import NetCDF_Gridded
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


@istest
@raises(ClassNotFoundError)
def files_which_match_some_of_regexp_but_not_the_end_shouldnt_match():
    """
    Because we're using re.match the regular expression has to match the start - but not necassarily the end. This
     test ensures that we have taken care of that as often the extension is the most important part.
    """
    import cis.plugin as plugin
    from cis.data_io.products.AProduct import AProduct
    # We have to patch all of the plugin classes because get_file_type_error gets called and this file doesn't exist
    #  we are only testing the wildcard matching logic.
    product_classes = plugin.find_plugin_classes(AProduct, 'cis.data_io.products')
    for p in product_classes:
        p.get_file_type_error = lambda self, f: None
    _ = __get_class(example_caliop_l2_filename+".ext")
