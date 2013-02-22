from jasmin_cis.data_io.read import read_data, read_coordinates
from plot import Plotter

filename = "/home/david/Data/CAL_LID_L2_05kmAPro-Prov-V3-01.2010-01-01T22-40-31ZN.hdf"
filenames = [filename]

data_obj = read_data(filenames, "Backscatter_Coefficient_1064", "Caliop")
print data_obj.metadata.shape
print data_obj.data

Plotter([data_obj])

