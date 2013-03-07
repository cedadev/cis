from jasmin_cis.data_io.read import read_data, read_coordinates

filename = "/home/duncan/jasmin_cis/jasmin_cis/test/test_files/CAL_LID_L2_05kmAPro-Prov-V3-01.2009-12-31T23-36-08ZN.hdf"
filenames = [filename]


from jasmin_cis.exceptions import InvalidVariableError
from jasmin_cis.data_io.hdf import get_hdf4_file_metadata
from jasmin_cis.data_io.hdf_vd import get_data, VDS


my_data = get_data(VDS(filename,'Production_Script'), first_record=True)

print my_data

# metadata_dict = get_hdf4_file_metadata(filename)
#
# for item,val in metadata_dict.iteritems():
#     print item, val
#print metadata_dict

#data_obj = read_data(filenames, "Particulate_Depolarization_Ratio_Profile_532", "Caliop")



#print data_obj.metadata.shape
#print data_obj.data
# Eds code from jasmin_cis.test.harness.hdf import read_hdf4
# Eds code datad = read_hdf4(filename) #DELETE ME
#from plotting.plot import Plotter

#Plotter([data_obj],plot_type="scatter", yrange={"ymin":0}, valrange={"vmin":0.0, "vmax":1.0})
#Plotter([data_obj],plot_type="scatter")

