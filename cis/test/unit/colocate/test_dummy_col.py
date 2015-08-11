import unittest

import numpy

from cis.data_io.ungridded_data import UngriddedDataList
import cis.test.util.mock as mock
from cis.collocation.col_implementations import DummyCollocator


class TestDummyCollocator(unittest.TestCase):
    
    def test_single_data(self):
        sample = mock.make_regular_2d_ungridded_data()
        data = mock.make_regular_2d_ungridded_data(data_offset=10)
        col = DummyCollocator()
        con = None
        kernel = None

        output = col.collocate(sample, data, con, kernel)

        assert len(output) == 1
        assert numpy.array_equal(output[0].data, data.data)

    def test_list_of_data(self):
        sample = mock.make_regular_2d_ungridded_data()
        data = UngriddedDataList([mock.make_regular_2d_ungridded_data(data_offset=5),
                                  mock.make_regular_2d_ungridded_data(data_offset=10)])
        col = DummyCollocator()
        con = None
        kernel = None

        output = col.collocate(sample, data, con, kernel)

        assert len(output) == 2
        assert numpy.array_equal(output[0].data, data[0].data)
        assert numpy.array_equal(output[1].data, data[1].data)

if __name__ == '__main__':
    unittest.main()
