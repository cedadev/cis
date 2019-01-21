"""
Unit tests for the top-level subsetting routines.
"""
import datetime
from unittest import TestCase
import numpy as np
from cis.data_io.gridded_data import GriddedDataList

from cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedDataList
from cis.data_io.gridded_data import make_from_cube
import cis.test.util.mock


class TestGriddedSubsetConstraint(TestCase):
    """
    Tests for subsetting gridded data
    """

    def test_null_subset_2d_gridded_data(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset()
        np.testing.assert_array_equal(subset.data, data.data)

    def test_can_subset_2d_gridded_data_by_longitude(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(longitude=[0.0, 5.0])
        assert (subset.data.tolist() == [[2, 3], [5, 6], [8, 9], [11, 12], [14, 15]])

    def test_can_subset_2d_gridded_data_by_latitude(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(latitude=[0.0, 10.0])
        assert (subset.data.tolist() == [[7, 8, 9], [10, 11, 12], [13, 14, 15]])

    def test_can_subset_2d_gridded_data_by_latitude_with_None_min(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(latitude=[0.0, None])
        assert (subset.data.tolist() == [[7, 8, 9], [10, 11, 12], [13, 14, 15]])

    def test_can_subset_2d_gridded_data_by_latitude_with_None_max(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(latitude=[None, 0.0])
        assert (subset.data.tolist() == [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_can_subset_3d_gridded_data_by_altitude(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube_with_altitude())
        subset = data.subset(altitude=[2, 5])
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_3d_gridded_data_by_pressure(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube_with_pressure())
        subset = data.subset(air_pressure=[2, 5])
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_2d_gridded_data_by_time(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube_with_time())
        subset = data.subset(time=[140494, 140497])
        assert (subset.data.tolist() == [[[3, 4, 5, 6], [10, 11, 12, 13], [17, 18, 19, 20]],
                                         [[24, 25, 26, 27], [31, 32, 33, 34], [38, 39, 40, 41]],
                                         [[45, 46, 47, 48], [52, 53, 54, 55], [59, 60, 61, 62]],
                                         [[66, 67, 68, 69], [73, 74, 75, 76], [80, 81, 82, 83]],
                                         [[87, 88, 89, 90], [94, 95, 96, 97], [101, 102, 103, 104]]])

    def test_can_subset_gridded_data_using_multiple_extract_constraints(self):
        from cis.time_util import convert_std_time_to_datetime
        data = make_from_cube(cis.test.util.mock.make_mock_cube(time_dim_length=3, alt_dim_length=6))
        subset = data.subset(time=convert_std_time_to_datetime([140492, 140493]), altitude=[0, 3])
        assert subset.data.shape == (5, 3, 3, 2)

    def test_can_subset_gridded_data_by_shape(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(shape=cis.test.util.mock.WKT_DIAMOND)
        # The corner should be masked, but the center not
        assert np.ma.is_masked(subset.data[0, 0])
        assert ~np.ma.is_masked(subset.data[2, 1])
        assert (subset.data.tolist() == [[None, 5.0, None], 
                                         [7.0, 8.0, 9.0],
                                         [None, 11.0, None]])

    def test_can_subset_2d_gridded_data_by_longitude_with_wrapping_at_180(self):
        data = make_from_cube(cis.test.util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
        long_coord = data.coord('longitude')
        long_coord.points = np.arange(-175, 185, 40)
        long_coord.bounds = None
        long_coord.guess_bounds()
        subset = data.subset(longitude=[135.0, 270])
        assert (subset.data.tolist() == [[9, 1, 2, 3],
                                         [18, 10, 11, 12],
                                         [27, 19, 20, 21],
                                         [36, 28, 29, 30],
                                         [45, 37, 38, 39]])

    def test_can_subset_2d_gridded_data_by_longitude_with_wrapping_at_360(self):
        data = make_from_cube(cis.test.util.mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
        long_coord = data.coord('longitude')
        long_coord.points = np.arange(5, 365, 40)
        long_coord.bounds = None
        long_coord.guess_bounds()
        subset = data.subset(longitude=[-45.0, 90])
        assert (subset.data.tolist() == [[9, 1, 2, 3],
                                         [18, 10, 11, 12],
                                         [27, 19, 20, 21],
                                         [36, 28, 29, 30],
                                         [45, 37, 38, 39]])

    def test_can_subset_2d_gridded_data_with_missing_data(self):
        """This test just shows that missing values do not interfere with subsetting -
        nothing special happens to the missing values.
        """
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube_with_missing_data())
        subset = data.subset(longitude=[0.0, 5.0])
        assert (subset.data.tolist(fill_value=-999) == [[2, 3], [-999, 6], [8, -999], [11, 12], [14, 15]])

    def test_can_subset_2d_gridded_data_by_longitude_latitude(self):
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(longitude=[0.0, 5.0], latitude=[-5.0, 5.0])
        assert (subset.data.tolist() == [[5, 6], [8, 9], [11, 12]])

    def test_edge_cases_with_no_bounds_for_2d_gridded_data_subset_by_longitude_latitude(self):
        """
        This test defines the behaviour for constraints set just away from cell centers when no bounds have been
        assigned to the coordinates: Namely the cell centers are treated as points with no bounds.

        This test constrains the subsetting algorithm as defined in the CIS paper so be very careful about changing it!
        """
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        subset = data.subset(longitude=[0.0, 4.5], latitude=[-5.5, 5.5])
        assert (subset.data.tolist() == [[5,], [8,], [11,]])

    def test_edge_cases_with_bounds_for_2d_gridded_data_subset_by_longitude_latitude(self):
        """
        Complementary to the test above, if bounds are assigned to the coordinates then the cells can match the
        constraint if the matching points are within - or equal to the bounds.

        This test constrains the subsetting algorithm as defined in the CIS paper so be very careful about changing it!
        """
        data = make_from_cube(cis.test.util.mock.make_square_5x3_2d_cube())
        for c in data.coords():
            c.guess_bounds()
        subset = data.subset(longitude=[0.0, 4.5], latitude=[-2.50, 2.50])
        assert (subset.data.tolist() == [[5, 6], [8, 9], [11, 12]])

    def test_empty_longitude_subset_of_gridded_data_list_returns_no_data(self):
        """
        Checks that the convention of returning None if subsetting results in an empty subset.
        Longitude has a modulus and so uses the IRIS intersection method
        """
        data = GriddedDataList([cis.test.util.mock.make_square_5x3_2d_cube()])
        subset = data.subset(longitude=[1.0, 3.0])
        assert (subset is None)

    def test_empty_time_subset_of_gridded_data_list_returns_no_data(self):
        """
        Checks that the convention of returning None if subsetting results in an empty subset.
        Longitude has no modulus and so uses the IRIS extract method
        """
        data = GriddedDataList([cis.test.util.mock.make_square_5x3_2d_cube_with_time()])
        subset = data.subset(time=[140500, 140550])
        assert (subset is None)

    def test_GIVEN_GriddedDataList_WHEN_constrain_THEN_correctly_subsetted_GriddedDataList_returned(self):
        gridded1 = cis.test.util.mock.make_square_5x3_2d_cube()
        gridded2 = cis.test.util.mock.make_square_5x3_2d_cube()
        datalist = GriddedDataList([gridded1, gridded2])
        subset = datalist.subset(longitude=[0.0, 5.0], latitude=[-5.0, 5.0])
        assert isinstance(subset, GriddedDataList)
        assert (subset[0].data.tolist() == [[5, 6], [8, 9], [11, 12]])
        assert (subset[1].data.tolist() == [[5, 6], [8, 9], [11, 12]])


class TestUngriddedSubsetConstraint(TestCase):
    # Tests for subsetting ungridded data

    def test_null_subset_of_2d_ungridded_data(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset()
        # The data gets flattened, but is otherwise equal
        np.testing.assert_array_equal(subset.data.flatten(), data.data.flatten())

    def test_can_subset_2d_ungridded_data_by_longitude(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset(longitude=[0.0, None])
        assert (subset.data.tolist() == [2, 3, 5, 6, 8, 9, 11, 12, 14, 15])

    def test_can_subset_2d_ungridded_data_by_longitude_with_None_min(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset(longitude=[None, 0.0])
        assert (subset.data.tolist() == [1, 2, 4, 5, 7, 8, 10, 11, 13, 14])

    def test_can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_180(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data(
            lat_dim_length=5, lon_dim_length=9, lon_min=-175., lon_max=145.)
        subset = data.subset(longitude=[135.0, 270.0])
        assert (subset.data.tolist() == [1, 2, 3, 9, 10, 11, 12, 18, 19, 20, 21, 27, 28, 29, 30, 36, 37, 38, 39, 45])

    def test_can_subset_2d_ungridded_data_by_longitude_with_wrapping_at_360(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data(
            lat_dim_length=5, lon_dim_length=9, lon_min=5., lon_max=325.)
        subset = data.subset(longitude=[-45.0, 90.0])
        assert (subset.data.tolist() == [1, 2, 3, 9, 10, 11, 12, 18, 19, 20, 21, 27, 28, 29, 30, 36, 37, 38, 39, 45])

    def test_original_data_not_altered_when_subsetting(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset(longitude=[0.0, 5.0], latitude=[-5.0, 5.0])
        assert len(data.data_flattened) == 15
        assert len(data.coord('longitude').data_flattened) == 15

    def test_can_subset_2d_ungridded_data_by_longitude_latitude(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset(longitude=[0.0, 5.0], latitude=[-5.0, 5.0])
        assert (subset.data.tolist() == [5, 6, 8, 9, 11, 12])

    def test_empty_subset_of_ungridded_data_returns_no_data(self):
        """Checks that the convention of returning None if subsetting results in an empty subset.
        """
        data = cis.test.util.mock.make_regular_2d_ungridded_data()
        subset = data.subset(longitude=[1.0, 3.0])
        assert (subset is None)

    def test_can_subset_ungridded_data_by_time(self):
        data = cis.test.util.mock.make_regular_4d_ungridded_data()
        subset = data.subset(time=[datetime.datetime(1984, 8, 28), datetime.datetime(1984, 8, 29)])
        assert (subset.data.tolist() == [2, 3, 7, 8, 12, 13, 17, 18, 22, 23, 27, 28, 32, 33, 37, 38, 42, 43, 47, 48])

    def test_can_subset_ungridded_data_by_partial_date_time(self):
        from cis.time_util import PartialDateTime
        data = cis.test.util.mock.make_dummy_ungridded_data_time_series(100)
        subset = data.subset(time=[PartialDateTime(1984, 9)])
        assert (subset.data.tolist() == [6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
                                         20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0,
                                         33.0, 34.0, 35.0])

    def test_can_subset_ungridded_data_by_time_altitude(self):
        data = cis.test.util.mock.make_regular_4d_ungridded_data()
        subset = data.subset(time=[datetime.datetime(1984, 8, 28), datetime.datetime(1984, 8, 29)],
                             altitude=[45.0, 75.0])
        assert (subset.data.tolist() == [27, 28, 32, 33, 37, 38])

    def test_can_subset_ungridded_data_by_shape(self):
        data = cis.test.util.mock.make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        subset = data.subset(shape=cis.test.util.mock.WKT_DIAMOND)
        # The corners should be masked, but the center not
        assert (subset.data.tolist() == [5, 7, 8, 9, 11])

    def test_can_subset_ungridded_data_by_shape_and_time(self):
        data = cis.test.util.mock.make_regular_2d_with_time_ungridded_data()
        data.time.convert_to_std_time()
        subset = data.subset(shape=cis.test.util.mock.WKT_DIAMOND, time=[datetime.datetime(1984, 8, 28),
                                                                         datetime.datetime(1984, 9, 3)])
        assert (subset.data.tolist() == [5, 7, 8])

    def test_can_subset_2d_ungridded_data_with_missing_values(self):
        data = cis.test.util.mock.make_regular_2d_ungridded_data_with_missing_values()
        subset = data.subset(longitude=[0.0, 5.0])
        assert (subset.data.tolist() == [2, 3, None, 6, 8, None, 11, 12, 14, 15])

    def test_GIVEN_UngriddedDataList_WHEN_constrain_THEN_correctly_subsetted_UngriddedDataList_returned(self):
        ug_data = cis.test.util.mock.make_regular_2d_ungridded_data()
        ug_data2 = UngriddedData(ug_data.data + 1, Metadata(name='snow', standard_name='snowfall_flux',
                                                            long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S",
                                                            units="kg m-2 s-1", missing_value=-999), ug_data.coords())
        datalist = UngriddedDataList([ug_data, ug_data2])
        subset = datalist.subset(longitude=[0.0, 5.0], latitude=[-5.0, 10.0])

        assert isinstance(subset, UngriddedDataList)
        assert subset[0].data.tolist() == [5, 6, 8, 9, 11, 12, 14, 15]
        assert subset[1].data.tolist() == [6, 7, 9, 10, 12, 13, 15, 16]
