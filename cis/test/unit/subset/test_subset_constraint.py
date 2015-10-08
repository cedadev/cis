"""Tests for subset_constraint module
"""
import datetime
from unittest import TestCase
import numpy as np
from cis.data_io.gridded_data import GriddedDataList

from cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedDataList
import cis.subsetting.subset_constraint as subset_constraint
import cis.test.util.mock
import cis.time_util as time_util


class TestGriddedSubsetConstraint(TestCase):
    """
    Tests for subsetting gridded data
    """

    def test_can_subset_2d_gridded_data_by_longitude(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube()
        long_coord = data.coord('longitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[2, 3], [5, 6], [8, 9], [11, 12], [14, 15]])

    def test_can_subset_2d_gridded_data_by_latitude(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube()
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(lat_coord, 0.0, 10.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[7, 8, 9], [10, 11, 12], [13, 14, 15]])

    def test_can_subset_3d_gridded_data_by_altitude(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube_with_altitude()
        alt_coord = data.coord('altitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(alt_coord, 2, 5)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_3d_gridded_data_by_pressure(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube_with_pressure()
        press_coord = data.coord('air_pressure')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(press_coord, 2, 5)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_2d_gridded_data_by_time(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube_with_time()
        time_coord = data.coord('time')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(time_coord, 140494, 140497)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_2d_gridded_data_by_longitude_with_wrapping_at_180(self):
        data = cis.test.util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9)
        long_coord = data.coord('longitude')
        long_coord.points = np.arange(-175, 185, 40)
        long_coord.bounds = None
        long_coord.guess_bounds()
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 135.0, 270)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[9, 1, 2, 3],
                                         [18, 10, 11, 12],
                                         [27, 19, 20, 21],
                                         [36, 28, 29, 30],
                                         [45, 37, 38, 39]])

    def test_can_subset_2d_gridded_data_by_longitude_with_wrapping_at_360(self):
        data = cis.test.util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9)
        long_coord = data.coord('longitude')
        long_coord.points = np.arange(5, 365, 40)
        long_coord.bounds = None
        long_coord.guess_bounds()
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, -45.0, 90.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[9, 1, 2, 3],
                                         [18, 10, 11, 12],
                                         [27, 19, 20, 21],
                                         [36, 28, 29, 30],
                                         [45, 37, 38, 39]])

    def test_can_subset_2d_gridded_data_with_missing_data(self):
        """This test just shows that missing values do not interfere with subsetting -
        nothing special happens to the missing values.
        """
        data = cis.test.util.mock.make_square_5x3_2d_cube_with_missing_data()
        long_coord = data.coord('longitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist(fill_value=-999) == [[2, 3], [-999, 6], [8, -999], [11, 12], [14, 15]])

    def test_can_subset_2d_gridded_data_by_longitude_latitude(self):
        data = cis.test.util.mock.make_square_5x3_2d_cube()
        long_coord = data.coord('longitude')
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        constraint.set_limit(lat_coord, -5.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[5, 6], [8, 9], [11, 12]])

    def test_edge_cases_with_no_bounds_for_2d_gridded_data_subset_by_longitude_latitude(self):
        """
        This test defines the behaviour for constraints set just away from cell centers when no bounds have been
        assigned to the coordinates: Namely the cell centers are treated as points with no bounds.

        This test constrains the subsetting algorithm as defined in the CIS paper so be very careful about changing it!
        """
        data = cis.test.util.mock.make_square_5x3_2d_cube()
        long_coord = data.coord('longitude')
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 4.5)
        constraint.set_limit(lat_coord, -5.5, 5.5)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[5,], [8,], [11,]])

    def test_edge_cases_with_bounds_for_2d_gridded_data_subset_by_longitude_latitude(self):
        """
        Complementary to the test above, if bounds are assigned to the coordinates then the cells can match the
        constraint if the matching points are within - or equal to the bounds.

        This test constrains the subsetting algorithm as defined in the CIS paper so be very careful about changing it!
        """
        data = cis.test.util.mock.make_square_5x3_2d_cube()
        for c in data.coords():
            c.guess_bounds()
        long_coord = data.coord('longitude')
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 4.5)
        constraint.set_limit(lat_coord, -2.50, 2.50)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [[5, 6], [8, 9], [11, 12]])

    def test_empty_longitude_subset_of_gridded_data_list_returns_no_data(self):
        """
        Checks that the convention of returning None if subsetting results in an empty subset.
        Longitude has a modulus and so uses the IRIS intersection method
        """
        data = GriddedDataList([cis.test.util.mock.make_square_5x3_2d_cube()])
        long_coord = data.coord('longitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 1.0, 3.0)
        subset = constraint.constrain(data)
        assert (subset is None)

    def test_empty_time_subset_of_gridded_data_list_returns_no_data(self):
        """
        Checks that the convention of returning None if subsetting results in an empty subset.
        Longitude has no modulus and so uses the IRIS extract method
        """
        data = GriddedDataList([cis.test.util.mock.make_square_5x3_2d_cube_with_time()])
        long_coord = data.coord('time')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 140500, 140550)
        subset = constraint.constrain(data)
        assert (subset is None)

    def test_GIVEN_GriddedDataList_WHEN_constrain_THEN_correctly_subsetted_GriddedDataList_returned(self):
        gridded1 = cis.test.util.mock.make_square_5x3_2d_cube()
        gridded2 = cis.test.util.mock.make_square_5x3_2d_cube()
        datalist = GriddedDataList([gridded1, gridded2])
        long_coord = gridded1.coord('longitude')
        lat_coord = gridded1.coord('latitude')
        constraint = subset_constraint.GriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        constraint.set_limit(lat_coord, -5.0, 5.0)
        subset = constraint.constrain(datalist)
        assert isinstance(subset, GriddedDataList)
        assert (subset[0].data.tolist() == [[5, 6], [8, 9], [11, 12]])
        assert (subset[1].data.tolist() == [[5, 6], [8, 9], [11, 12]])


