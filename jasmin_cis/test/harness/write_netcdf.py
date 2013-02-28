from jasmin_cis.data_io.write_netcdf import *


def test_main():
    from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
    from jasmin_cis.data_io.Coord import Coord
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
    metadata = Metadata(name='mass_fraction_of_cloud_liquid_water_in_air',
                        long_name='Long Rain',
                        shape=(10,),
                        units='Rain units',
                        range=(0,100),
                        missing_value='-999')
    data_object = UngriddedData(data, metadata, coords)
    print data.dtype
    write(data_object, "ungridded_netcdf.nc")

def test_read():
    from jasmin_cis.data_io.products.AProduct import get_data

    filenames = ["ungridded_netcdf.nc"]
    data_object = get_data(filenames, 'mass_fraction_of_cloud_liquid_water_in_air',"Cloud_CCI")

    print data_object.data

    from plotting.plot import Plotter

    Plotter([data_object])


test_main()

test_read()