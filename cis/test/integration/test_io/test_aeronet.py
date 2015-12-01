import unittest

from cis.test.integration_test_data import valid_aeronet_filename, valid_aeronet_variable
from cis.data_io.aeronet import load_aeronet
from nose.tools import assert_almost_equal


class TestAeronet(unittest.TestCase):

    def test_aeronet_time_parsing(self):
        # 1.8s
        from datetime import datetime
        from cis.time_util import cis_standard_time_unit as ct

        aeronet_data = load_aeronet(valid_aeronet_filename, [valid_aeronet_variable])

        assert_almost_equal(aeronet_data['datetime'][0], ct.date2num(datetime(2003, 9, 25, 6, 47, 9)))
        assert_almost_equal(aeronet_data['datetime'][5], ct.date2num(datetime(2003, 9, 25, 7, 10, 37)))
        assert_almost_equal(aeronet_data['datetime'][76], ct.date2num(datetime(2003, 9, 27, 13, 28, 2)))
