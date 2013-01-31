from pyhdf.SD import *
from numpy import *
from jasmin_cis.test.test_util.mock import gen_random_data

filename = "test_hdf_file"

def create_variable(hdf_file, name):
    var = hdf_file.create(name, SDC.FLOAT32, (3,3))
    var.description = name + " 3x3 float array"
    var.units = "blah"
    
    dimension1 = var.dim(0)
    dimension2 = var.dim(1)
    
    dimension1.setname("width")
    dimension2.setname("height")
    
    dimension1.units = "m"
    dimension2.units = "cm"
    
    var[0] = (gen_random_data(), gen_random_data(), gen_random_data())
    var[1] = (gen_random_data(), gen_random_data(), gen_random_data())
    var[2] = (gen_random_data(), gen_random_data(), gen_random_data())
    
    var.endaccess()
    
def write():
    hdf_file = SD(filename, SDC.WRITE|SDC.CREATE)

    hdf_file.author = "WALDM"
    
    create_variable(hdf_file, "rain")
    create_variable(hdf_file, "latitude")
    create_variable(hdf_file, "longitude")   
    
    hdf_file.end()
    
def read():
    # Open file in read-only mode (default)
    hdf_file = SD(filename)
    # Open variable 'rain'
    rain = hdf_file.select('rain')
    # Display variable attributes.
    print "variable:", 'rain'
    # Show variable values
    print rain[:]
    # Close variable
    rain.endaccess()    
    
    # Open variable 'latitude'
    latitude = hdf_file.select('latitude')
    # Display variable attributes.
    print "variable:", 'latitude'
    # Show variable values
    print latitude[:]
    # Close variable
    latitude.endaccess()    
    
    # Open variable 'longitude'
    longitude = hdf_file.select('longitude')
    print "variable:", 'longitude'
    # Show variable values
    print longitude[:]
    # Close variable
    longitude.endaccess()
    # Close file
    hdf_file.end()

write()    
read()