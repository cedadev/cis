import unittest

import numpy as np
from hamcrest import assert_that, is_, close_to

from jasmin_cis.stats import StatsAnalyzer
from jasmin_cis.data_io.gridded_data import GriddedData


class TestStatsAnalyser(unittest.TestCase):

    def setUp(self):
        self.data1 = GriddedData(np.array([[1.0, -2.0, 3.0, 4.0, 5.0],
                                           [6.0,  7.0, 8.0, 9.0, 10.0]]))
        self.data2 = GriddedData(np.array([[0.8, -1.7, 3.6, 3.7, 5.1],
                                           [6.0,  7.3, 7.9, 9.1, 10.1]]))
        self.missing1 = GriddedData(np.ma.masked_equal([[1.0, -2.0, 3.0, 4.0, -999],
                                                        [6.0, -999, 8.0, -100, -999]], -999))
        self.missing2 = GriddedData(np.ma.masked_equal([[-999, -2.1, 4.1, 3.2, -999],
                                                        [6.0, 7.3,  8.1, -120, -999]], -999))

    def test_GIVEN_datasets_WHEN_analyze_THEN_StatisticsResults_returned(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        results = stats.analyze()
        assert_that(len(results), is_(14))

    # ======================== POINTS COUNT

    def test_GIVEN_no_missing_vals_WHEN_count_THEN_points_count_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.points_count()
        assert_that(res[0].num_points, is_(10))

    def test_GIVEN_missing_vals_WHEN_count_THEN_points_count_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.points_count()
        assert_that(res[0].num_points, is_(6))

    def test_GIVEN_one_masked_one_nparray_WHEN_points_count_THEN_count_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.points_count()
        assert_that(res[0].num_points, is_(7))

    # ======================== MEAN

    def test_GIVEN_no_missing_vals_WHEN_mean_THEN_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing1)
        res = stats.means()
        assert_that(res[0].mean, is_(5.1))

    def test_GIVEN_missing_vals_WHEN_count_THEN_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing1)
        res = stats.means()
        assert_that(res[1].mean, close_to(-11.4285714286, 1e-5))

    # ======================= STDDEV

    def test_GIVEN_no_missing_vals_WHEN_stddev_THEN_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing1)
        res = stats.stddevs()
        assert_that(res[0].stddev, close_to(3.7252889523, 1e-5))

    def test_GIVEN_missing_vals_WHEN_stddev_THEN_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing1)
        res = stats.stddevs()
        assert_that(res[1].stddev, close_to(39.1912283675, 1e-5))

    # ================= ABS MEAN

    def test_GIVEN_no_missing_vals_WHEN_abs_mean_THEN_abs_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.abs_mean()
        assert_that(res[0].abs_mean, close_to(0.09, 1e-5))

    def test_GIVEN_missing_vals_WHEN_abs_mean_THEN_abs_mean_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.abs_mean()
        assert_that(res[0].abs_mean, close_to(-3.2833333333, 1e-5))

    def test_GIVEN_one_masked_one_nparray_WHEN_abs_mean_THEN_abs_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.abs_mean()
        assert_that(res[0].abs_mean, close_to(-18.3428571429, 1e-5))

    # ================= ABS STDDEV

    def test_GIVEN_no_missing_vals_WHEN_abs_stddev_THEN_abs_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.abs_stddev()
        assert_that(res[0].abs_stddev, close_to(0.2643650675, 1e-5))

    def test_GIVEN_missing_vals_WHEN_abs_stddev_THEN_abs_stddev_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.abs_stddev()
        assert_that(res[0].abs_stddev, close_to(8.2120440005, 1e-5))

    def test_GIVEN_one_masked_one_nparray_WHEN_abs_stddev_THEN_abs_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.abs_stddev()
        assert_that(res[0].abs_stddev, close_to(48.7984582114, 1e-5))

    # ================= REL MEAN
    
    def test_GIVEN_no_missing_vals_WHEN_rel_mean_THEN_rel_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.rel_mean()
        assert_that(res[0].rel_mean, close_to(-0.0153531746, 1e-5))

    def test_GIVEN_missing_vals_WHEN_rel_mean_THEN_rel_mean_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.rel_mean()
        assert_that(res[0].rel_mean, close_to(0.0715277778, 1e-5))

    def test_GIVEN_one_masked_one_nparray_WHEN_rel_mean_THEN_rel_mean_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.rel_mean()
        assert_that(res[0].rel_mean, close_to(-2.0087585034, 1e-5))
    
    def test_GIVEN_divide_by_zeros_WHEN_rel_mean_THEN_rel_mean_correct(self):
        # Zeros in the first array cause undefined values in the relative calculations.
        data_with_zeros = self.data1
        data_with_zeros.data[0][1] = 0
        stats = StatsAnalyzer(data_with_zeros, self.missing2)
        res = stats.rel_mean()
        assert_that(res[0].rel_mean, close_to(-2.3518849206, 1e-5))

    # ================= REL STDDEV
    
    def test_GIVEN_no_missing_vals_WHEN_rel_stddev_THEN_rel_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.rel_stddev()
        assert_that(res[0].rel_stddev, close_to(0.1097392069, 1e-5))

    def test_GIVEN_missing_vals_WHEN_rel_stddev_THEN_rel_stddev_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.rel_stddev()
        assert_that(res[0].rel_stddev, close_to(0.1930820326, 1e-5))

    def test_GIVEN_one_masked_one_nparray_WHEN_rel_stddev_THEN_rel_stddev_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.rel_stddev()
        assert_that(res[0].rel_stddev, close_to(5.4371807462, 1e-5))

    def test_GIVEN_divide_by_zeros_WHEN_rel_stddev_THEN_rel_stddev_correct(self):
        # Zeros in the first array cause undefined values in the relative calculations.
        data_with_zeros = self.data1
        data_with_zeros.data[0][1] = 0
        stats = StatsAnalyzer(data_with_zeros, self.missing2)
        res = stats.rel_stddev()
        assert_that(res[0].rel_stddev, close_to(5.8725242578, 1e-5))

    # ================= SPEARMAN

    def test_GIVEN_no_missing_vals_WHEN_spearman_THEN_spearman_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.spearmans_rank()
        assert_that(res[0].spearman, close_to(1.0, 1e-5))

    def test_GIVEN_missing_vals_WHEN_spearman_THEN_spearman_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.spearmans_rank()
        assert_that(res[0].spearman, close_to(0.9428571429, 1e-5))

    def test_GIVEN_one_masked_one_nparray_WHEN_spearman_THEN_spearman_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.spearmans_rank()
        assert_that(res[0].spearman, close_to(0.2142857143, 1e-5))

    # ==================  LINREG

    def test_GIVEN_no_missing_vals_WHEN_lin_regression_THEN_regression_correct(self):
        stats = StatsAnalyzer(self.data1, self.data2)
        res = stats.linear_regression()
        expected_res = [0.9912730184, 0.1345076061, 0.997485722,  0.248895076302]
        actual_res = res[0].grad, res[1].intercept, res[2].r, res[3].stderr
        assert_that(np.allclose(actual_res, expected_res))

    def test_GIVEN_missing_vals_WHEN_lin_regression_THEN_regression_correct(self):
        stats = StatsAnalyzer(self.missing1, self.missing2)
        res = stats.linear_regression()
        expected_res = [1.1920369653, -0.6908343017, 0.999845219, 0.813981263802]
        actual_res = res[0].grad, res[1].intercept, res[2].r, res[3].stderr
        assert_that(np.allclose(actual_res, expected_res))

    def test_GIVEN_one_masked_one_nparray_WHEN_lin_regression_THEN_regression_correct(self):
        stats = StatsAnalyzer(self.data1, self.missing2)
        res = stats.linear_regression()
        expected_res = [-5.1404761905, 12.3595238095, -0.4079085869, 39.8577461979]
        actual_res = res[0].grad, res[1].intercept, res[2].r, res[3].stderr
        assert_that(np.allclose(actual_res, expected_res))

if __name__ == '__main__':
    unittest.main()
