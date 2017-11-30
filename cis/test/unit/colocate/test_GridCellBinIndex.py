import unittest

from hamcrest import *
from cis.collocation.data_index import GridCellBinIndexInSlices
from cis.collocation import data_index
from cis.collocation.col_implementations import make_coord_map
from cis.test.util.mock import *
from cis.time_util import convert_datetime_to_std_time


class TestGridCellBinIndex(unittest.TestCase):

    def test_GIVEN_single_point_in_cube_WHEN_iterate_THEN_return_point_in_middle(self):

        sample_cube = make_square_5x3_2d_cube_with_time(offset=0, time_offset=0)
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0))
        coord_map = make_coord_map(sample_cube, data_point)
        coords = sample_cube.coords()
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            if coord.ndim > 1:
                raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                          " than one is not supported (coordinate %s)", coord.name())
            # Ensure that bounds exist.
            if not coord.has_bounds():
                coord.guess_bounds()

        index = GridCellBinIndexInSlices()
        index.index_data(coords, data_point.get_non_masked_points(), coord_map)
        iterator = index.get_data_iterator(False, data_point.get_non_masked_points(), sample_cube)

        final_points_index = [(out_index, hp, points) for out_index, hp, points in iterator]
        assert_that(len(final_points_index), is_(1), "There is one mapping from sample_cube to the final grid")
        assert_that(final_points_index[0][0], is_((2, 1, 1)), "The points should map to index")
        assert_that(final_points_index[0][1], is_(make_dummy_ungridded_data_single_point(0.0, 0.0, time=datetime.datetime(1984, 8, 28))),
                    "The points should map to index")
        assert_that(final_points_index[0][2].latitudes, is_([0.5]), "The points should map to index")
        assert_that(final_points_index[0][2].longitudes, is_([0.5]), "The points should map to index")
        assert_that(final_points_index[0][2].times,
                    is_([convert_datetime_to_std_time(datetime.datetime(1984, 8, 28, 0, 0))]),
                    "The points should map to index")
        assert_that(final_points_index[0][2].vals, is_([1.2]), "The points should map to index")

    def test_GIVEN_single_masked_point_in_cube_WHEN_iterate_THEN_return_no_points(self):

        sample_cube = make_square_5x3_2d_cube_with_time(offset=0, time_offset=0)
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0),
                                                            mask=True)
        coord_map = make_coord_map(sample_cube, data_point)
        coords = sample_cube.coords()
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            if coord.ndim > 1:
                raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                          " than one is not supported (coordinate %s)", coord.name())
            # Ensure that bounds exist.
            if not coord.has_bounds():
                coord.guess_bounds()

        index = GridCellBinIndexInSlices()
        index.index_data(coords, data_point.get_non_masked_points(), coord_map)
        iterator = index.get_data_iterator(False, data_point.get_non_masked_points(), sample_cube)

        final_points_index = [(out_index, hp, points) for out_index, hp, points in iterator]
        assert_that(len(final_points_index), is_(0), "Masked points should not be iterated over")
