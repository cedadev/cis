import logging

from cis.collocation.col_implementations import DummyConstraint, _fix_longitude_range
from cis.data_io.cube_utils import make_new_with_same_coordinates
from cis.data_io.datalist import DataList
from cis.utils import log_memory_profile, set_standard_name_if_valid
from cis.collocation.col import get_kernel


interpolator = None


def collocate(points, data, constraint=None, kernel='', fill_value=None,
              missing_data_for_missing_sample=False, extrapolate=False):
    """
    This collocator takes a list of HyperPoints and a data object (currently either Ungridded
    data or a Cube) and returns one new LazyData object with the values as determined by the
    constraint and kernel objects. The metadata for the output LazyData object is copied from
    the input data object.

    :param UngriddedData or UngriddedCoordinates points: Objects defining the sample points
    :param GriddedData or DataList data: Data to resample
    :param constraint: An instance of a Constraint subclass which takes a data object and
                       returns a subset of that data based on it's internal parameters
    :param kernel: An instance of a Kernel subclass which takes a number of points and returns
                   a single value
    :return: A single LazyData object
    """
    from cis.collocation.gridded_interpolation import GriddedUngriddedInterpolator
    log_memory_profile("GriddedUngriddedCollocator Initial")
    global interpolator

    # We can have any kernel, default to moments
    kernel = get_kernel(kernel)

    if isinstance(data, list):
        # Indexing and constraints (for SepConstraintKdTree) will only take place on the first iteration,
        # so we really can just call this method recursively if we've got a list of data.
        output = DataList()
        for var in data:
            output.extend(collocate(points, var, constraint, kernel))
        return output

    if constraint is not None and not isinstance(constraint, DummyConstraint):
        raise ValueError("A constraint cannot be specified for the GriddedUngriddedCollocator")
    data_points = data

    # First fix the sample points so that they all fall within the same 360 degree longitude range
    _fix_longitude_range(points.coords(), points)
    # Then fix the data points so that they fall onto the same 360 degree longitude range as the sample points
    _fix_longitude_range(points.coords(), data_points)

    log_memory_profile("GriddedUngriddedCollocator after data retrieval")

    logging.info("--> Collocating...")
    logging.info("    {} sample points".format(points.shape[0]))

    if interpolator is None:
        # Cache the interpolator
        interpolator = GriddedUngriddedInterpolator(data, points, kernel, missing_data_for_missing_sample)

    values = interpolator(data, fill_value=fill_value, extrapolate=extrapolate)

    log_memory_profile("GriddedUngriddedCollocator after running kernel on sample points")

    new = make_new_with_same_coordinates(points, values, var_name=data.var_name or 'var',
                                         long_name=data.long_name,
                                         units=data.units)
    set_standard_name_if_valid(new, data.standard_name)
    return_data = DataList([new])

    log_memory_profile("GriddedUngriddedCollocator final")

    return return_data
