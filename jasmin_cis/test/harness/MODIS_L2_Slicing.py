from jasmin_cis.data_io.read import read_data
from jasmin_cis.plotting.plot import Plotter
from copy import deepcopy

variable = "Effective_Optical_Depth_Average_Ocean"
filename = "/home/daniel/Code/jasmin_cis/jasmin_cis/test/test_files/MOD04_L2.A2010001.2255.005.2010005215814.hdf"
#wavelength_index = 3

data_object = read_data([filename], variable)

# Do all coords have the same dimensionality?
coord_shape = None
for coord in data_object.coords():
    if coord_shape == None:
        coord_shape = coord.shape
    else:
        if coord_shape != coord.shape:
            raise Exception("All coords must be of the same shape")

print "All coords are of the shape: " + str(coord_shape)

print "Shape of data: " + str(data_object.shape)

if len(data_object.shape) > len(coord_shape):
    print "Shape of data has " + str(len(data_object.shape) - len(coord_shape)) + " more dimension(s) than its coordinates"

for wavelength_index in range(0,7,1):
    print wavelength_index
    sliced_data_object = deepcopy(data_object)
    sliced_data_object.data = data_object.data[wavelength_index,:,:]
    sliced_data_object.shape = [203, 135]

    Plotter([sliced_data_object], out_filename="/home/daniel/Desktop/modis" + str(wavelength_index))