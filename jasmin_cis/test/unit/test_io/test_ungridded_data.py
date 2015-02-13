"""Tests for ungridded_data module
"""
from unittest import TestCase
from hamcrest import assert_that, is_, contains_inanyorder

import numpy as np

from jasmin_cis.data_io.Coord import CoordList, Coord
from jasmin_cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, Metadata, UngriddedDataList


class TestUngriddedData(TestCase):

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

    def test_GIVEN_numpy_array_data_with_missing_coordinate_values_WHEN_data_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(data, Metadata(), coords)
        data = ug.data.flatten()
        assert_that(len(data), is_(14))

    def test_GIVEN_lazy_load_data_with_missing_coordinate_values_WHEN_data_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        data = ug.data.flatten()
        assert_that(len(data), is_(14))


class TestUngriddedCoordinates(TestCase):

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


class TestUngriddedDataList(TestCase):

    def test_GIVEN_grids_contain_multiple_matching_coordinates_WHEN_coords_THEN_only_unique_coords_returned(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        x = Coord(x, Metadata(name='lat', standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(name='lon', standard_name='longitude', units='degrees'))
        data = np.reshape(np.arange(15) + 1.0, (5, 3))
        coords = CoordList([x, y])

        ug1 = UngriddedData(data, Metadata(standard_name='rain', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                           units="kg m-2 s-1", missing_value=-999), coords)
        ug2 = UngriddedData(data * 0.1, Metadata(standard_name='snow', long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S",
                                                 units="kg m-2 s-1", missing_value=-999), coords)
        ungridded_data_list = UngriddedDataList([ug1, ug2])

        unique_coords = ungridded_data_list.coords()
        assert_that(len(unique_coords), is_(2))
        assert_that(isinstance(unique_coords, CoordList))
        coord_names = [coord.standard_name for coord in unique_coords]
        assert_that(coord_names, contains_inanyorder('latitude', 'longitude'))

if __name__ == '__main__':
    import nose
    nose.runmodule()
