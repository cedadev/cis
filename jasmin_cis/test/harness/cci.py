from jasmin_cis.data_io.products.AProduct import get_data

#filenames = "/home/daniel/CCI_Files/*"
filenames = [ "/home/daniel/CCI_Files/20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc" ]
data_object = get_data(filenames, 'AOD550',"Cloud_CCI")

from jasmin_cis.plot import Plotter

Plotter([data_object], plot_type="scatter")