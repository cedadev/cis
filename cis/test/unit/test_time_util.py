"""
module to test the time conversion utilities
"""
from nose.tools import eq_, assert_almost_equal, istest, raises
import datetime as dt
from unittest import TestCase

from cis.time_util import convert_sec_since_to_std_time, convert_datetime_to_std_time, \
    convert_julian_date_to_std_time, PartialDateTime, find_last_day_of_month, set_year, change_year_of_ungridded_data


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
        t1 = convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 0, 0, 0))
        t2 = convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o6, 0, 0, 0))
        tm = calculate_mid_time(t1, t2)
        eq_(tm, convert_datetime_to_std_time(dt.datetime(2010, 0o2, 0o5, 12, 0, 0)))

    def test_convert_julian_date_to_std_time(self):
        import numpy as np
        from cis.time_util import convert_datetime_to_std_time

        julian_days = np.array([2454637.8091, 2454637.8092, 2454637.8097,
                                2454637.8197, 2454638.8097, 2454657.8097,
                                2454737.8197, 2456638.8097, 2464657.8097])

        std_days = convert_julian_date_to_std_time(julian_days)

        ref = convert_datetime_to_std_time([dt.datetime(2008, 6, 20, 7, 25, 6),
                                            dt.datetime(2008, 6, 20, 7, 25, 15),
                                            dt.datetime(2008, 6, 20, 7, 25, 58),
                                            dt.datetime(2008, 6, 20, 7, 40, 22),
                                            dt.datetime(2008, 6, 21, 7, 25, 58),
                                            dt.datetime(2008, 7, 10, 7, 25, 58),
                                            dt.datetime(2008, 9, 28, 7, 40, 22),
                                            dt.datetime(2013, 12, 12, 7, 25, 58),
                                            dt.datetime(2035, 11, 26, 7, 25, 58)])

        eq_(julian_days.shape, std_days.shape)
        assert np.allclose(std_days, ref)

    # Tests for find_last_day_of_month
    def test_find_last_day_of_month_finds_day_for_dec_2010(self):
        day = find_last_day_of_month(2010, 12)
        assert (day == 31)

    def test_find_last_day_of_month_finds_day_for_feb_2000(self):
        day = find_last_day_of_month(2000, 2)
        assert (day == 29)

    # Tests for convert_datetime_components_to_datetime
    def test_convert_datetime_components_to_datetime_can_convert_year_as_lower_limit(self):
        start, end = PartialDateTime(2000).range()
        assert (start == dt.datetime(2000, 1, 1, 0, 0, 0))
        assert (end == dt.datetime(2000, 12, 31, 23, 59, 59))

    def test_convert_datetime_components_to_datetime_can_convert_year_month_as_lower_limit(self):
        start, end = PartialDateTime(1990, 6).range()
        assert (start == dt.datetime(1990, 6, 1, 0, 0, 0))
        assert (end == dt.datetime(1990, 6, 30, 23, 59, 59))

    def test_convert_datetime_components_to_datetime_can_convert_year_month_day_as_lower_limit(self):
        start, end = PartialDateTime(1990, 6, 7).range()
        assert (start == dt.datetime(1990, 6, 7, 0, 0, 0))
        assert (end == dt.datetime(1990, 6, 7, 23, 59, 59))

    def test_convert_datetime_components_to_datetime_can_convert_date_hour_as_lower_limit(self):
        start, end = PartialDateTime(1990, 6, 7, 18).range()
        assert (start == dt.datetime(1990, 6, 7, 18, 0, 0))
        assert (end == dt.datetime(1990, 6, 7, 18, 59, 59))

    def test_convert_datetime_components_to_datetime_can_convert_date_hour_min_as_lower_limit(self):
        start, end = PartialDateTime(1990, 6, 7, 6, 30).range()
        assert (start == dt.datetime(1990, 6, 7, 6, 30, 0))
        assert (end == dt.datetime(1990, 6, 7, 6, 30, 59))

    def test_convert_datetime_components_to_datetime_can_convert_date_hour_min_sec_as_lower_limit(self):
        start, end = PartialDateTime(1990, 6, 7, 12, 15, 45).range()
        assert (start == dt.datetime(1990, 6, 7, 12, 15, 45))
        assert (end == dt.datetime(1990, 6, 7, 12, 15, 45))

    @raises(ValueError)
    def test_convert_datetime_components_to_datetime_raises_error_if_invalid_date(self):
        start, end = PartialDateTime(2000, 6, 31).range()

    @raises(ValueError)
    def test_convert_datetime_components_to_datetime_raises_error_if_invalid_time(self):
        start, end = PartialDateTime(2000, 6, 30, 12, 30, 60).range()

    def test_set_year(self):
        from datetime import datetime

        # Test changing a leapday to a year without a leapday returns None
        eq_(set_year(datetime(1984, 2, 28), 2007), datetime(2007, 2, 28))
        eq_(set_year(datetime(1984, 2, 29), 2007), None)

        # Test changing a leapday to a year with a leapday works fine
        eq_(set_year(datetime(1984, 2, 28), 2000), datetime(2000, 2, 28))
        eq_(set_year(datetime(1984, 2, 29), 2000), datetime(2000, 2, 29))

    def test_change_ug_data_year(self):
        from cis.test.util.mock import make_regular_2d_with_time_ungridded_data
        from cis.time_util import convert_datetime_to_std_time
        from datetime import datetime

        ug = make_regular_2d_with_time_ungridded_data()

        change_year_of_ungridded_data(ug, 2007)

        eq_(ug.coord('time').points[0, 0], convert_datetime_to_std_time(datetime(2007, 8, 27)))
