from jasmin_cis.data_io.products.AProduct import get_data

filenames = ["/home/daniel/Aeronet_Files/Data/920801_091128_Abracos_Hill_small.lev20"]
data_object1 = get_data(filenames, 'AOT_1020',"Aeronet")
data_object2 = get_data(filenames, 'AOT_870',"Aeronet")
data_object3 = get_data(filenames, 'AOT_675',"Aeronet")
data_object4 = get_data(filenames, 'AOT_500',"Aeronet")
data_object5 = get_data(filenames, 'Watercm',"Aeronet")

from plotting.plot import Plotter

Plotter([data_object1, data_object2, data_object3, data_object4, data_object5])