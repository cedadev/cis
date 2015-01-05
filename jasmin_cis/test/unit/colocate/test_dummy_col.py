import unittest
import numpy

from jasmin_cis.data_io.ungridded_data import UngriddedDataList
import jasmin_cis.test.util.mock as mock
from jasmin_cis.col_implementations import DummyColocator


class TestDummyColocator(unittest.TestCase):
    
    def test_single_data(self):
        sample = mock.make_regular_2d_ungridded_data()
        data = mock.make_regular_2d_ungridded_data(data_offset=10)
        col = DummyColocator()
        con = None
        kernel = None

        output = col.colocate(sample, data, con, kernel)

        assert len(output) == 1
        assert numpy.array_equal(output[0].data, data.data)

    def test_list_of_data(self):
        sample = mock.make_regular_2d_ungridded_data()
        data = UngriddedDataList([mock.make_regular_2d_ungridded_data(data_offset=5),
                                  mock.make_regular_2d_ungridded_data(data_offset=10)])
        col = DummyColocator()
        con = None
        kernel = None

        output = col.colocate(sample, data, con, kernel)

        assert len(output) == 2
        assert numpy.array_equal(output[0].data, data[0].data)
        assert numpy.array_equal(output[1].data, data[1].data)

if __name__ == '__main__':
    unittest.main()
