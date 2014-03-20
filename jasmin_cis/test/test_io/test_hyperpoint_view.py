from nose.tools import istest, nottest, raises

from jasmin_cis.data_io.hyperpoint import HyperPoint
from jasmin_cis.data_io.hyperpoint_view import UngriddedHyperPointView, GriddedHyperPointView
import jasmin_cis.test.test_util.mock as mock
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
    def test_can_access_point_in_ungridded_hyper_point_view_(self):
        ug = mock.make_regular_2d_ungridded_data_with_missing_values()
        hpv = ug.get_all_points()
        p = hpv[10]
        assert(p.val[0] == 11.0)
        assert(p.longitude == 0.0)
        assert(p.latitude == 5.0)

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
    def test3(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        all_coords = [((c[0].points, c[1]) if c is not None else None) for c in gd.find_standard_coords()]
        hpv = GriddedHyperPointView(all_coords, gd.data)
        print 0, hpv[0]
        print (3, 2), hpv[3, 2]
        x = hpv[3, 2]
        assert(hpv[3, 2].val[0] == 12)

    @istest
    def test4(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        hpv = gd.get_all_points()
        print 0, hpv[0]
        print 11, hpv[11]
        print (3, 2), hpv[3, 2]
        x = hpv[3, 2]
        assert(hpv[3, 2].val[0] == 12)

    @istest
    def test5(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        for p in gd.get_non_masked_points():
            print p

    @istest
    def test6(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        for i, p in gd.get_non_masked_points().enumerate_non_masked_points():
            print i, p

    @istest
    def test7(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        it = gd.get_non_masked_points().__iter__()
        print it.next()
        for p in it:
            print p

    @istest
    def test8(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        print gd.data[4, 2]
        hpv = gd.get_non_masked_points()
        p = hpv[4, 2]
        p_new = p.modified(val=999)
        hpv[4, 2] = p_new
        print gd.data[4, 2]

    @nottest
    def test9(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        print gd.data[4, 2]
        hpv = gd.get_non_masked_points()
        p = hpv[4, 2]
        p_new = p.modified(lon=999)
        hpv[4, 2] = p_new
        print gd.data[4, 2]

    @istest
    def test10(self):
        gd = gridded_data.make_from_cube(mock.make_5x3_lon_lat_2d_cube_with_missing_data())
        print gd.data[4, 2]
        hpv = gd.get_non_masked_points()
        hpv[4, 2] = 999
        print gd.data[4, 2]


# if __name__ == '__main__':
#     import nose
#     nose.runmodule()
