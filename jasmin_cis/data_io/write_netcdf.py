'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
from numpy import shape

class UngriddedData(object):
    def __init__(self, x, y, data, long_name, units, coords, v_type, short_name):
        self.x = x # A numpy array
        self.y = y # A numpy array
        self.data = data # A numpy array
        self.data_list = [x, y, data]
        self.shape = shape(data) # A tuple
        self.long_name = long_name # A string
        self.units = units # A string
        self._coords = coords
        self.type = v_type
        self.short_name = short_name
        
    def coords(self, optional_arg1 = None, optional_arg2 = None):
        return self._coords # list of object Coord
    
class Coord(object):
    def __init__(self, name):
        self._name = name
    def name(self):
        return self._name

def create_dimensions(nc_file, data_object):
    dimensions = ()
    for i, coord in enumerate(data_object.coords()):
        nc_file.createDimension(coord.name(), len(data_object.data_list[i]))
        dimensions = dimensions + (coord.name(),)
        
        var = nc_file.createVariable(coord.name(), data_object.type, coord.name())
        var[:] = data_object.data_list[i]
        
    return dimensions

def set_metadata(nc_file, data_object):
    pass
    #nc_file.units = data_object.units
    #nc_file.long_name = data_object.long_name

def write_to_file(data_object, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w')
    dimensions = create_dimensions(netcdf_file, data_object)
    variable = netcdf_file.createVariable(data_object.short_name, data_object.type, dimensions)
    variable[:] = data_object.data
    set_metadata(netcdf_file, data_object)
    netcdf_file.close()

def main():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8]
    data = [[0.1, 0.5, 0.6, 0.2, 0.9],[0.2, 3.5, 0.6, 2.2, 0.9],[4.1, 5.5, 2.2, 2.2, 0.2],[0.2, 5.5, 6.6, 0.7, 6.9]]
    coords = [Coord("latitude"), Coord("longitude")]
    data_object = UngriddedData(x, y, data, "TOTAL RAINFALL RATE: LS+CONV KG/M2/S", "kg m-2 s-1", coords, "f", "rain")
    write_to_file(data_object, "test_netcdf_file")
    
main()