from nose.tools import istest, nottest, raises
import numpy as np

from jasmin_cis.data_io.hyperpoint_view import UngriddedHyperPointView, GriddedHyperPointView
import jasmin_cis.test.util.mock as mock
import jasmin_cis.data_io.gridded_data as gridded_data


class TestUngriddedHyperPointView(object):
    """
    Unit tests for UngriddedHyperPointView class
    """
    @istest
    def test_can_create_ungridded_hyper_point_view(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        all_coords = ug._coords.find_standard_coords()
        flattened_coords = [(c.data_flattened if c is not None else None) for c in all_coords]
        hpv = UngriddedHyperPointView(flattened_coords, ug.data_flattened)
        assert(len(hpv) == 15)

    @istest
    def test_can_access_point_in_ungridded_hyper_point_view(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_all_points()
        p = hpv[10]
        assert(p.val[0] == 11.0)
        assert(p.longitude == 0.0)
        assert(p.latitude == 5.0)

    @istest
    @raises(IndexError)
    def test_accessing_with_invalid_index_raises_error(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_all_points()
        p = hpv[16]

    @istest
    def test_can_iterate_over_all_points(self):
        ug = mock.make_regular_2d_ungridded_data()
        hpv = ug.get_all_points()
        count = 0
        vals = []
        for p in hpv:
            count += 1
            vals.append(p.val[0])
        assert(count == 15)
        assert(vals == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    @istest
    def test_can_iterate_over_non_masked_points(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_non_masked_points()
        count = 0
        vals = []
        for p in hpv:
            count += 1
            vals.append(p.val[0])
        assert(count == 12)
        assert(vals == [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15])

    @istest
    def test_can_enumerate_non_masked_points(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_non_masked_points()
        count = 0
        indices = []
        vals = []
        for i, p in hpv.enumerate_non_masked_points():
            count += 1
            indices.append(i)
            vals.append(p.val[0])
        assert(count == 12)
        assert(indices == [0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14])
        assert(vals == [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15])

    @istest
    def test_can_set_a_hyperpoint(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_all_points()
        p = hpv[6]
        p_new = p.modified(lon=123, val=99)
        hpv[6] = p_new
        p = hpv[6]
        assert(p.latitude == 0)
        assert(p.longitude == 123)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[5]
        assert(p.latitude == -5)
        assert(p.longitude == 5)
        assert(p.val[0] == 6)

    @istest
    def test_can_modify_a_hyperpoint_value(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_all_points()
        hpv[6] = 99
        p = hpv[6]
        assert(p.latitude == 0)
        assert(p.longitude == -5)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[5]
        assert(p.latitude == -5)
        assert(p.longitude == 5)
        assert(p.val[0] == 6)

    @istest
    def test_can_set_longitude_wrap_at_180(self):
        ug = mock.make_regular_2d_ungridded_data(lat_dim_length=5, lat_min=-90, lat_max=90,
                                                 lon_dim_length=9, lon_min=0, lon_max=360)
        hpv = ug.get_non_masked_points()
        hpv.set_longitude_range(-180.0)
        assert(np.min(hpv.longitudes) >= -180.0)
        assert(np.max(hpv.longitudes) < 180.0)
        assert(hpv[0].longitude == 0.0)
        assert(hpv[36].longitude == 0.0)
        assert(hpv[4].longitude == -180.0)
        assert(hpv[40].longitude == -180.0)
        assert(hpv[7].longitude == -45.0)
        assert(hpv[43].longitude == -45.0)
        assert(hpv[8].longitude == 0.0)
        assert(hpv[44].longitude == 0.0)

    @istest
    def test_can_set_longitude_wrap_at_360(self):
        ug = mock.make_regular_2d_ungridded_data(lat_dim_length=5, lat_min=-90, lat_max=90,
                                                 lon_dim_length=9, lon_min=-180, lon_max=180)
        hpv = ug.get_non_masked_points()
        hpv.set_longitude_range(0.0)
        assert(np.min(hpv.longitudes) >= 0.0)
        assert(np.max(hpv.longitudes) < 360.0)
        assert(hpv[0].longitude == 180.0)
        assert(hpv[36].longitude == 180.0)
        assert(hpv[1].longitude == 225.0)
        assert(hpv[37].longitude == 225.0)
        assert(hpv[4].longitude == 0.0)
        assert(hpv[40].longitude == 0.0)
        assert(hpv[8].longitude == 180.0)
        assert(hpv[44].longitude == 180.0)


class TestGriddedHyperPointView(object):
    """
    Unit tests for GriddedHyperPointView class
    """
    @istest
    def test_can_create_gridded_hyper_point_view(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        all_coords = [((c[0].points, c[1]) if c is not None else None) for c in gd.find_standard_coords()]
        hpv = GriddedHyperPointView(all_coords, gd.data)
        assert(len(hpv) == 15)

    @istest
    def test_can_access_point_in_gridded_hyper_point_view_(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_all_points()
        p = hpv[3, 1]
        assert(p.val[0] == 11.0)
        assert(p.longitude == 5.0)
        assert(p.latitude == 0.0)

    @istest
    @raises(IndexError)
    def test_accessing_with_invalid_index_raises_error(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_all_points()
        p = hpv[2, 3]

    @istest
    @raises(IndexError)
    def test_accessing_with_invalid_flat_index_raises_error(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_all_points()
        p = hpv[16]

    @istest
    def test_can_iterate_over_all_points(self):
        gd = gridded_data.make_from_cube(mock.make_square_5x3_2d_cube())
        hpv = gd.get_all_points()
        count = 0
        vals = []
        for p in hpv:
            count += 1
            vals.append(p.val[0])
        assert(count == 15)
        assert(vals == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    @istest
    def test_can_iterate_over_non_masked_points(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        count = 0
        vals = []
        for p in hpv:
            count += 1
            vals.append(p.val[0])
        assert(count == 12)
        assert(vals == [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15])

    @istest
    def test_can_enumerate_non_masked_points(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        count = 0
        indices = []
        vals = []
        for i, p in hpv.enumerate_non_masked_points():
            count += 1
            indices.append(i)
            vals.append(p.val[0])
        assert(count == 12)
        assert(indices == [0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14])
        assert(vals == [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15])

    @istest
    def test_can_set_a_hyperpoint_via_flat_index(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        p = hpv[6]
        p_new = p.modified(lon=123, val=99)
        hpv[6] = p_new
        p = hpv[6]
        assert(p.latitude == -5)
        # Note: the coordinates cannot be changed for GriddedHyperPointView.
        assert(p.longitude == 0)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[5]
        assert(p.latitude == 5)
        assert(p.longitude == -5)
        assert(p.val[0] == 6)

    @istest
    def test_can_set_a_hyperpoint(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        p = hpv[2, 0]
        p_new = p.modified(lon=123, val=99)
        hpv[6] = p_new
        p = hpv[2, 0]
        assert(p.latitude == -5)
        # Note: the coordinates cannot be changed for GriddedHyperPointView.
        assert(p.longitude == 0)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[1, 2]
        assert(p.latitude == 5)
        assert(p.longitude == -5)
        assert(p.val[0] == 6)

    @istest
    @raises(ValueError)
    def test_setting_new_hyperpoint_coord_can_raise_exception(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        hpv._verify_no_coord_change_on_setting = True
        p = hpv[6]
        p_new = p.modified(lon=123, val=99)
        hpv[6] = p_new

    @istest
    def test_can_modify_a_hyperpoint_value(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        hpv[2, 0] = 99
        p = hpv[2, 0]
        assert(p.latitude == -5)
        assert(p.longitude == 0)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[1, 2]
        assert(p.latitude == 5)
        assert(p.longitude == -5)
        assert(p.val[0] == 6)

    @istest
    def test_can_modify_a_hyperpoint_value_via_flat_index(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_non_masked_points()
        hpv[6] = 99
        p = hpv[6]
        assert(p.latitude == -5)
        assert(p.longitude == 0)
        assert(p.val[0] == 99)
        # Check an unmodified point.
        p = hpv[5]
        assert(p.latitude == 5)
        assert(p.longitude == -5)
        assert(p.val[0] == 6)

    @istest
    def test_can_set_longitude_wrap_at_180(self):
        gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
        long_coord = gd.coord('longitude')
        long_coord.points = np.array([0., 45., 90., 135., 180., 225., 270., 315., 360.])
        long_coord.bounds = None
        long_coord.guess_bounds()
        hpv = gd.get_non_masked_points()
        hpv.set_longitude_range(-180.0)
        assert(np.min(hpv.longitudes) >= -180.0)
        assert(np.max(hpv.longitudes) < 180.0)
        assert(hpv[0, 0].longitude == 0.0)
        assert(hpv[4, 0].longitude == 0.0)
        assert(hpv[0, 4].longitude == -180.0)
        assert(hpv[4, 4].longitude == -180.0)
        assert(hpv[0, 7].longitude == -45.0)
        assert(hpv[4, 7].longitude == -45.0)
        assert(hpv[0, 8].longitude == 0.0)
        assert(hpv[4, 8].longitude == 0.0)

    @istest
    def test_can_set_longitude_wrap_at_360(self):
        gd = gridded_data.make_from_cube(mock.make_mock_cube(lat_dim_length=5, lon_dim_length=9))
        long_coord = gd.coord('longitude')
        long_coord.points = np.array([-180., -135., -90., -45., 0., 45., 90., 135., 180.])
        long_coord.bounds = None
        long_coord.guess_bounds()
        hpv = gd.get_non_masked_points()
        hpv.set_longitude_range(0.0)
        assert(np.min(hpv.longitudes) >= 0.0)
        assert(np.max(hpv.longitudes) < 360.0)
        assert(hpv[0, 0].longitude == 180.0)
        assert(hpv[4, 0].longitude == 180.0)
        assert(hpv[0, 1].longitude == 225.0)
        assert(hpv[4, 1].longitude == 225.0)
        assert(hpv[0, 4].longitude == 0.0)
        assert(hpv[4, 4].longitude == 0.0)
        assert(hpv[0, 8].longitude == 180.0)
        assert(hpv[4, 8].longitude == 180.0)


# if __name__ == '__main__':
#     import nose
#     nose.runmodule()
