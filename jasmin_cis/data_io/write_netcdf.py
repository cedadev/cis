'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset

def __create_dimensions(nc_file, data_object):
    dimensions = ()
    for i, coord in enumerate(data_object.coords()):
        nc_file.createDimension(coord.name(), len(data_object.data_list[i]))
        dimensions = dimensions + (coord.name(),)
        
        var = nc_file.createVariable(coord.name(), data_object.type, coord.name())
        var[:] = data_object.data_list[i]
        
    return dimensions

def write(data_object, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w')
    dimensions = __create_dimensions(netcdf_file, data_object)
    variable = netcdf_file.createVariable(data_object.standard_name, data_object.type, dimensions)
    variable[:] = data_object.data
    netcdf_file.close()

def test_main():
    from ungridded_data import UngriddedData, Coord, Metadata
    from numpy import array
    coords = []
    coords.append(Coord(array(1,2,3,4,5,6,7,8,9,10), Metadata("Lon", "Longitude", (10,), "degrees", (-180, 180), missing_value=-999), "X"))
    coords.append(Coord(array(3,5,3,1,8,5,3,2,6,31), Metadata("Lat", "Latitude", (10,), "degrees", (-90, 90), missing_value=-999), "Y"))
    coords.append(Coord(array(7,8,9,10,11,12,13,14,15,16), Metadata("Time", "Time", (10,), "seconds", (0,10000), missing_value=-999), "T"))
    data_object = UngriddedData(data, coords, metadata)

test_main()