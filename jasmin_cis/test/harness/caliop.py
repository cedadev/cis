from jasmin_cis.data_io.products.AProduct import get_data

filename = "/home/daniel/Caliop_Files/CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf"
filenames = [filename]
data_object = get_data(filenames, "Backscatter_Coefficient_1064", "Caliop")

# Eds code from jasmin_cis.test.harness.hdf import read_hdf4
# Eds code datad = read_hdf4(filename) #DELETE ME
from jasmin_cis.plot import Plotter

Plotter([data_object])