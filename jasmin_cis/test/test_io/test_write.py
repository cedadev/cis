from jasmin_cis.test.test_util.mock import MockCoord, MockUngriddedData
from jasmin_cis.test.test_util.mock import gen_random_data

def test__write_netcdf():
    from jasmin_cis.data_io.write_netcdf import write_to_file
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8]
    data = [[0.1, 0.5, 0.6, 0.2, 0.9],[0.2, 3.5, 0.6, 2.2, 0.9],[4.1, 5.5, 2.2, 2.2, 0.2],[0.2, 5.5, 6.6, 0.7, 6.9]]
    coords = [MockCoord("latitude"), MockCoord("longitude")]
    data_object = MockUngriddedData(x, y, data, "TOTAL RAINFALL RATE: LS+CONV KG/M2/S", "kg m-2 s-1", coords, "f", "rain")
    write_to_file(data_object, "test_netcdf_file")
    
def test__write_hdf():
    from numpy import array
    from jasmin_cis.data_io.write_hdf import write
    x = array((gen_random_data(), gen_random_data(), gen_random_data(), gen_random_data()))
    y = array((gen_random_data(), gen_random_data(), gen_random_data(), gen_random_data()))
    data = array((gen_random_data(), gen_random_data(), gen_random_data(), gen_random_data()))
    coords = [MockCoord("coord1"), MockCoord("coord2")]
    obj = MockUngriddedData(x, y, data, "long rain", "units", coords, "f", "short rain")
    write(obj, "WALDM.hdf")