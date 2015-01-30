import unittest
from hamcrest import assert_that, is_
from numpy import array_equal

from jasmin_cis.stats import *


class TestNumPoints(unittest.TestCase):

    def setUp(self):
        num_points = PointsCount(123)
        self.output_string = num_points.pprint()
        self.output_cube = num_points.as_cube()

    def test_GIVEN_num_points_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Number of points: 123"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_num_points_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(123))

    def test_GIVEN_num_points_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("num_points"))
        assert_that(self.output_cube.long_name, is_("Number of points used in calculations"))


class TestDatasetMean(unittest.TestCase):

    def setUp(self):
        mean = DatasetMean(100, 'dataset1.nc', 1)
        self.output_string = mean.pprint()
        self.output_cube = mean.as_cube()

    def test_GIVEN_dataset_mean_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Mean value of dataset 1: 100"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_dataset_mean_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(100))

    def test_GIVEN_dataset_mean_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("dataset_mean_1"))
        assert_that(self.output_cube.long_name, is_("Mean value of dataset1.nc"))


class TestDatasetStddev(unittest.TestCase):

    def setUp(self):
        stddev = DatasetStddev(1.4123134512, 'dataset1.nc', 1)
        self.output_string = stddev.pprint()
        self.output_cube = stddev.as_cube()

    def test_GIVEN_dataset_stddev_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Standard deviation for dataset 1: 1.4123134512"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_dataset_stddev_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(1.4123134512))

    def test_GIVEN_dataset_stddev_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("dataset_stddev_1"))
        assert_that(self.output_cube.long_name, is_("Corrected sample standard deviation of dataset1.nc"))


class TestAbsoluteMean(unittest.TestCase):

    def setUp(self):
        mean = AbsoluteMean(97.5)
        self.output_string = mean.pprint()
        self.output_cube = mean.as_cube()

    def test_GIVEN_abs_mean_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Mean of absolute difference: 97.5"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_abs_mean_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [97.5]))

    def test_GIVEN_abs_mean_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("abs_mean"))
        assert_that(self.output_cube.long_name, is_("Mean of the absolute difference (data2 - data1)"))


class TestAbsoluteStddev(unittest.TestCase):

    def setUp(self):
        stddev = AbsoluteStddev(14.4)
        self.output_string = stddev.pprint()
        self.output_cube = stddev.as_cube()

    def test_GIVEN_abs_stddev_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Standard deviation of absolute difference: 14.4"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_abs_stddev_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [14.4]))

    def test_GIVEN_abs_stddev_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("abs_stddev"))
        assert_that(self.output_cube.long_name,
                    is_("Corrected sample standard deviation of the absolute difference (data2 - data1)"))

              
class TestRelativeMean(unittest.TestCase):

    def setUp(self):
        mean = RelativeMean(0.88)
        self.output_string = mean.pprint()
        self.output_cube = mean.as_cube()

    def test_GIVEN_rel_mean_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Mean of relative difference: 0.88"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_rel_mean_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [0.88]))

    def test_GIVEN_rel_mean_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("rel_mean"))
        assert_that(self.output_cube.long_name, is_("Mean of the relative difference (data2 - data1)/data1"))


class TestRelativeStddev(unittest.TestCase):

    def setUp(self):
        stddev = RelativeStddev(0.17)
        self.output_string = stddev.pprint()
        self.output_cube = stddev.as_cube()

    def test_GIVEN_rel_stddev_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Standard deviation of relative difference: 0.17"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_rel_stddev_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [0.17]))

    def test_GIVEN_rel_stddev_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("rel_stddev"))
        assert_that(self.output_cube.long_name,
                    is_("Corrected sample standard deviation of the relative difference (data2 - data1)/data1"))


class TestSpearmansRank(unittest.TestCase):

    def setUp(self):
        spearmans = SpearmansRank(0.87)
        self.output_string = spearmans.pprint()
        self.output_cube = spearmans.as_cube()

    def test_GIVEN_spearmans_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Spearman's rank coefficient: 0.87"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_spearmans_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [0.87]))

    def test_GIVEN_spearmans_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("spearman"))
        assert_that(self.output_cube.long_name, is_("Spearman's rank correlation coefficient"))


class TestLinearRegressionGradient(unittest.TestCase):

    def setUp(self):
        regression = LinearRegressionGradient(1.1)
        self.output_string = regression.pprint()
        self.output_cube = regression.as_cube()

    def test_GIVEN_regression_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Linear regression gradient: 1.1"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(1.1))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("regression_gradient"))
        assert_that(self.output_cube.long_name, is_("Linear regression gradient"))


class TestLinearRegressionIntercept(unittest.TestCase):

    def setUp(self):
        regression = LinearRegressionIntercept(0.5)
        self.output_string = regression.pprint()
        self.output_cube = regression.as_cube()

    def test_GIVEN_regression_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Linear regression intercept: 0.5"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(0.5))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("regression_intercept"))
        assert_that(self.output_cube.long_name, is_("Linear regression intercept"))


class TestLinearRegressionRValue(unittest.TestCase):

    def setUp(self):
        regression = LinearRegressionRValue(0.99)
        self.output_string = regression.pprint()
        self.output_cube = regression.as_cube()

    def test_GIVEN_regression_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Linear regression r-value: 0.99"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(0.99))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("regression_r"))
        assert_that(self.output_cube.long_name, is_("Linear regression r-value "
                                                    "(Pearson product-moment correlation coefficient)"))


class TestLinearRegressionStderr(unittest.TestCase):

    def setUp(self):
        regression = LinearRegressionStderr(1.0)
        self.output_string = regression.pprint()
        self.output_cube = regression.as_cube()

    def test_GIVEN_regression_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Linear regression standard error: 1.0"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(self.output_cube.data, is_(1.0))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("regression_stderr"))
        assert_that(self.output_cube.long_name, is_("Linear regression standard error of the estimate"))