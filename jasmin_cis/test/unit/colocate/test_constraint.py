"""
Test the constraints
"""
import unittest
from nose.tools import eq_

from jasmin_cis.test.util import mock
from jasmin_cis.data_io.hyperpoint import HyperPoint


class TestSepConstraint(unittest.TestCase):

    def test_all_constraint_in_4d(self):
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, pres=50.0, t=dt.datetime(1984, 8, 29))

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        # in each direction
        h_sep = 1000
        # 15m altitude seperation
        a_sep = 15
        # 1 day (and a little bit) time seperation
        t_sep = 'P1DT1M'
        # Pressure constraint is 50/40 < p_sep < 60/50
        p_sep = 1.22

        constraint = SepConstraint(h_sep=h_sep, a_sep=a_sep, p_sep=p_sep, t_sep=t_sep)

        # This should leave us with 9 points: [[ 22, 23, 24]
        #                                      [ 27, 28, 29]
        #                                      [ 32, 33, 34]]
        ref_vals = np.array([27., 28., 29., 32., 33., 34.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    def test_alt_constraint_in_4d(self):
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, t=dt.datetime(1984, 8, 29))

        # 15m altitude seperation
        a_sep = 15

        constraint = SepConstraint(a_sep=a_sep)

        # This should leave us with 15 points:  [ 21.  22.  23.  24.  25.]
        # [ 26.  27.  28.  29.  30.]
        #                                       [ 31.  32.  33.  34.  35.]
        ref_vals = np.array([21., 22., 23., 24., 25., 26., 27., 28., 29., 30., 31., 32., 33., 34., 35.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    def test_horizontal_constraint_in_4d(self):
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, t=dt.datetime(1984, 8, 29))

        # One degree near 0, 0 is about 110km in latitude and longitude, so 300km should keep us to within 3 degrees
        # in each direction
        constraint = SepConstraint(h_sep=1000)

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50) + 1.0, (10, 5))[:, 1:4].flatten()

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    def test_time_constraint_in_4d(self):
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(lat=0.0, lon=0.0, alt=50.0, t=dt.datetime(1984, 8, 29))

        # 1 day (and a little bit) time seperation
        constraint = SepConstraint(t_sep='P1dT1M')

        # This should leave us with 30 points
        ref_vals = np.reshape(np.arange(50) + 1.0, (10, 5))[:, 1:4].flatten()

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())

    def test_pressure_constraint_in_4d(self):
        from jasmin_cis.col_implementations import SepConstraint
        import datetime as dt
        import numpy as np

        ug_data = mock.make_regular_4d_ungridded_data()
        ug_data_points = ug_data.get_non_masked_points()
        sample_point = HyperPoint(0.0, 0.0, 50.0, 24.0, dt.datetime(1984, 8, 29))

        constraint = SepConstraint(p_sep=2)

        # This should leave us with 20 points:  [  6.   7.   8.   9.  10.]
        # [ 11.  12.  13.  14.  15.]
        #                                       [ 16.  17.  18.  19.  20.]
        #                                       [ 21.  22.  23.  24.  25.]
        ref_vals = np.array([6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23.,
                             24., 25.])

        new_points = constraint.constrain_points(sample_point, ug_data_points)
        new_vals = new_points.vals

        eq_(ref_vals.size, new_vals.size)
        assert (np.equal(ref_vals, new_vals).all())


if __name__ == '__main__':
    unittest.main()
