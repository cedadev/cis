"""
Test the CommonData API: slicing, maths operations, equality, all main API functions, and no side effects...
"""
from unittest import TestCase
from nose.tools import assert_raises
from cis.test.util.mock import make_mock_cube, make_regular_2d_ungridded_data
from cis.data_io.gridded_data import make_from_cube
import numpy as np
from numpy.testing.utils import assert_array_almost_equal


class TestAPI(TestCase):
    def setUp(self):
        """
            Create the dummy objects necessary for testing
        """
        self.ug = make_regular_2d_ungridded_data()
        self.ug_1 = make_regular_2d_ungridded_data()
        self.gd = make_from_cube(make_mock_cube())
        self.gd_large = make_from_cube(make_mock_cube(50, 30))

    def test_can_slice_ungridded_data(self):
        res = self.ug[2:5]
        assert_array_almost_equal(res.data, self.ug.data[2:5])
        assert_array_almost_equal(res.lat.data, self.ug.lat.data[2:5])
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_can_slice_single_row_of_ungridded_data(self):
        scalar = self.ug[2]
        assert_array_almost_equal(scalar.data, self.ug.data[2])
        assert_array_almost_equal(scalar.lat.data, self.ug.lat.data[2])
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_can_slice_multidim_ungridded_data(self):
        res = self.ug[2:5, 2]
        assert_array_almost_equal(res.data, self.ug.data[2:5, 2])
        assert_array_almost_equal(res.lat.data, self.ug.lat.data[2:5, 2])
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    # Basic maths operations

    def test_can_add_ungridded_data_objects(self):
        res = self.ug + self.ug_1
        assert_array_almost_equal(res.data, self.ug.data + self.ug_1.data)

    def test_can_add_numpy_arrays_and_ungridded_data_objects(self):
        # Create a new object that is the same size so I can just use it's data array
        data = make_regular_2d_ungridded_data().data
        res = self.ug + data
        assert_array_almost_equal(res.data, self.ug.data + data)

    def test_can_add_scalar_and_ungridded_data_objects(self):
        res = self.ug + 5
        assert_array_almost_equal(res.data, self.ug.data + 5)

    def test_can_perform_in_place_maths(self):
        self.ug -= 5
        # Test against the other ungridded data object as this one has changed!
        assert_array_almost_equal(self.ug.data, self.ug_1.data - 5)

    def test_can_perform_unary_op_on_ungridded_data(self):
        from cis.maths import abs
        self.ug -= 5
        res = abs(self.ug)
        # Test against the other ungridded data object as this one has changed!
        assert_array_almost_equal(res.data, np.abs(self.ug_1.data - 5))

    def test_cannot_add_gridded_and_ungridded_data_objects_of_different_shape(self):
        # Force to have the same units
        self.gd_large.units = self.ug.units
        with assert_raises(ValueError):
            res = self.ug + self.gd_large

    def test_CAN_add_gridded_and_ungridded_data_objects_of_same_shape(self):
        # Force to have the same units
        self.gd.units = self.ug.units
        res = self.ug + self.gd
        assert_array_almost_equal(res.data, self.ug.data + self.gd.data)

    def test_can_do_basic_coord_math(self):
        res_c = self.ug.lat + 5
        assert_array_almost_equal(res_c.data, self.ug.lat.data + 5)

    # API tests (subset, aggregate, collocate, etc)

    def test_basic_gridded_to_ungridded_collocation(self):
        res = self.gd.collocated_onto(self.ug)
        res_1 = self.ug.sampled_from(self.gd)
        # The two results should be identical
        assert res == res_1
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_basic_gridded_to_ungridded_collocation_invalid_method(self):
        with assert_raises(ValueError):
            self.gd.collocated_onto(self.ug, how='blah')

    def test_basic_ungridded_to_ungridded_collocation(self):
        res = self.ug.collocated_onto(self.ug_1)
        res_1 = self.ug_1.sampled_from(self.ug)
        # The two results should be identical
        assert res == res_1
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_basic_gridded_to_gridded_collocation(self):
        gd_copy = self.gd.copy()
        res = self.gd.collocated_onto(self.gd)
        assert self.gd == gd_copy
        res_1 = self.gd.sampled_from(self.gd)
        # The two data results should be identical, although the metadata is slightly different for some reason
        assert_array_almost_equal(res[0].data, res_1[0].data)

    def test_basic_ungridded_to_gridded_collocation(self):
        gd_copy = self.gd.copy()
        res = self.ug.collocated_onto(self.gd)
        assert self.gd == gd_copy
        res_1 = self.gd.sampled_from(self.ug)
        # The two data results should be identical, although the metadata is slightly different for some reason
        assert_array_almost_equal(res[0].data, res_1[0].data)
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_basic_gridded_subsetting(self):
        gd_copy = self.gd.copy()
        res = self.gd.subset(x=[-5, 0])
        assert self.gd == gd_copy

    def test_basic_ungridded_subsetting(self):
        res = self.ug.subset(x=[-5, 0])
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_basic_gridded_collapse(self):
        gd_copy = self.gd.copy()
        res = self.gd.collapsed('x')
        assert self.gd == gd_copy

    def test_basic_gridded_collapse_using_coord_objects(self):
        gd_copy = self.gd.copy()
        res = self.gd.collapsed(self.gd.coords())
        assert self.gd == gd_copy

    def test_basic_ungridded_aggregation(self):
        res = self.ug.aggregate(x=[-5, 0, 1])
        # This dataset should still be the same as the alternative one (this checks data and metadata)
        assert self.ug == self.ug_1

    def test_copy_copies_metadata(self):
        res = self.ug.copy()
        res.var_name = 'test'
        assert self.ug.var_name != 'test'

    def test_change_units(self):
        from numpy.testing import assert_almost_equal
        assert self.ug.data[0, 0] == 1

        self.ug.units = 'cm-3'

        self.ug.convert_units('m-3')

        assert str(self.ug.units) == 'm-3'
        assert_almost_equal(self.ug.data[0, 0], [1e6])

    def test_change_units_throws_ValueError_for_invalid_units_or_conversion(self):
        # Invalid units on the ungridded data
        with assert_raises(ValueError):
            self.ug.units = 'cm-3 stp'
            self.ug.convert_units('m-3')

        # Invalid units to convert to
        with assert_raises(ValueError):
            self.ug.units = 'cm-3'
            self.ug.convert_units('foo')

        # Invalid conversion
        with assert_raises(ValueError):
            self.ug.units = 'cm-3'
            self.ug.convert_units('kg')
