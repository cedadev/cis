'''
Module for writing data to NetCDF files
'''
from netCDF4 import Dataset
import numpy

types = {float: "f",
         numpy.int64: "i"}

index_name = 'pixel_number'

def __add_metadata(var, data):
    if data._metadata.standard_name: var.standard_name = data._metadata.standard_name
    if data._metadata.units: var.units = data._metadata.units
    if data._metadata.long_name: var.long_name = data._metadata.long_name
    if data._metadata.range : var.valid_range = data._metadata.range
    return var

def __get_missing_value(coord):
    f = coord._metadata.missing_value
    if not f and f !=0:
        f = None
    return f

#def __create_dimensions(nc_file, coords):
#    dimensions = ()
#    first_coord = True
#    for coord in coords:
#        if first_coord:
#            dimension = nc_file.createDimension(coord.name(), len(coord.data))
#            dimensions = dimensions + (coord.name(),)
#            first_coord = False
#        var = nc_file.createVariable(coord.name(), types[type(coord.data[0])], dimension._name, fill_value=__get_missing_value(coord))
#        var = __add_metadata(var, coord)
#        var[:] = coord.data
#
#    return dimensions

def __create_variable(nc_file, data):
    var = nc_file.createVariable(data.name(), types[type(data.data[0])], index_name, fill_value=__get_missing_value(data))
    var = __add_metadata(var, data)
    var[:] = data.data

    return var

def __create_index(nc_file, length):
    dimension = nc_file.createDimension(index_name, length)
    dimensions = ( index_name, )
    var = nc_file.createVariable(index_name, numpy.int32, dimensions)

    var.valid_range = (0, length)
    var[:] = numpy.arange(length)

    return dimensions


def write(data_object, filename):
    """

    @param data_object:
    @param filename:
    @return:
    """
    write_coordinates(data_object.coords(), filename)
    add_data_to_file(data_object, filename)

def write_coordinates(coords, filename):
    """

    @param coords:
    @param filename:
    @return:
    """
    netcdf_file = Dataset(filename, 'w', format="NETCDF4_CLASSIC")
    index_dim = __create_index(netcdf_file, coords[0].shape[0])
    for data in coords:
        coord = __create_variable(netcdf_file, data)
    netcdf_file.close()

def add_data_to_file(data_object, filename):
    """

    @param data_object:
    @param filename:
    @return:
    """
    netcdf_file = Dataset(filename, 'a', format="NETCDF4_CLASSIC")
    var = __create_variable(netcdf_file, data_object)
    netcdf_file.close()

def test_main():
    from ungridded_data import UngriddedData, Metadata
    from Coord import Coord
    from numpy import array
    coords = []
#    coords.append(Coord(array([1,2,3,4,5,6,7,8,9,10]), Metadata(name="pixel_number",
#                                                                long_name="Sinusoidal pixel index",
#                                                                shape=(10,),
#                                                                range = (0,90352))))
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

    print data_object.data

    from jasmin_cis.plot import Plotter

    Plotter([data_object])


test_main()

test_read()