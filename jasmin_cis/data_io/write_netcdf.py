'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
from numpy import int64

types = {float: "f",
         int64: "i"}

def __add_metadata(var, coord):
    if coord._metadata.standard_name: var.standard_name = coord._metadata.standard_name
    if coord._metadata.units: var.units = coord._metadata.units
    if coord._metadata.long_name: var.long_name = coord._metadata.long_name
    if coord._metadata.range : var.valid_range = coord._metadata.range
    return var

def __get_missing_value(coord):
    f = coord._metadata.missing_value
    if not f and f !=0:
        f = None
    return f

def __create_dimensions(nc_file, data_object):
    dimensions = ()
    first_coord = True
    for coord in data_object.coords():
        if first_coord:
            dimension = nc_file.createDimension(coord.name(), len(coord.data))
            dimensions = dimensions + (coord.name(),)
            first_coord = False
        var = nc_file.createVariable(coord.name(), types[type(coord.data[0])], dimension._name, fill_value=__get_missing_value(coord))
        var = __add_metadata(var, coord)
        var[:] = coord.data
        
    return dimensions

def write(data_object, filename):
    # Create file
    netcdf_file = Dataset(filename, 'w', format="NETCDF4_CLASSIC")
    dimensions = __create_dimensions(netcdf_file, data_object)
    variable = netcdf_file.createVariable(data_object.name(), types[type(data_object.data[0])], dimensions, fill_value=__get_missing_value(data_object))
    variable = __add_metadata(variable, data_object)
    variable[:] = data_object.data
    netcdf_file.close()

def test_main():
    from ungridded_data import UngriddedData, Coord, Metadata
    from numpy import array
    coords = []
    coords.append(Coord(array([1,2,3,4,5,6,7,8,9,10]), Metadata(name="pixel_number",
                                                                long_name="Sinusoidal pixel index",
                                                                shape=(10,),
                                                                range = (0,90352))))
    coords.append(Coord(array([1,2,3,4,5,6,7,8,9,10]), Metadata(name="lon",
                                                                long_name="Longitude",
                                                                shape=(10,),
                                                                units="degrees_east",
                                                                range=(-180, 180),
                                                                missing_value=-999), "X"))
    coords.append(Coord(array([3,5,3,1,8,5,3,2,6,31]), Metadata(name="lat",
                                                                long_name="Latitude",
                                                                shape=(10,),
                                                                units="degrees_north",
                                                                range=(-90, 90),
                                                                missing_value=-999), "Y"))
    coords.append(Coord(array([7,8,9,10,11,12,13,14,15,16]), Metadata(name="time",
                                                                      long_name="TAI70 time",
                                                                      shape=(10,),
                                                                      units="seconds",
                                                                      range=(1,-1),
                                                                      missing_value=0), "T"))

    data = array([6,43,86,25,86,12,95,45,73,87])
    metadata = Metadata(name='rain',
                        long_name='Long Rain',
                        shape=(10,),
                        units='Rain units',
                        range=(0,100),
                        missing_value='-999')
    data_object = UngriddedData(data, metadata, coords)
    write(data_object, "ungridded_netcdf.nc")

def test_read():
    from data_io.products.AProducts import get_data

    filenames = ["ungridded_netcdf.nc"]
    data_object = get_data(filenames, 'rain',"Cloud_CCI")

    from jasmin_cis.plot import Plotter

    Plotter([data_object])


test_main()

test_read()