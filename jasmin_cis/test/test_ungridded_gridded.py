from nose.tools import istest
import numpy
from jasmin_cis.col_implementations import UngriddedGriddedColocator, mean, CubeCellConstraint
from jasmin_cis.test.test_util.mock import make_dummy_ungridded_data_single_point, make_square_5x3_2d_cube


@istest
def test_single_point_results_in_single_value_in_cell():
    sample_cube = make_square_5x3_2d_cube()
    data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2)

    col = UngriddedGriddedColocator()
    con = CubeCellConstraint(fill_value=-999.9)

    out_cube = col.colocate(points=sample_cube, data=data_point, constraint=con, kernel=mean())[0]

    expected_result = numpy.array([[-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, 1.2, -999.9],
                                   [-999.9, -999.9, -999.9],
                                   [-999.9, -999.9, -999.9]])

    assert (out_cube.data == expected_result).all()

