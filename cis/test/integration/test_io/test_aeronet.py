import unittest

from cis.test.integration_test_data import valid_aeronet_filename, valid_aeronet_variable
from cis.data_io.aeronet import load_aeronet
from nose.tools import assert_almost_equal, raises, assert_equal
from cis.exceptions import InvalidVariableError


class TestAeronet(unittest.TestCase):

    def test_aeronet_variable_name_parsing(self):
        from cf_units import Unit
        from cis import read_data_list

        aeronet_data = read_data_list(valid_aeronet_filename, ["AOT_440", "Water(cm)"])

        assert_equal(aeronet_data[0].name(), "AOT_440")
        assert_equal(aeronet_data[0].units, Unit('1'))
        assert_equal(aeronet_data[1].name(), "Water(cm)")
        assert_equal(aeronet_data[1].var_name, "Water")
        assert_equal(aeronet_data[1].units, Unit('cm'))

    def test_aeronet_time_parsing(self):
        # 1.8s
        from datetime import datetime
        from cis.time_util import cis_standard_time_unit as ct

        aeronet_data = load_aeronet(valid_aeronet_filename, [valid_aeronet_variable])

        assert_almost_equal(aeronet_data['datetime'][0], ct.date2num(datetime(2003, 9, 25, 6, 47, 9)))
        assert_almost_equal(aeronet_data['datetime'][5], ct.date2num(datetime(2003, 9, 25, 7, 10, 37)))
        assert_almost_equal(aeronet_data['datetime'][76], ct.date2num(datetime(2003, 9, 27, 13, 28, 2)))

    @raises(InvalidVariableError)
    def test_aeronet_missing_variable(self):
        aeronet_data = load_aeronet(valid_aeronet_filename, ['invalid_variable'])

