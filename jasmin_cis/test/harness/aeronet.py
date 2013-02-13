from jasmin_cis.data_io.products.AProduct import get_data

filenames = ["/home/daniel/Aeronet_Files/Data/920801_091128_Abracos_Hill.lev20"]
data_object = get_data(filenames, 'AOT_1640',"Aeronet")

print data_object