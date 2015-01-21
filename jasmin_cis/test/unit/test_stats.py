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

    def test_GIVEN_num_points_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))


class TestDatasetMeans(unittest.TestCase):

    def setUp(self):
        means = DatasetMeans(100, 125, 'dataset1', 'dataset2')
        self.output_string = means.pprint()
        self.output_cube = means.as_cube()

    def test_GIVEN_dataset_means_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Dataset means: 100, 125"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_dataset_means_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [100, 125]))

    def test_GIVEN_dataset_means_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("dataset_means"))
        assert_that(self.output_cube.long_name, is_("Mean value of each dataset"))

    def test_GIVEN_dataset_means_WHEN_as_cube_THEN_cube_coord_is_correct(self):
        coords = self.output_cube.aux_coords
        assert_that(len(coords), is_(1))
        assert_that(coords[0].long_name, is_('Input datasets'))
        assert_that(coords[0].var_name, is_('datasets'))
        assert_that(coords[0].points.tolist(), is_(['dataset1', 'dataset2']))


class TestDatasetStddevs(unittest.TestCase):

    def setUp(self):
        stddevs = DatasetStddevs(1.4123134512, 11.123, 'dataset1', 'dataset2')
        self.output_string = stddevs.pprint()
        self.output_cube = stddevs.as_cube()

    def test_GIVEN_dataset_stddevs_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Dataset standard deviations: 1.4123134512, 11.123"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_dataset_stddevs_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [1.4123134512, 11.123]))

    def test_GIVEN_dataset_stddevs_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("dataset_stddevs"))
        assert_that(self.output_cube.long_name, is_("Unbiased standard deviation of each dataset"))

    def test_GIVEN_dataset_stddevs_WHEN_as_cube_THEN_cube_coord_is_correct(self):
        coords = self.output_cube.aux_coords
        assert_that(len(coords), is_(1))
        assert_that(coords[0].long_name, is_('Input datasets'))
        assert_that(coords[0].var_name, is_('datasets'))
        assert_that(coords[0].points.tolist(), is_(['dataset1', 'dataset2']))
        
        
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

    def test_GIVEN_abs_mean_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))


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
                    is_("Unbiased standard deviation of the absolute difference (data2 - data1)"))

    def test_GIVEN_abs_stddev_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))

              
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

    def test_GIVEN_rel_mean_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))


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
                    is_("Unbiased standard deviation of the relative difference (data2 - data1)/data1"))

    def test_GIVEN_rel_stddev_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))
        

class TestPearsonCorrelation(unittest.TestCase):

    def setUp(self):
        pearson = PearsonCorrelation(0.97)
        self.output_string = pearson.pprint()
        self.output_cube = pearson.as_cube()

    def test_GIVEN_pearson_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Pearson coefficient: 0.97"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_pearson_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [0.97]))

    def test_GIVEN_pearson_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("pearson"))
        assert_that(self.output_cube.long_name, is_("Pearson product-moment correlation coefficient"))

    def test_GIVEN_pearson_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))
        
        
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
        assert_that(self.output_cube.var_name, is_("spearmans"))
        assert_that(self.output_cube.long_name, is_("Spearman's rank correlation coefficient"))

    def test_GIVEN_spearmans_WHEN_as_cube_THEN_cube_coord_is_empty(self):
        assert_that(self.output_cube.aux_coords, is_(()))
        
         
class TestLinearRegression(unittest.TestCase):

    def setUp(self):
        regression = LinearRegression(1.1, 0.5, 0.99, 0.1, 1.0)
        self.output_string = regression.pprint()
        self.output_cube = regression.as_cube()

    def test_GIVEN_regression_WHEN_pretty_print_THEN_pprint_is_correct(self):
        expected_output_string = "Linear regression results: data2 = 1.1 x data1 + 0.5;" \
                                 " r-value: 0.99; p-value: 0.1; stderr: 1.0"
        assert_that(self.output_string, is_(expected_output_string))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_data_is_correct(self):
        assert_that(array_equal(self.output_cube.data, [1.1, 0.5, 0.99, 0.1, 1.0]))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_metadata_is_correct(self):
        assert_that(self.output_cube.var_name, is_("regression"))
        assert_that(self.output_cube.long_name, is_("Linear regression results"))

    def test_GIVEN_regression_WHEN_as_cube_THEN_cube_coord_is_correct(self):
        coords = self.output_cube.aux_coords
        assert_that(len(coords), is_(1))
        assert_that(coords[0].long_name, is_('Linear regression results components'))
        assert_that(coords[0].var_name, is_('regression_components'))
        assert_that(coords[0].points.tolist(), ['gradient', 'intercept', 'r-value', 'p-value', 'stderr'])