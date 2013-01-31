'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
    
def create_variable(nc_file, name, v_type, dimensions, data_object = None):
    var = nc_file.createVariable(name, v_type, dimensions)
    
    return var

def write_to_file(variables, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w')
    # Create dimensions
    netcdf_file.createDimension("latitude", size = 3) # Size = None or 0 = Unlimited (can be appended to)
    netcdf_file.createDimension("longitude", size = 2)
    netcdf_file.createDimension("time", size = 0)
    # Create variables
    time = create_variable(netcdf_file, "time", "d", ("time",)) # d = double
    time.standard_name = "time"
    time.units = "minutes since 1994-01-01 00:00:00"
    time.long_name = "time"
    
    latitude = create_variable(netcdf_file, "latitude", "f", ("latitude",)) # f = float
    latitude.standard_name = "latitude"
    latitude.units = "degrees_north"
    latitude.point_spacing = "even"
    latitude.long_name = "latitude"
    
    longitude = create_variable(netcdf_file, "longitude", "f", ("longitude",))
    
    temp = netcdf_file.createVariable("temp", "f", ("time", "latitude", "longitude"))
    netcdf_file.close()

write_to_file(None, "test_netcdf_file")