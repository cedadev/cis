from jasmin_cis.data_io.read import read_data, read_coordinates
from plot import Plotter

filename = "/home/david/Data/CAL_LID_L2_05kmAPro-Prov-V3-01.2010-01-01T22-40-31ZN.hdf"
filenames = [filename]

data_obj = read_data(filenames, "Particulate_Depolarization_Ratio_Profile_532", "Caliop")
#print data_obj.metadata.shape
#print data_obj.data
# Eds code from jasmin_cis.test.harness.hdf import read_hdf4
# Eds code datad = read_hdf4(filename) #DELETE ME
from plotting.plot import Plotter

Plotter([data_obj],plot_type="scatter", yrange={"ymin":0}, valrange={"vmin":0.0, "vmax":1.0})
#Plotter([data_obj],plot_type="scatter")

