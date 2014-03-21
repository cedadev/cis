"""Tests for ungridded_data module
"""
from nose.tools import istest, nottest, raises

import numpy as np

from jasmin_cis.data_io.Coord import CoordList, Coord
from jasmin_cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, Metadata


class TestUngriddedData(object):
    @istest
    def test_can_create_ungridded_data(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        coords = CoordList([x, y])
        ug = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                          units="kg m-2 s-1", missing_value=-999), coords)
        standard_coords = ug.coords().find_standard_coords()
        assert(standard_coords == [x, y, None, None, None])
        assert(ug.data.size == 15)


    @istest
    def test_get_all_points_returns_points(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        coords = CoordList([x, y])
        ug = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                          units="kg m-2 s-1", missing_value=-999), coords)
        points = ug.get_all_points()
        num_points = len([p for p in points])
        assert(num_points == 15)


    @istest
    def test_get_non_masked_points_returns_points(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        values = np.ma.arange(15) + 1.0
        values[4] = np.ma.masked
        values[8] = np.ma.masked
        values[12] = np.ma.masked
        data = np.reshape(values, (5, 3))

        coords = CoordList([x, y])
        ug = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                          units="kg m-2 s-1", missing_value=-999), coords)
        points = ug.get_non_masked_points()
        num_points = len([p for p in points])
        assert(num_points == 12)


    @istest
    def test_get_coordinates_points_returns_points(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        values = np.ma.arange(15) + 1.0
        values[4] = np.ma.masked
        values[8] = np.ma.masked
        values[12] = np.ma.masked
        data = np.reshape(values, (5, 3))

        coords = CoordList([x, y])
        ug = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                          units="kg m-2 s-1", missing_value=-999), coords)
        points = ug.get_coordinates_points()
        num_points = len([p for p in points])
        assert(num_points == 15)


    @istest
    def test_can_add_history(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        coords = CoordList([x, y])
        ug = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                          units="kg m-2 s-1", missing_value=-999), coords)

        new_history = 'This is a new history entry.'
        ug.add_history(new_history)
        assert(ug.metadata.history.find(new_history) >= 0)


class TestUngriddedCoordinates(object):
    @istest
    def test_can_create_ungridded_coordinates(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))

        coords = CoordList([x, y])
        ug = UngriddedCoordinates(coords)
        standard_coords = ug.coords().find_standard_coords()
        assert(standard_coords == [x, y, None, None, None])


    @istest
    def test_get_coordinates_points_returns_points(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))

        coords = CoordList([x, y])
        ug = UngriddedCoordinates(coords)
        points = ug.get_coordinates_points()
        num_points = len([p for p in points])
        assert(num_points == 15)


if __name__ == '__main__':
    import nose
    nose.runmodule()
