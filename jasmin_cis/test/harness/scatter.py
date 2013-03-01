from plotting.plot import Plotter
from jasmin_cis.data_io.Coord import CoordList, Coord
from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
from numpy import array

x = Coord(array([1,2,3,4,5,6,7,8,9]), Metadata('fgfgf'),'x')
y = Coord(array([1,2,3,4,5,6,7,8,9]), Metadata('fgfghghg'),'y')
coords = CoordList([x, y])
data = array([1,2,3,4,5,6,7,8,109])
dataobject = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S", units="kg m-2 s-1", missing_value=-999), coords)

Plotter([dataobject], plot_type="scatter", logv = False, itemwidth = 400, datagroups = [{"itemstyle" : None, "color" : None, "label" : "Line 1"}])

