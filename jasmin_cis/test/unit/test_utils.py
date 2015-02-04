import numpy
import unittest
from nose.tools import eq_, raises

from jasmin_cis.utils import *
from jasmin_cis.test.utils_for_testing import compare_masked_arrays


class TestUtils(unittest.TestCase):
    def test_can_apply_intersection_mask_to_two_masked_arrays(self):
        import numpy.ma as ma
        import numpy as np

        array1 = ma.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], mask=[1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
        array2 = ma.array([2, 4, 5, 6, 7, 8, 4, 3, 6, 80], mask=[0, 1, 0, 0, 0, 0, 0, 1, 0, 0])
        array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
        assert (np.equal(array1.mask, [1, 1, 1, 0, 0, 0, 0, 1, 0, 0]).all())
        assert (np.equal(array2.mask, [1, 1, 1, 0, 0, 0, 0, 1, 0, 0]).all())

    def test_can_apply_intersection_mask_to_three_masked_arrays(self):
        import numpy.ma as ma

        array1 = ma.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], mask=[1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
        array2 = ma.array([2, 4, 5, 6, 7, 8, 4, 3, 6, 80], mask=[0, 1, 0, 0, 0, 0, 0, 1, 0, 0])
        array3 = ma.array([2, 4, 5, 6, 7, 8, 4, 3, 6, 80], mask=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
        array1, array3 = apply_intersection_mask_to_two_arrays(array1, array3)
        array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)

        assert (ma.equal(array1.mask, [1, 1, 1, 0, 0, 0, 0, 1, 0, 1]).all())
        assert (ma.equal(array2.mask, [1, 1, 1, 0, 0, 0, 0, 1, 0, 1]).all())
        assert (ma.equal(array3.mask, [1, 1, 1, 0, 0, 0, 0, 1, 0, 1]).all())

    def test_can_apply_intersection_mask_to_one_masked_and_one_unmasked_array(self):
        import numpy.ma as ma
        import numpy as np

        array1 = ma.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], mask=[1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
        array2 = np.array([2, 4, 5, 6, 7, 8, 4, 3, 6, 80])
        array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
        assert (np.equal(array1.mask, [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]).all())
        assert (np.equal(array2.mask, [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]).all())

    def test_can_apply_intersection_mask_to_two_unmasked_arrays(self):
        import numpy as np

        array1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        array2 = np.array([2, 4, 5, 6, 7, 8, 4, 3, 6, 80])
        array1, array2 = apply_intersection_mask_to_two_arrays(array1, array2)
        assert (all(array1.mask) is False)
        assert (all(array2.mask) is False)

    def test_can_expand_1d_array_across(self):
        import numpy as np
        from jasmin_cis.utils import expand_1d_to_2d_array

        a = np.array([1, 2, 3, 4])
        b = expand_1d_to_2d_array(a, 4, axis=0)
        ref = np.array([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]])
        assert (np.equal(b, ref).all())

    def test_can_expand_1d_array_down(self):
        import numpy as np
        from jasmin_cis.utils import expand_1d_to_2d_array

        a = np.array([1, 2, 3, 4])
        b = expand_1d_to_2d_array(a, 4, axis=1)
        ref = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]])
        assert (np.equal(b, ref).all())

    def ten_bins_are_created_by_default(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {}
        step = None

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 11)  # 11 edges = 10 bins
        eq_(bin_edges.min(), data.min())
        assert (abs(bin_edges.max() - data.max()) < 1.e-7)

    def bin_width_can_be_specified_where_bin_width_perfectly_divides_range(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {}
        step = 0.5

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 7)
        eq_(bin_edges.min(), data.min())
        eq_(bin_edges.max(), data.max())

    def bin_width_can_be_specified_where_bin_width_does_not_perfectly_divides_range(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {}
        step = 0.7

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 5)
        eq_(bin_edges.min(), data.min())
        assert (bin_edges.max() < data.max())

    def ten_bins_are_created_when_min_is_specified(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {"xmin": 0.3}
        step = None

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 11)  # 11 edges = 10 bins
        eq_(bin_edges.min(), 0.3)
        assert (abs(bin_edges.max() - data.max()) < 1.e-7)  # 1.e-7 is approx 0

    def ten_bins_are_created_when_max_is_specified(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {"xmax": 2.3}
        step = None

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 11)  # 11 edges = 10 bins
        eq_(bin_edges.min(), data.min())
        assert (abs(bin_edges.max() - 2.3) < 1.e-7)  # 1.e-7 is approx 0'''

    def ten_bins_are_created_when_min_and_max_is_specified(self):
        from numpy import array

        data = array([0.0, 1.0, 2.0, 3.0])
        val_range = {"xmin": 0.3, "xmax": 2.3}
        step = None

        bin_edges = calculate_histogram_bin_edges(data, "x", val_range, step)
        eq_(len(bin_edges), 11)  # 11 edges = 10 bins
        assert (abs(bin_edges.min() - 0.3) < 1.e-7)  # 1.e-7 is approx 0
        assert (abs(bin_edges.max() - 2.3) < 1.e-7)  # 1.e-7 is approx 0

    def test_split_into_float_and_units(self):
        eq_(split_into_float_and_units('10km')['value'], 10)
        eq_(split_into_float_and_units('10km')['units'], 'km')

    def test_split_into_float_and_units_with_spaces(self):
        eq_(split_into_float_and_units('10 km')['value'], 10)
        eq_(split_into_float_and_units('10 km')['units'], 'km')

    def test_split_into_float_and_units_with_full_float(self):
        eq_(split_into_float_and_units('12.3e4uM')['value'], 12.3e4)
        eq_(split_into_float_and_units('12.3e4uM')['units'], 'uM')

    @raises(InvalidCommandLineOptionError)
    def test_split_into_float_and_units_with_extra_numbers(self):
        split_into_float_and_units('10km10')

    @raises(InvalidCommandLineOptionError)
    def test_split_into_float_and_units_with_no_numbers(self):
        split_into_float_and_units('km')

    def test_split_into_float_and_units_with_no_units(self):
        eq_(split_into_float_and_units('10')['value'], 10)
        eq_(split_into_float_and_units('10')['units'], None)

    @raises(InvalidCommandLineOptionError)
    def test_split_into_float_and_units_with_extra_units(self):
        eq_(split_into_float_and_units('km10m'), 10)

    def test_parse_distance_with_units_of_km_to_float_km(self):
        eq_(parse_distance_with_units_to_float_km('10km'), 10)

    def test_parse_distance_with_units_of_m_to_float_km(self):
        eq_(parse_distance_with_units_to_float_km('10000m'), 10)

    def test_parse_distance_without_units_to_float_km(self):
        eq_(parse_distance_with_units_to_float_km('10'), 10)

    @raises(InvalidCommandLineOptionError)
    def test_parse_distance_with_invalid_units(self):
        eq_(parse_distance_with_units_to_float_km('10Gb'), 10)

    def test_parse_distance_with_units_of_m_to_float_m(self):
        eq_(parse_distance_with_units_to_float_m('10m'), 10)

    def test_parse_distance_with_units_of_km_to_float_m(self):
        eq_(parse_distance_with_units_to_float_m('10km'), 10000)

    def test_parse_distance_without_units_to_float_m(self):
        eq_(parse_distance_with_units_to_float_m('10'), 10)

    def test_array_equal_including_nan(self):
        array1 = numpy.array([[1, 2], [3, 4]])
        array2 = numpy.array([[1, 2], [3, 4.1]])
        array3 = numpy.array([[1, 2], [3, float('nan')]])
        assert array_equal_including_nan(array1, array1)
        assert not array_equal_including_nan(array1, array2)
        assert not array_equal_including_nan(array1, array3)
        assert array_equal_including_nan(array3, array3)

    # Tests for apply_mask_to_numpy_array

    def test_apply_mask_to_numpy_array_with_unmasked_array(self):
        # Input array not a masked array to which is applied a mask containing 'True's
        in_array = numpy.array([1, 2, 3, 4])
        mask = numpy.array([False, False, True, False])
        out_array = apply_mask_to_numpy_array(in_array, mask)
        assert numpy.array_equal(out_array.mask, mask)

    def test_apply_mask_to_numpy_array_with_masked_array(self):
        # Input array has masked points to which is applied a mask containing 'True's
        in_array = numpy.ma.array([1, 2, 3, 4], mask=numpy.array([True, False, False, False]))
        mask = numpy.array([False, False, True, False])
        out_array = apply_mask_to_numpy_array(in_array, mask)
        assert numpy.array_equal(out_array.mask, numpy.array([True, False, True, False]))

    def test_apply_mask_to_numpy_array_with_masked_array_with_nomask(self):
        # Input array is a masked array but with mask 'nomask'. This is masked by a mask with no 'True's.
        # The output array should not have had a mask created.
        in_array = numpy.ma.array([1, 2, 3, 4], mask=numpy.ma.nomask)
        mask = numpy.array([False, False, False, False])
        out_array = apply_mask_to_numpy_array(in_array, mask)
        assert numpy.ma.getmask(out_array) is numpy.ma.nomask

    def test_apply_mask_to_numpy_array_with_masked_array_but_all_unmasked(self):
        # Input array is a masked array but no elements are masked. The mask contains no 'True's.
        # This is masked by a mask with no 'True's. The output array should not have had a mask created.
        in_array = numpy.ma.array([1, 2, 3, 4], mask=numpy.array([False, False, False, False]))
        mask = numpy.array([False, False, False, False])
        out_array = apply_mask_to_numpy_array(in_array, mask)
        assert numpy.array_equal(out_array.mask, mask)

    def test_apply_mask_to_numpy_array_with_masked_array_with_array_unmasked(self):
        # Input array is a masked array but with mask 'nomask'. This is masked by a mask with 'True's.
        # The output array should not have had a mask created.
        in_array = numpy.ma.array([1, 2, 3, 4], mask=numpy.ma.nomask)
        mask = numpy.array([False, True, False, True])
        out_array = apply_mask_to_numpy_array(in_array, mask)
        assert numpy.array_equal(out_array.mask, mask)

    def test_GIVEN_masked_array_WHEN_fix_longitude_THEN_longitudes_fixed_but_masked_values_untouched(self):
        lons = numpy.ma.masked_less([0, -639, 90, 180, -639, 270, 360, -639], -360)
        new_lons = fix_longitude_range(lons, -180)
        expected_new_lons = numpy.ma.masked_invalid([0, float('Nan'), 90, -180, float('Nan'), -90, 0, float('Nan')])
        compare_masked_arrays(new_lons, expected_new_lons)

    def test_GIVEN_unmasked_array_WHEN_fix_longitude_THEN_longitudes_fixed(self):
        lons = numpy.array([0, 90, 180, 270, 360])
        new_lons = fix_longitude_range(lons, -180)
        assert numpy.array_equal(new_lons, [0, 90, -180, -90, 0])

    def test_GIVEN_lons_write_only_WHEN_fix_longitude_THEN_longitudes_fixed(self):
        # Previously there was an issue where if the longitudes array being read in
        # was read only then this method failed.
        lons = numpy.array([0, 90, 180, 270, 360])
        lons.setflags(write=False)
        new_lons = fix_longitude_range(lons, -180)
        assert numpy.array_equal(new_lons, [0, 90, -180, -90, 0])