class TestUngriddedSubsetConstraint(TestCase):
    # Tests for subsetting ungridded data

    def test_can_subset_2d_ungridded_data_by_longitude(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        long_coord = data.coord('longitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [2, 3, 5, 6, 8, 9, 11, 12, 14, 15])

    def test_can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_180(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data(
            lat_dim_length=5, lon_dim_length=9, lon_min=-175., lon_max=145.)
        long_coord = data.coord('longitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 135.0, 270.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [1, 2, 3, 9, 10, 11, 12, 18, 19, 20, 21, 27, 28, 29, 30, 36, 37, 38, 39, 45])

    def test_can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_360(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data(
            lat_dim_length=5, lon_dim_length=9, lon_min=5., lon_max=325.)
        long_coord = data.coord('longitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, -45.0, 90.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [1, 2, 3, 9, 10, 11, 12, 18, 19, 20, 21, 27, 28, 29, 30, 36, 37, 38, 39, 45])

    def test_original_data_not_altered_when_subsetting(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        long_coord = data.coord('longitude')
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        constraint.set_limit(lat_coord, -5.0, 5.0)
        subset = constraint.constrain(data)
        assert len(data.data_flattened) == 15
        assert len(data.coord('longitude').data_flattened) == 15

    def test_can_subset_2d_ungridded_data_by_longitude_latitude(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        long_coord = data.coord('longitude')
        lat_coord = data.coord('latitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        constraint.set_limit(lat_coord, -5.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [5, 6, 8, 9, 11, 12])

    def test_empty_subset_of_ungridded_data_returns_no_data(self):
        """Checks that the convention of returning None if subsetting results in an empty subset.
        """
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        long_coord = data.coord('longitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 1.0, 3.0)
        subset = constraint.constrain(data)
        assert (subset is None)

    def test_can_subset_ungridded_data_by_time(self):
        data = cis.test.util.mock.make_regular_4d_ungridded_data()
        time_coord = data.coord('time')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(time_coord,
                             time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 28)),
                             time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 29)))
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [2, 3, 7, 8, 12, 13, 17, 18, 22, 23, 27, 28, 32, 33, 37, 38, 42, 43, 47, 48])

    def test_can_subset_ungridded_data_by_time_altitude(self):
        data = cis.test.util.mock.make_regular_4d_ungridded_data()
        time_coord = data.coord('time')
        alt_coord = data.coord('altitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(time_coord,
                             time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 28)),
                             time_util.convert_datetime_to_std_time(datetime.datetime(1984, 8, 29)))
        constraint.set_limit(alt_coord, 45.0, 75.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [27, 28, 32, 33, 37, 38])

    def test_can_subset_2d_ungridded_data_with_missing_values(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data_with_missing_values()
        long_coord = data.coord('longitude')
        constraint = subset_constraint.UngriddedSubsetConstraint()
        constraint.set_limit(long_coord, 0.0, 5.0)
        subset = constraint.constrain(data)
        assert (subset.data.tolist() == [2, 3, -999, 6, 8, -999, 11, 12, 14, 15])

    def test_GIVEN_UngriddedDataList_WHEN_constrain_THEN_correctly_subsetted_UngriddedDataList_returned(self):
        ug_data = cis.test.util.mock.make_regular_2d_ungridded_data()
        ug_data2 = UngriddedData(ug_data.data + 1, Metadata(name='snow', standard_name='snowfall_rate',
                                                            long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S",
                                                            units="kg m-2 s-1", missing_value=-999), ug_data.coords())
        constraint = subset_constraint.UngriddedSubsetConstraint()
        xmin, xmax = 0, 5
        ymin, ymax = -5, 10
        constraint.set_limit(ug_data.coord(standard_name='longitude'), xmin, xmax)
        constraint.set_limit(ug_data.coord(standard_name='latitude'), ymin, ymax)
        subset = constraint.constrain(UngriddedDataList([ug_data, ug_data2]))
        assert isinstance(subset, UngriddedDataList)
        assert subset[0].data.tolist() == [5, 6, 8, 9, 11, 12, 14, 15]
        assert subset[1].data.tolist() == [6, 7, 9, 10, 12, 13, 15, 16]
