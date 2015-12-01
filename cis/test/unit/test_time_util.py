"""
module to test the time conversion utilities
"""
from nose.tools import istest, raises, eq_, assert_almost_equal
import datetime as dt
from unittest import TestCase

from cis.time_util import convert_sec_since_to_std_time, convert_datetime_to_std_time, \
    convert_julian_date_to_std_time


class TestTimeUtils(TestCase):

    def test_that_can_convert_tai_to_datetime_obj(self):
        import numpy as np
        sec = 1.0/(24.0*60.0*60.0)
        days_since_standard_epoch = 143541.0  # Almost, but not quite 365.2425*393.0, not sure why...

        a = np.arange(6).reshape(2, 3)
        b = convert_sec_since_to_std_time(a, dt.datetime(1993, 1, 1))

        eq_(a.shape, b.shape)
        assert_almost_equal(b[0][0], days_since_standard_epoch)
        assert_almost_equal(b[0][1], days_since_standard_epoch+1*sec)
        assert_almost_equal(b[0][2], days_since_standard_epoch+2*sec)
        assert_almost_equal(b[1][0], days_since_standard_epoch+3*sec)
        assert_almost_equal(b[1][1], days_since_standard_epoch+4*sec)
        assert_almost_equal(b[1][2], days_since_standard_epoch+5*sec)

    def test_that_can_convert_masked_tai_to_datetime_obj(self):
        import numpy.ma as ma
        sec = 1.0/(24.0*60.0*60.0)
        days_since_standard_epoch = 143541.0  # Almost, but not quite 365.2425*393.0, not sure why...

        a = ma.array([0, 1, 2, 3, 4, 5], mask=[False, False, True, False, False, False]).reshape(2, 3)
        b = convert_sec_since_to_std_time(a, dt.datetime(1993, 1, 1))

        eq_(a.shape, b.shape)
        assert_almost_equal(b[0][0], days_since_standard_epoch)
        assert_almost_equal(b[0][1], days_since_standard_epoch+1*sec)
        assert_almost_equal(b.filled()[0][2], b.fill_value)
        assert_almost_equal(b[1][0], days_since_standard_epoch+3*sec)
        assert_almost_equal(b[1][1], days_since_standard_epoch+4*sec)
        assert_almost_equal(b[1][2], days_since_standard_epoch+5*sec)

    def test_that_can_convert_julian_tai_to_datetime_obj(self):
        import numpy as np
        sec = 1.0/(24.0*60.0*60.0)
        days_since_standard_epoch = 143541.0  # Almost, but not quite 365.2425*393.0, not sure why...

        a = np.arange(6).reshape(2, 3)
        b = convert_sec_since_to_std_time(a, dt.datetime(1993, 1, 1))

        eq_(a.shape, b.shape)
        assert_almost_equal(b[0][0], days_since_standard_epoch)
        assert_almost_equal(b[0][1], days_since_standard_epoch+1*sec)
        assert_almost_equal(b[0][2], days_since_standard_epoch+2*sec)
        assert_almost_equal(b[1][0], days_since_standard_epoch+3*sec)
        assert_almost_equal(b[1][1], days_since_standard_epoch+4*sec)
        assert_almost_equal(b[1][2], days_since_standard_epoch+5*sec)


    def test_that_can_calculate_mid_point_between_two_datetime(self):
        from cis.time_util import calculate_mid_time
        t1 = convert_datetime_to_std_time(dt.datetime(2010, 02, 05, 0, 0, 0))
        t2 = convert_datetime_to_std_time(dt.datetime(2010, 02, 06, 0, 0, 0))
        tm = calculate_mid_time(t1, t2)
        eq_(tm, convert_datetime_to_std_time(dt.datetime(2010, 02, 05, 12, 0, 0)))

    def test_convert_julian_date_to_std_time(self):
        import numpy as np
        from cis.time_util import convert_std_time_to_datetime
        import datetime as dt

        a = np.array([2454637.8091, 2454637.8092, 2454637.8097,
                      2454637.8197, 2454638.8097, 2454657.8097,
                      2454737.8197, 2456638.8097, 2464657.8097,])

        b = convert_julian_date_to_std_time(a)

        # Convert back to datetimes for easy (by eye) comparison
        c = convert_std_time_to_datetime(b)

        eq_(a.shape, b.shape)
        eq_(c[0], dt.datetime(2008,6,20,7,25,6))
        eq_(c[1], dt.datetime(2008,6,20,7,25,15))
        eq_(c[2], dt.datetime(2008,6,20,7,25,58))
        eq_(c[3], dt.datetime(2008,6,20,7,40,22))
        eq_(c[4], dt.datetime(2008,6,21,7,25,58))
        eq_(c[5], dt.datetime(2008,7,10,7,25,58))
        eq_(c[6], dt.datetime(2008,9,28,7,40,22))
        eq_(c[7], dt.datetime(2013,12,12,7,25,58))
        eq_(c[8], dt.datetime(2035,11,26,7,25,58))

