import unittest

from jasmin_cis.subsetting.subset import Subset
from hamcrest import assert_that, is_


class TestLongitudeSubsetting(unittest.TestCase):

    data_min, data_max = None, None

    def fix_limits(self, limit_min, limit_max):
        return Subset._fix_longitude_limits(limit_min, limit_max, self.data_min, self.data_max)


class TestDataMinus180To180(TestLongitudeSubsetting):

    data_min, data_max = -180, 180

    def test_GIVEN_limits_minus_180_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 180)
        assert_that(limits, is_((-180, 180, False)))

    def test_GIVEN_limits_0_to_360_THEN_limits_match_data(self):
        limits = self.fix_limits(0, 360)
        assert_that(limits, is_((0, 0, True)))

    def test_GIVEN_limits_0_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 180)
        assert_that(limits, is_((0, 180, False)))

    def test_GIVEN_limits_minus_180_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 360)
        assert_that(limits, is_((-180, 360, False)))

    def test_GIVEN_wrapped_limits_THEN_limits_correct(self):
        limits = self.fix_limits(45, 200)  # i.e. Include 45->90->180->200
        assert_that(limits, is_((45, -160, True)))


class TestData0To360(TestLongitudeSubsetting):

    data_min, data_max = 0, 360

    def test_GIVEN_limits_minus_180_to_180_THEN_limits_match_data(self):
        limits = self.fix_limits(-180, 180)
        assert_that(limits, is_((180, 180, True)))

    def test_GIVEN_limits_0_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 360)
        assert_that(limits, is_((0, 360, False)))

    def test_GIVEN_limits_0_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 180)
        assert_that(limits, is_((0, 180, False)))

    def test_GIVEN_limits_minus_180_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 360)
        assert_that(limits, is_((-180, 360, False)))

    def test_GIVEN_wrapped_limits_THEN_limits_correct(self):
        limits = self.fix_limits(45, -160)  # i.e. Include 45->90->180/-180->-160
        assert_that(limits, is_((45, 200, False)))


class TestData0To180(TestLongitudeSubsetting):

    data_min, data_max = 0, 180

    def test_GIVEN_limits_minus_180_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 180)
        assert_that(limits, is_((-180, 180, False)))

    def test_GIVEN_limits_0_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 360)
        assert_that(limits, is_((0, 360, False)))

    def test_GIVEN_limits_0_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 180)
        assert_that(limits, is_((0, 180, False)))

    def test_GIVEN_limits_minus_180_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 360)
        assert_that(limits, is_((-180, 360, False)))

    def test_GIVEN_wrapped_limits_THEN_limits_correct(self):
        limits = self.fix_limits(90, 45)  # i.e. Include 90->180->270->360->45
        assert_that(limits, is_((90, 45, True)))


class TestDataMinus180To360(TestLongitudeSubsetting):

    data_min, data_max = -180, 360

    def test_GIVEN_limits_minus_180_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 180)
        assert_that(limits, is_((-180, 180, False)))

    def test_GIVEN_limits_0_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 360)
        assert_that(limits, is_((0, 360, False)))

    def test_GIVEN_limits_0_to_180_THEN_limits_unchanged(self):
        limits = self.fix_limits(0, 180)
        assert_that(limits, is_((0, 180, False)))

    def test_GIVEN_limits_minus_180_to_360_THEN_limits_unchanged(self):
        limits = self.fix_limits(-180, 360)
        assert_that(limits, is_((-180, 360, False)))

    def test_GIVEN_wrapped_limits_THEN_limits_correct(self):
        limits = self.fix_limits(90, 45)  # i.e. Include 90->180->270->360->45
        assert_that(limits, is_((90, 45, True)))

if __name__ == '__main__':
    unittest.main()
