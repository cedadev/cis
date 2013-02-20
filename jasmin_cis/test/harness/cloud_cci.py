'''
This is currently not  working due to files having incorrect fill values and potentially other problems too
'''
#from jasmin_cis.data_io.products.AProduct import get_data
from jasmin_cis.data_io.read import read_data

#filenames = "/home/daniel/CCI_Files/*"
#filenames = [ "/home/daniel/CCI_Files/Modis_L2/20080620000000-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc" ]
filenames = [ "/home/daniel/Downloads/Fixed_CCI_Files_From_Gareth/20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc"]
data_object = read_data(filenames, 'stemp', "Cloud_CCI")

from jasmin_cis.plot import Plotter

Plotter([data_object], plot_type="scatter")#"heatmap")