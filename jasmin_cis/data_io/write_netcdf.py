'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
from numpy import int64

types = {float: "f",
         int64: "i"}

def __create_dimensions(nc_file, data_object):
    dimensions = ()
    first_coord = True
    for coord in data_object.coords():
        if first_coord:
            dimension = nc_file.createDimension(coord.name(), len(coord.data))
            dimensions = dimensions + (coord.name(),)
            first_coord = False
        var = nc_file.createVariable(coord.name(), types[type(coord.data[0])], dimension._name, fill_value=coord._metadata.missing_value)
        var.standard_name = coord._metadata._name
        var.units = coord._metadata.units
        var.long_name = coord._metadata.long_name
        var.valid_range = coord._metadata.range
        var[:] = coord.data
        
    return dimensions

def write(data_object, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w')
    dimensions = __create_dimensions(netcdf_file, data_object)
    variable = netcdf_file.createVariable(data_object.name(), types[type(data_object.data[0])], dimensions)
    variable[:] = data_object.data
    netcdf_file.close()

def test_main():
    from ungridded_data import UngriddedData, Coord, Metadata
    from numpy import array
    coords = []
    coords.append(Coord(array([1,2,3,4,5,6,7,8,9,10]), Metadata("pixel_number", "Sinusoidal pixel index", (10,), range = (0,90352))))
    coords.append(Coord(array([1,2,3,4,5,6,7,8,9,10]), Metadata("lon", "Longitude", (10,), "degrees_east", (-180, 180), missing_value=-999), "X"))
    coords.append(Coord(array([3,5,3,1,8,5,3,2,6,31]), Metadata("lat", "Latitude", (10,), "degrees_north", (-90, 90), missing_value=-999), "Y"))
    coords.append(Coord(array([7,8,9,10,11,12,13,14,15,16]), Metadata("time", "TAI70 time", (10,), "seconds", (1,-1), missing_value=0), "T"))

    data = array([6,43,86,25,86,12,95,45,73,87])
    metadata = Metadata('rain', 'Long Rain', (10,), 'Rain units', (0,100), missing_value='-999')
    data_object = UngriddedData(data, metadata, coords)
    write(data_object, "ungridded_netcdf.nc")

test_main()