#from jasmin_cis.data_io.products.AProduct import get_data
from glob import glob

from jasmin_cis.data_io.read import read_data


filenames = glob("/home/daniel/Downloads/Fixed_CCI_Files_From_Gareth/*")
#filenames = [ "/home/daniel/CCI_Files/Modis_L2/20080620000000-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc" ]
#filenames = [ "/home/daniel/Downloads/Fixed_CCI_Files_From_Gareth/20080620073500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc"]
data_object = read_data(filenames, 'stemp', "Cloud_CCI")

from plotting.plot import Plotter

Plotter([data_object], valrange = {"vmin" :260, "vmax" : 340}, plot_type="scatter", itemwidth=1)