from plotting.plot import Plotter
from data_io.Coord import CoordList, Coord
from data_io.ungridded_data import UngriddedData, Metadata
from numpy import array, arange

x = Coord(arange(10), Metadata('latitude'),'x')
coords = CoordList([x])

data1 = array([1,1.5,1,1.5,
              2,2,2.5,
              3,3.5,
              4,
              5,5.5,
              6,6.5,6,
              7,7,7.5,7,
              8,8.5,8,8,8,
              9,9,9.5,9,
              10,10.5,10])

data2 = array([1.5,1,1.5,1,1,
               2,2.5,2,
               3.5,
               5.5,5,5,
               6.5,6,
               7,7.5,7,7,7,
               8.5,8,8,8,8,8,8,
               9,9.5,9,
               10.5,10])


data_object1 = UngriddedData(data1, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)
data_object2 = UngriddedData(data2, Metadata(standard_name='snow', long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)

Plotter([data_object1, data_object2],
        cmap = "RdBu",
        ylabel = "Overidden y",
        title = "Overidden Title",
        xrange = {"xmin" : 4, "xmax" : 8},
        yrange = {"ystep" : 0.5},
        valrange = {"vmin" : 1.2, "vstep" : 0.4},
        datagroups = [{"itemstyle" : None, "color" : None, "label" : None},
                      {"itemstyle" : None, "color" : None, "label" : None}],
        plot_type="histogram3d")

