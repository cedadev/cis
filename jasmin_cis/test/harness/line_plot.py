from plotting.plot import Plotter
from jasmin_cis.test.test_util.mock import make_dummy_1d_ungridded_data
data_object1 = make_dummy_1d_ungridded_data()
data_object2 = make_dummy_1d_ungridded_data()
Plotter([data_object1, data_object2], {"xlabel" : None, "ylabel" : None, "title" : None, "fontsize" : None, "grid" : False, "logy" : False, "logx" : False, "logv": False, "no_colour_bar" : False, "x_range" : None, "y_range" : None,
                         "datagroups" : [{"itemstyle" : None, "color" : None, "label" : "Line 1"},
                                        {"itemstyle" : None, "color" : None, "label" : None}]}, plot_type="line")
