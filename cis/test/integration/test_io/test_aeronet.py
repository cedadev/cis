import unittest

from cis.test.integration_test_data import valid_aeronet_filename, valid_aeronet_variable
from cis.data_io.aeronet import load_aeronet
from nose.tools import eq_


class TestAeronet(unittest.TestCase):

    def test_aeronet_time_parsing(self):
        from datetime import datetime
        aeronet_data = load_aeronet(valid_aeronet_filename, [valid_aeronet_variable])

        eq_(aeronet_data['datetime'][0], datetime(2003, 9, 25, 6, 47, 9))
        eq_(aeronet_data['datetime'][5], datetime(2003, 9, 25, 7, 10, 37))
        eq_(aeronet_data['datetime'][76], datetime(2003, 9, 27, 13, 28, 2))
