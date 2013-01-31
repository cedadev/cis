'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset

def create_dimensions(nc_file, data_object):
    dimensions = ()
    for i, coord in enumerate(data_object.coords()):
        nc_file.createDimension(coord.name(), len(data_object.data_list[i]))
        dimensions = dimensions + (coord.name(),)
        
        var = nc_file.createVariable(coord.name(), data_object.type, coord.name())
        var[:] = data_object.data_list[i]
        
    return dimensions

def write_to_file(data_object, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w')
    dimensions = create_dimensions(netcdf_file, data_object)
    variable = netcdf_file.createVariable(data_object.short_name, data_object.type, dimensions)
    variable[:] = data_object.data
    netcdf_file.close()