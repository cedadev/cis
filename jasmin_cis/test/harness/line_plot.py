from plotting.plot import Plotter
from jasmin_cis.test.util.mock import make_dummy_1d_ungridded_data
data_object1 = make_dummy_1d_ungridded_data()
data_object2 = make_dummy_1d_ungridded_data()
Plotter([data_object1, data_object2],
        datagroups = [{"itemstyle" : None, "color" : None, "label" : "Line 1"},
                                        {"itemstyle" : None, "color" : None, "label" : None}],
        xrange = {"xmin" : -100, "xstep" : 25, "xmax" : 100},
        yrange = {"ymin" : 0, "ystep" : 0.5},
        plot_type="line")
