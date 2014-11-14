"""Tests for creating and finding points for the aggregation grid
"""
import datetime
from nose.tools import assert_equal, with_setup

import numpy as np
from jasmin_cis.aggregation.aggregator import categorise_coord_function
from jasmin_cis.parse_datetime import date_delta_creator
import iris.unit
import iris.coords


class TestCategoriseCoordFunctionForTime:

    def __init__(self):
        self.u = iris.unit.Unit('days since 1600-01-01 00:00:00', calendar=iris.unit.CALENDAR_STANDARD)
        self.points = np.arange(1, 5, 1)
        self.coord = iris.coords.DimCoord(self.points, units=self.u)
        self.start = datetime.datetime(2000, 1, 1)
        self.end = datetime.datetime(2003, 4, 24)
        self.start = self.u.date2num(self.start)
        self.end = self.u.date2num(self.end)

    def setup_func(self):
        self.__init__()

    @with_setup(setup_func)
    def test_categorise_coord_function_time_year_only(self):
        delta = date_delta_creator(1)
        result_function = categorise_coord_function(self.start, self.end, delta, True)
        expected = np.array([self.u.date2num(datetime.datetime(2000, 7, 1, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2001, 7, 1, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2002, 7, 1, 0, 0, 0))])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2000, 1, 1, 0, 0, 0))), expected[0])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2001, 3, 3, 0, 0, 0))), expected[1])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2002, 5, 8, 0, 0, 0))), expected[2])

    @with_setup(setup_func)
    def test_categorise_coord_function_time_year_month(self):
        delta = date_delta_creator(1, 1)
        result_function = categorise_coord_function(self.start, self.end, delta, True)
        expected = np.array([self.u.date2num(datetime.datetime(2000, 7, 15, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2001, 8, 15, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2002, 9, 15, 0, 0, 0))])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2000, 1, 1, 0, 0, 0))), expected[0])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2001, 3, 3, 0, 0, 0))), expected[1])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2002, 5, 8, 0, 0, 0))), expected[2])

    @with_setup(setup_func)
    def test_categorise_coord_function_with_month_going_past_december(self):
        start = datetime.datetime(2000, 11, 3)
        start = self.u.date2num(start)
        end = datetime.datetime(2004, 11, 3)
        end = self.u.date2num(end)
        delta = date_delta_creator(1, 2)
        result_function = categorise_coord_function(start, end, delta, True)
        expected = np.array([self.u.date2num(datetime.datetime(2001, 6, 3, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2002, 8, 3, 0, 0, 0)),
                             self.u.date2num(datetime.datetime(2003, 10, 3, 0, 0, 0))])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(1999, 1, 1, 0, 0, 0))), expected[0])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2001, 3, 3, 0, 0, 0))), expected[0])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2002, 3, 3, 0, 0, 0))), expected[1])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2005, 5, 8, 0, 0, 0))), expected[2])

    @with_setup(setup_func)
    def test_categorise_coord_function_time_year_month_day_hour_minute_second(self):
        delta = date_delta_creator(1, 3, 2, 4, 5, 6)
        result_function = categorise_coord_function(self.start, self.end, delta, True)
        expected = np.array([self.u.date2num(datetime.datetime(2000, 8, 16, 2, 2, 33)),
                             self.u.date2num(datetime.datetime(2001, 11, 18, 6, 7, 39)),
                             self.u.date2num(datetime.datetime(2003, 2, 20, 10, 12, 45))])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2000, 1, 1, 0, 0, 0))), expected[0])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2001, 7, 3, 0, 0, 0))), expected[1])
        assert_equal(result_function(self.coord, self.u.date2num(datetime.datetime(2002, 9, 8, 0, 0, 0))), expected[2])


class TestCategoriseCoordFunctionForSpatial:

    def __init__(self):
        self.u = iris.unit.Unit('hPa')
        self.points = np.arange(1, 5, 1)
        self.coord = iris.coords.DimCoord(self.points, units=self.u)
        self.start = 1
        self.end = 7

    def setup_func(self):
        self.__init__()

    @with_setup(setup_func)
    def test_categorise_coord_function(self):
        delta = 1.5
        result_function = categorise_coord_function(self.start, self.end, delta, False)
        expected = np.array([1.75, 3.25, 4.75, 6.25])
        assert_equal(result_function(self.coord, -1), expected[0])
        assert_equal(result_function(self.coord, 3.25), expected[1])
        assert_equal(result_function(self.coord, 5.5), expected[2])
        assert_equal(result_function(self.coord, 6.5), expected[3])
