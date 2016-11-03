import logging

import iris
import iris.analysis
import iris.analysis.interpolate
import iris.coords
from iris.exceptions import CoordinateMultiDimError
import numpy as np
from numpy import mean as np_mean, std as np_std, min as np_min, max as np_max, sum as np_sum

from cis.collocation.col_framework import (Collocator, Constraint, PointConstraint, CellConstraint,
                                           IndexedConstraint, Kernel, AbstractDataOnlyKernel)
import cis.exceptions
from cis.data_io.gridded_data import GriddedData, make_from_cube, GriddedDataList
from cis.data_io.hyperpoint import HyperPoint, HyperPointList
from cis.data_io.ungridded_data import Metadata, UngriddedDataList, UngriddedData
import cis.collocation.data_index as data_index
from cis.utils import log_memory_profile, set_standard_name_if_valid


class GeneralUngriddedCollocator(Collocator):
    """
    Collocator for locating onto ungridded sample points
    """

    def collocate(self, points, data, constraint, kernel):
        """
        This collocator takes a list of HyperPoints and a data object (currently either Ungridded
        data or a Cube) and returns one new LazyData object with the values as determined by the
        constraint and kernel objects. The metadata for the output LazyData object is copied from
        the input data object.

        :param UngriddedData or UngriddedCoordinates points: Object defining the sample points
        :param UngriddedData data: The source data to collocate from
        :param constraint: An instance of a Constraint subclass which takes a data object and
                           returns a subset of that data based on it's internal parameters
        :param kernel: An instance of a Kernel subclass which takes a number of points and returns
                       a single value
        :return UngriddedData or UngriddedDataList: Depending on the input
        """
        log_memory_profile("GeneralUngriddedCollocator Initial")

        if isinstance(data, list):
            # Indexing and constraints (for SepConstraintKdTree) will only take place on the first iteration,
            # so we really can just call this method recursively if we've got a list of data.
            output = UngriddedDataList()
            for var in data:
                output.extend(self.collocate(points, var, constraint, kernel))
            return output

        metadata = data.metadata

        sample_points = points.get_all_points()

        data_points = data.get_non_masked_points()

        # First fix the sample points so that they all fall within the same 360 degree longitude range
        _fix_longitude_range(points.coords(), sample_points)
        # Then fix the data points so that they fall onto the same 360 degree longitude range as the sample points
        _fix_longitude_range(points.coords(), data_points)

        log_memory_profile("GeneralUngriddedCollocator after data retrieval")

        # Create index if constraint and/or kernel require one.
        coord_map = None
        data_index.create_indexes(constraint, points, data_points, coord_map)
        data_index.create_indexes(kernel, points, data_points, coord_map)
        log_memory_profile("GeneralUngriddedCollocator after indexing")

        logging.info("--> Collocating...")

        # Create output arrays.
        self.var_name = data.name()
        self.var_long_name = metadata.long_name
        self.var_standard_name = metadata.standard_name
        self.var_units = data.units
        var_set_details = kernel.get_variable_details(self.var_name, self.var_long_name,
                                                      self.var_standard_name, self.var_units)

        sample_points_count = len(sample_points)
        # Create an empty masked array to store the collocated values. The elements will be unmasked by assignment.
        values = np.ma.masked_all((len(var_set_details), sample_points_count))
        values.fill_value = self.fill_value
        log_memory_profile("GeneralUngriddedCollocator after output array creation")

        logging.info("    {} sample points".format(sample_points_count))
        # Apply constraint and/or kernel to each sample point.
        cell_count = 0
        total_count = 0

        # Check if we want to sample missing points
        if self.missing_data_for_missing_sample:
            sample_enumerator = sample_points.enumerate_non_masked_points
        else:
            sample_enumerator = sample_points.enumerate_all_points

        for i, point in sample_enumerator():
            # Log progress periodically.
            cell_count += 1
            if cell_count == 1000:
                total_count += cell_count
                cell_count = 0
                logging.info("    Processed {} points of {}".format(total_count, sample_points_count))

            if constraint is None:
                con_points = data_points
            else:
                con_points = constraint.constrain_points(point, data_points)
            try:
                value_obj = kernel.get_value(point, con_points)
                # Kernel returns either a single value or a tuple of values to insert into each output variable.
                if isinstance(value_obj, tuple):
                    for idx, val in enumerate(value_obj):
                        if not np.isnan(val):
                            values[idx, i] = val
                else:
                    values[0, i] = value_obj
            except CoordinateMultiDimError as e:
                raise NotImplementedError(e)
            except ValueError as e:
                pass
        log_memory_profile("GeneralUngriddedCollocator after running kernel on sample points")

        return_data = UngriddedDataList()
        for idx, var_details in enumerate(var_set_details):
            var_metadata = Metadata(name=var_details[0], long_name=var_details[1], shape=(len(sample_points),),
                                    missing_value=self.fill_value, units=var_details[3])
            set_standard_name_if_valid(var_metadata, var_details[2])
            return_data.append(UngriddedData(values[idx, :], var_metadata, points.coords()))
        log_memory_profile("GeneralUngriddedCollocator final")

        return return_data


class GriddedUngriddedCollocator(Collocator):
    """
    Collocator for locating GriddedData onto ungridded sample points
    """

    def __init__(self, fill_value=None, var_name='', var_long_name='', var_units='',
                 missing_data_for_missing_sample=False, extrapolate=False):
        super(GriddedUngriddedCollocator, self).__init__(fill_value, var_name, var_long_name, var_units,
                                                         missing_data_for_missing_sample)
        self.extrapolate = extrapolate
        self.interpolator = None

    def collocate(self, points, data, constraint, kernel):
        """
        This collocator takes a list of HyperPoints and a data object (currently either Ungridded
        data or a Cube) and returns one new LazyData object with the values as determined by the
        constraint and kernel objects. The metadata for the output LazyData object is copied from
        the input data object.

        :param UngriddedData or UngriddedCoordinates points: Objects defining the sample points
        :param GriddedData or GriddedDataList data: Data to resample
        :param constraint: An instance of a Constraint subclass which takes a data object and
                           returns a subset of that data based on it's internal parameters
        :param kernel: An instance of a Kernel subclass which takes a number of points and returns
                       a single value
        :return: A single LazyData object
        """
        from cis.collocation.gridded_interpolation import GriddedUngriddedInterpolator
        log_memory_profile("GriddedUngriddedCollocator Initial")

        if isinstance(data, list):
            # Indexing and constraints (for SepConstraintKdTree) will only take place on the first iteration,
            # so we really can just call this method recursively if we've got a list of data.
            output = UngriddedDataList()
            for var in data:
                output.extend(self.collocate(points, var, constraint, kernel))
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
        logging.info("    {} sample points".format(points.size))

        if self.interpolator is None:
            # Cache the interpolator
            self.interpolator = GriddedUngriddedInterpolator(data, points, kernel, self.missing_data_for_missing_sample)

        values = self.interpolator(data, fill_value=self.fill_value, extrapolate=self.extrapolate)

        log_memory_profile("GriddedUngriddedCollocator after running kernel on sample points")

        metadata = Metadata(self.var_name or data.name(), long_name=self.var_long_name or data.metadata.long_name,
                            shape=values.shape, missing_value=self.fill_value, units=self.var_units or data.units)
        set_standard_name_if_valid(metadata, data.standard_name)
        return_data = UngriddedDataList([UngriddedData(values, metadata, points.coords())])

        log_memory_profile("GriddedUngriddedCollocator final")

        return return_data


class DummyCollocator(Collocator):
    def collocate(self, points, data, constraint, kernel):
        """
            This collocator does no collocation at all - it just returns the original data values. This might be useful
            if the input data for one variable is already known to be on the same grid as points. This routine could
            check the coordinates are the same but currently does no such check.

        :param points: A list of HyperPoints
        :param data: An UngriddedData object or Cube
        :param constraint: Unused
        :param kernel: Unused
        :return: A single LazyData object
        """
        from cis.data_io.ungridded_data import LazyData

        logging.info("--> Collocating...")
        data = cis.utils.listify(data)
        return [LazyData(var.data, var.metadata) for var in data]


class DummyConstraint(Constraint):
    def constrain_points(self, point, data):
        # This is a null constraint - all of the points just get passed back
        return data


class SepConstraint(PointConstraint):
    def __init__(self, h_sep=None, a_sep=None, p_sep=None, t_sep=None):
        from cis.exceptions import InvalidCommandLineOptionError

        super(SepConstraint, self).__init__()

        self.checks = []

        if h_sep is not None:
            self.h_sep = cis.utils.parse_distance_with_units_to_float_km(h_sep)
            self.checks.append(self.horizontal_constraint)
        if a_sep is not None:
            self.a_sep = cis.utils.parse_distance_with_units_to_float_m(a_sep)
            self.checks.append(self.alt_constraint)
        if p_sep is not None:
            try:
                self.p_sep = float(p_sep)
            except:
                raise InvalidCommandLineOptionError('Separation Constraint p_sep must be a valid float')
            self.checks.append(self.pressure_constraint)
        if t_sep is not None:
            from cis.parse_datetime import parse_datetimestr_delta_to_float_days
            try:
                self.t_sep = parse_datetimestr_delta_to_float_days(t_sep)
            except ValueError as e:
                raise InvalidCommandLineOptionError(e)
            self.checks.append(self.time_constraint)

    def time_constraint(self, point, ref_point):
        return point.time_sep(ref_point) < self.t_sep

    def alt_constraint(self, point, ref_point):
        return point.alt_sep(ref_point) < self.a_sep

    def pressure_constraint(self, point, ref_point):
        return point.pres_sep(ref_point) < self.p_sep

    def horizontal_constraint(self, point, ref_point):
        return point.haversine_dist(ref_point) < self.h_sep

    def constrain_points(self, ref_point, data):
        con_points = HyperPointList()
        for point in data:
            if all(check(point, ref_point) for check in self.checks):
                con_points.append(point)
        return con_points


class SepConstraintKdtree(PointConstraint):
    """A separation constraint that uses a k-D tree to optimise spatial constraining.
    If no horizontal separation parameter is supplied, this reduces to an exhaustive
    search using the other parameter(s).
    """

    def __init__(self, h_sep=None, a_sep=None, p_sep=None, t_sep=None):
        from cis.exceptions import InvalidCommandLineOptionError

        self.haversine_distance_kd_tree_index = False

        super(SepConstraintKdtree, self).__init__()

        self._index_cache = {}
        self.checks = []
        if h_sep is not None:
            self.h_sep = cis.utils.parse_distance_with_units_to_float_km(h_sep)
            self.haversine_distance_kd_tree_index = None
        else:
            self.h_sep = None

        if a_sep is not None:
            self.a_sep = cis.utils.parse_distance_with_units_to_float_m(a_sep)
            self.checks.append(self.alt_constraint)
        if p_sep is not None:
            try:
                self.p_sep = float(p_sep)
            except:
                raise InvalidCommandLineOptionError('Separation Constraint p_sep must be a valid float')
            self.checks.append(self.pressure_constraint)
        if t_sep is not None:
            from cis.parse_datetime import parse_datetimestr_delta_to_float_days
            try:
                self.t_sep = parse_datetimestr_delta_to_float_days(t_sep)
            except ValueError as e:
                raise InvalidCommandLineOptionError(e)
            self.checks.append(self.time_constraint)

    def time_constraint(self, point, ref_point):
        return point.time_sep(ref_point) < self.t_sep

    def alt_constraint(self, point, ref_point):
        return point.alt_sep(ref_point) < self.a_sep

    def pressure_constraint(self, point, ref_point):
        return point.pres_sep(ref_point) < self.p_sep

    def horizontal_constraint(self, point, ref_point):
        return point.haversine_dist(ref_point) < self.h_sep

    def constrain_points(self, ref_point, data):
        con_points = HyperPointList()
        if self.haversine_distance_kd_tree_index and self.h_sep:
            point_indices = self._get_cached_indices(ref_point)
            if point_indices is None:
                point_indices = self.haversine_distance_kd_tree_index.find_points_within_distance(ref_point, self.h_sep)
                self._add_cached_indices(ref_point, point_indices)
            for idx in point_indices:
                point = data[idx]
                if all(check(point, ref_point) for check in self.checks):
                    con_points.append(point)
        else:
            for point in data:
                if all(check(point, ref_point) for check in self.checks):
                    con_points.append(point)
        return con_points

    def _get_cached_indices(self, ref_point):
        key = ref_point[0:5]  # Don't use the value as a key (it's both irrelevant and un-hashable)
        try:
            return self._index_cache[key]
        except KeyError:
            return None

    def _add_cached_indices(self, ref_point, indices):
        key = ref_point[0:5]  # Don't use the value as a key (it's both irrelevant and un-hashable)
        self._index_cache[key] = indices


# noinspection PyPep8Naming
class mean(AbstractDataOnlyKernel):
    """
    Calculate mean of data points
    """

    def get_value_for_data_only(self, values):
        """
        return the mean
        """
        return np_mean(values)


# noinspection PyPep8Naming
class stddev(AbstractDataOnlyKernel):
    """
    Calculate the standard deviation
    """

    def get_value_for_data_only(self, values):
        """
        Return the standard deviation points
        """
        return np_std(values, ddof=1)


# noinspection PyPep8Naming,PyShadowingBuiltins
class min(AbstractDataOnlyKernel):
    """
    Calculate the minimum value
    """

    def get_value_for_data_only(self, values):
        """
        Return the minimum value
        """
        return np_min(values)


# noinspection PyPep8Naming,PyShadowingBuiltins
class max(AbstractDataOnlyKernel):
    """
    Calculate the maximum value
    """

    def get_value_for_data_only(self, values):
        """
        Return the maximum value
        """
        return np_max(values)


class sum(AbstractDataOnlyKernel):
    """
    Calculate the sum of the values
    """

    def get_value_for_data_only(self, values):
        """
        Return the sum of the values
        """
        return np_sum(values)


# noinspection PyPep8Naming
class moments(AbstractDataOnlyKernel):
    return_size = 3

    def __init__(self, mean_name='', stddev_name='', nopoints_name=''):
        self.mean_name = mean_name
        self.stddev_name = stddev_name
        self.nopoints_name = nopoints_name

    def get_variable_details(self, var_name, var_long_name, var_standard_name, var_units):
        """Sets name and units for mean, standard deviation and number of points variables, based
        on those of the base variable or overridden by those specified as kernel parameters.
        :param var_name: base variable name
        :param var_long_name: base variable long name
        :param var_standard_name: base variable standard name
        :param var_units: base variable units
        :return: tuple of tuples each containing (variable name, variable long name, variable units)
        """
        self.mean_name = var_name
        self.stddev_name = var_name + '_std_dev'
        stdev_long_name = 'Corrected sample standard deviation of %s' % var_long_name
        stddev_units = var_units
        self.nopoints_name = var_name + '_num_points'
        npoints_long_name = 'Number of points used to calculate the mean of %s' % var_long_name
        npoints_units = ''
        return ((self.mean_name, var_long_name, var_standard_name, var_units),
                (self.stddev_name, stdev_long_name, None, stddev_units),
                (self.nopoints_name, npoints_long_name, None, npoints_units))

    def get_value_for_data_only(self, values):
        """
        Returns the mean, standard deviation and number of values
        """

        return np_mean(values), np_std(values, ddof=1), np.size(values)


class nn_horizontal(Kernel):
    def get_value(self, point, data):
        """
            Collocation using nearest neighbours along the face of the earth where both points and
              data are a list of HyperPoints. The default point is the first point.
        """
        iterator = data.__iter__()
        try:
            nearest_point = next(iterator)
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.compdist(nearest_point, data_point):
                nearest_point = data_point
        return nearest_point.val[0]


class nn_horizontal_kdtree(Kernel):
    def __init__(self):
        self.haversine_distance_kd_tree_index = None

    def get_value(self, point, data):
        """
        Collocation using nearest neighbours along the face of the earth using a k-D tree index.
        """
        nearest_index = self.haversine_distance_kd_tree_index.find_nearest_point(point)
        if nearest_index is None:
            raise ValueError
        if nearest_index > len(data):
            pass
        nearest_point = data[nearest_index]
        return nearest_point.val[0]


class nn_altitude(Kernel):
    def get_value(self, point, data):
        """
            Collocation using nearest neighbours in altitude, where both points and
              data are a list of HyperPoints. The default point is the first point.
        """
        iterator = data.__iter__()
        try:
            nearest_point = next(iterator)
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.compalt(nearest_point, data_point):
                nearest_point = data_point
        return nearest_point.val[0]


class nn_pressure(Kernel):
    def get_value(self, point, data):
        """
            Collocation using nearest neighbours in pressure, where both points and
              data are a list of HyperPoints. The default point is the first point.
        """
        iterator = data.__iter__()
        try:
            nearest_point = next(iterator)
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.comppres(nearest_point, data_point):
                nearest_point = data_point
        return nearest_point.val[0]


class nn_time(Kernel):
    def get_value(self, point, data):
        """
            Collocation using nearest neighbours in time, where both points and
              data are a list of HyperPoints. The default point is the first point.
        """
        iterator = data.__iter__()
        try:
            nearest_point = next(iterator)
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.comptime(nearest_point, data_point):
                nearest_point = data_point
        return nearest_point.val[0]


# These classes act as abbreviations for kernel classes above:
class nn_h(nn_horizontal):
    """Nearest neighbour horizontal kernel - alias for nn_horizontal.
    """
    pass


class nn_a(nn_altitude):
    """Nearest neighbour altitude kernel - alias for nn_altitude.
    """
    pass


class nn_p(nn_pressure):
    """Nearest neighbour pressure kernel - alias for nn_pressure.
    """
    pass


class nn_t(nn_time):
    """Nearest neighbour time kernel - alias for nn_time.
    """
    pass


class GriddedCollocator(Collocator):

    def __init__(self, fill_value=None, var_name='', var_long_name='', var_units='',
                 missing_data_for_missing_sample=False, extrapolate=False):
        super(GriddedCollocator, self).__init__(fill_value, var_name, var_long_name, var_units,
                                                         missing_data_for_missing_sample)
        self.extrapolate = 'extrapolate' if extrapolate else 'mask'

    @staticmethod
    def _check_for_valid_kernel(kernel):
        from cis.exceptions import ClassNotFoundError

        if not (isinstance(kernel, gridded_gridded_nn) or isinstance(kernel, gridded_gridded_li)):
            raise ClassNotFoundError("Expected kernel of one of classes {}; found one of class {}".format(
                str([cis.utils.get_class_name(gridded_gridded_nn),
                     cis.utils.get_class_name(gridded_gridded_li)]),
                cis.utils.get_class_name(type(kernel))))

    def collocate(self, points, data, constraint, kernel):
        """
        This collocator takes two Iris cubes, and collocates from the data cube onto the grid of the 'points' cube. The
        collocator then returns another Iris cube.
        :param points: An Iris cube with the sampling grid to collocate onto.
        :param data: The Iris cube with the data to be collocated.
        :param constraint: None allowed yet, as this is unlikely to be required for gridded-gridded.
        :param kernel: The kernel to use, current options are gridded_gridded_nn and gridded_gridded_li.
        :return: An Iris cube with the collocated data.
        """
        self._check_for_valid_kernel(kernel)

        # Force the data longitude range to be the same as that of the sample grid.
        _fix_longitude_range(points.coords(), data)

        # Initialise variables used to create an output mask based on the sample data mask.
        sample_coord_lookup = {}  # Maps coordinate in sample data -> location in dimension order
        for idx, coord in enumerate(points.coords()):
            sample_coord_lookup[coord] = idx
        sample_coord_transpose_map = []  # For coords in both sample and data, contains the position in the sample
        other_coord_transpose_map = []  # For coords in data but not in sample, records that coord's position in data.
        repeat_size = 1
        output_mask = np.ma.nomask

        # Make a list of the coordinates we have, with each entry containing a list with the name of the coordinate and
        # the number of points along its axis. One is for the sample grid, which contains the points where we
        # interpolate too, and one is for the output grid, which will additionally contain any dimensions missing in the
        # sample grid.
        coord_names_and_sizes_for_sample_grid = []
        coord_names_and_sizes_for_output_grid = []
        for idx, coord in enumerate(data.coords(dim_coords=True)):
            # First try and find the coordinate in points, the sample grid. If an exception is thrown, it means that
            # name does not appear in the sample grid, and instead take the coordinate name and length from the original
            # data, as this is what we will be keeping.
            try:
                sample_coord = points.coords(coord.name())[0]
                coord_names_and_sizes_for_sample_grid.append([coord.name(), len(sample_coord.points)])
                # Find the index of the sample coordinate corresponding to the data coordinate.
                sample_coord_transpose_map.append(sample_coord_lookup[sample_coord])
            except IndexError:
                coord_names_and_sizes_for_output_grid.append([coord.name(), len(coord.points)])
                repeat_size *= len(coord.points)
                other_coord_transpose_map.append(idx)

        # Now we sort the sample coordinates so that they are in the same order as in the sample file,
        # rather than the order of the data file (that's the order we want the output dimensions).
        coord_names_and_sizes_for_sample_grid = [x[0] for x in sorted(zip(coord_names_and_sizes_for_sample_grid,
                                                                          sample_coord_transpose_map),
                                                                      key=lambda t: t[1])]

        # Adding the lists together in this way ensures that the coordinates not in the sample grid appear in the final
        # position, which is important for adding the points from the Iris interpolater to the new array. The data
        # returned from the Iris interpolater method will have dimensions of these missing coordinates, which needs
        # to be the final dimensions in the numpy array, as the iterator will give the position of the other dimensions.
        coord_names_and_sizes_for_output_grid = coord_names_and_sizes_for_sample_grid + \
                                                coord_names_and_sizes_for_output_grid

        # An array for the collocated data, with the correct shape
        output_shape = tuple(i[1] for i in coord_names_and_sizes_for_output_grid)
        new_data = np.zeros(output_shape)

        if self.missing_data_for_missing_sample:
            output_mask = self._make_output_mask(coord_names_and_sizes_for_sample_grid, output_shape,
                                                 points, repeat_size)

        # Now recreate the points cube, while ignoring any DimCoords in points that are not in the data cube
        new_dim_coord_list = []
        new_points_array_shape = []
        for i in range(0, len(coord_names_and_sizes_for_output_grid)):
            # Try and find the coordinate in the sample grid
            coord_found = points.coords(coord_names_and_sizes_for_output_grid[i][0])

            # If the coordinate exists in the sample grid then append the new coordinate to the list. Iris requires
            # this be given as a DimCoord object, along with a axis number, in a tuple pair.
            if len(coord_found) != 0:
                new_dim_coord_list.append((coord_found[0], len(new_dim_coord_list)))
                new_points_array_shape.append(coord_found[0].points.size)

        new_points_array = np.zeros(tuple(new_points_array_shape))

        # Use the new_data array to recreate points, without the DimCoords not in the data cube
        points = iris.cube.Cube(new_points_array, dim_coords_and_dims=new_dim_coord_list)

        output_cube = self._iris_interpolate(coord_names_and_sizes_for_output_grid,
                                             coord_names_and_sizes_for_sample_grid, data,
                                             kernel, output_mask, points, self.extrapolate)

        if not isinstance(output_cube, list):
            return GriddedDataList([output_cube])
        else:
            return output_cube

    @staticmethod
    def _make_output_mask(coord_names_and_sizes_for_sample_grid, output_shape, points, repeat_size):
        """ Creates a mask to apply to the output data based on the sample data mask. If there are coordinates in
        the data grid that are not in the sample grid, the same mask value is repeated for all values of the
        extra coordinates. If there are coordinates in the sample grid that are not in the data grid, a mask
        is not created since there is many to one correspondence between sample and output grid points.
        """
        output_mask = None

        # Construct the missing value mask from the sample data, if applicable.
        if len(coord_names_and_sizes_for_sample_grid) < len(points.dim_coords):
            # One or more axes collapsed so many sample points correspond to each output point.
            pass
        else:
            input_mask = np.ma.getmask(points.data)
            if input_mask is np.ma.nomask:
                # No sample data missing-value mask.
                pass
            else:
                # Fill in the remaining coordinates (those from the data which are not in the sample) by repeating
                # the constructed mask for each value of those coordinates
                output_mask = np.reshape(np.repeat(points.data.mask, repeat_size), output_shape)
        return output_mask

    @staticmethod
    def _iris_interpolate(coord_names_and_sizes_for_output_grid, coord_names_and_sizes_for_sample_grid, data, kernel,
                          output_mask, points, extrapolate):
        """ Collocates using iris.analysis.interpolate
        """
        coordinate_point_pairs = []
        for j in range(0, len(coord_names_and_sizes_for_sample_grid)):
            # For each coordinate make the list of tuple pair Iris requires, for example
            # [('latitude', -90), ('longitude, 0')]
            coordinate_point_pairs.append((coord_names_and_sizes_for_sample_grid[j][0],
                                           points.dim_coords[j].points))

        # The result here will be a cube with the correct dimensions for the output, so interpolated over all points
        # in coord_names_and_sizes_for_output_grid.
        output_cube = make_from_cube(data.interpolate(coordinate_point_pairs,
                                                      kernel.interpolater(extrapolation_mode=extrapolate)))

        # Iris outputs interpolated cubes with the dimensions in the order of the data grid, not the sample grid,
        # so we need to rearrange the order of the dimensions.
        output_coord_lookup = {}
        for idx, coord in enumerate(output_cube.dim_coords):
            output_coord_lookup[coord.name()] = idx
        transpose_map = [output_coord_lookup[coord[0]] for coord in coord_names_and_sizes_for_output_grid]
        output_cube.transpose(transpose_map)

        if isinstance(output_cube, list):
            for idx, data in enumerate(output_cube):
                output_cube[idx].data = cis.utils.apply_mask_to_numpy_array(data.data, output_mask)
        else:
            output_cube.data = cis.utils.apply_mask_to_numpy_array(output_cube.data, output_mask)
        return output_cube


class gridded_gridded_nn(Kernel):
    def __init__(self):
        self.name = 'nearest'
        self.interpolater = iris.analysis.Nearest

    def get_value(self, point, data):
        """Not needed for gridded/gridded collocation.
        """
        raise ValueError("gridded_gridded_nn kernel selected for use with collocator other than GriddedCollocator")


class gridded_gridded_li(Kernel):
    def __init__(self):
        self.name = 'bilinear'
        self.interpolater = iris.analysis.Linear

    def get_value(self, point, data):
        """Not needed for gridded/gridded collocation.
        """
        raise ValueError("gridded_gridded_li kernel selected for use with collocator other than GriddedCollocator")


class GeneralGriddedCollocator(Collocator):
    """Performs collocation of data on to the points of a cube (ie onto a gridded dataset).
    """

    def collocate(self, points, data, constraint, kernel):
        """
        :param points: cube defining the sample points
        :param data: CommonData object providing data to be collocated (or list of Data)
        :param constraint: instance of a Constraint subclass, which takes a data object and returns a subset of that
                           data based on it's internal parameters
        :param kernel: instance of a Kernel subclass which takes a number of points and returns a single value
        :return: GriddedDataList of collocated data
        """
        if isinstance(data, list):
            # If data is a list then call this method recursively over each element
            output_list = []
            for variable in data:
                collocated = self.collocate(points, variable, constraint, kernel)
                output_list.extend(collocated)
            return GriddedDataList(output_list)

        data_points = data.get_non_masked_points()

        # Work out how to iterate over the cube and map HyperPoint coordinates to cube coordinates.
        coord_map = make_coord_map(points, data)
        if self.missing_data_for_missing_sample and len(coord_map) is not len(points.coords()):
            raise cis.exceptions.UserPrintableException(
                "A sample variable has been specified but not all coordinates in the data appear in the sample so "
                "there are multiple points in the sample data so whether the data is missing or not can not be "
                "determined")

        coords = points.coords()
        shape = []
        output_coords = []

        # Find shape of coordinates to be iterated over.
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            if coord.ndim > 1:
                raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                          " than one is not supported (coordinate %s)", coord.name())
            # Ensure that bounds exist.
            if not coord.has_bounds():
                logging.warning("Creating guessed bounds as none exist in file")
                coord.guess_bounds()
            shape.append(coord.shape[0])
            output_coords.append(coord)

        _fix_longitude_range(coords, data_points)

        # Create index if constraint supports it.
        data_index.create_indexes(constraint, coords, data_points, coord_map)
        data_index.create_indexes(kernel, points, data_points, coord_map)

        # Initialise output array as initially all masked, and set the appropriate fill value.
        values = []
        for i in range(kernel.return_size):
            val = np.ma.zeros(shape)
            val.mask = True
            val.fill_value = self.fill_value
            values.append(val)

        if kernel.return_size == 1:
            set_value_kernel = self._set_single_value_kernel
        else:
            set_value_kernel = self._set_multi_value_kernel

        logging.info("--> Co-locating...")

        if hasattr(kernel, "get_value_for_data_only") and hasattr(constraint, "get_iterator_for_data_only"):
            # Iterate over constrained cells
            iterator = constraint.get_iterator_for_data_only(
                self.missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, values)
            for out_indices, data_values in iterator:
                try:
                    kernel_val = kernel.get_value_for_data_only(data_values)
                    set_value_kernel(kernel_val, values, out_indices)
                except ValueError:
                    # ValueErrors are raised by Kernel when there are no points to operate on.
                    # We don't need to do anything.
                    pass
        else:
            # Iterate over constrained cells
            iterator = constraint.get_iterator(
                self.missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, values)
            for out_indices, hp, con_points in iterator:
                try:
                    kernel_val = kernel.get_value(hp, con_points)
                    set_value_kernel(kernel_val, values, out_indices)
                except ValueError:
                    # ValueErrors are raised by Kernel when there are no points to operate on.
                    # We don't need to do anything.
                    pass

        # Construct an output cube containing the collocated data.
        kernel_var_details = kernel.get_variable_details(self.var_name or data.var_name,
                                                         self.var_long_name or data.long_name,
                                                         data.standard_name,
                                                         self.var_units or data.units)
        output = GriddedDataList([])
        for idx, val in enumerate(values):
            cube = self._create_collocated_cube(data, val, output_coords)
            data_with_nan_and_inf_removed = np.ma.masked_invalid(cube.data)
            data_with_nan_and_inf_removed.set_fill_value(self.fill_value)
            cube.data = data_with_nan_and_inf_removed
            cube.var_name = kernel_var_details[idx][0]
            cube.long_name = kernel_var_details[idx][1]
            set_standard_name_if_valid(cube, kernel_var_details[idx][2])
            try:
                cube.units = kernel_var_details[idx][3]
            except ValueError:
                logging.warn(
                    "Units are not cf compliant, not setting them. Units {}".format(kernel_var_details[idx][3]))

            # Sort the cube into the correct shape, so that the order of coordinates
            # is the same as in the source data
            coord_map = sorted(coord_map, key=lambda x: x[1])
            transpose_order = [coord[2] for coord in coord_map]
            cube.transpose(transpose_order)
            output.append(cube)

        return output

    def _set_multi_value_kernel(self, kernel_val, values, indices):
        # This kernel returns multiple values:
        for idx, val in enumerate(kernel_val):
            values[idx][indices] = val

    def _set_single_value_kernel(self, kernel_val, values, indices):
        values[0][indices] = kernel_val

    def _create_collocated_cube(self, src_data, data, coords):
        """Creates a cube using the metadata from the source cube and supplied data.

        :param src_data: ungridded data that was to be collocated
        :param data: collocated data values
        :param coords: coordinates for output cube
        :return: cube of collocated data
        """
        dim_coords_and_dims = []
        for idx, coord in enumerate(coords):
            dim_coords_and_dims.append((coord, idx))
        cube = GriddedData(data, standard_name=src_data.standard_name,
                           long_name=src_data.long_name,
                           var_name=src_data.var_name,
                           units=src_data.units,
                           dim_coords_and_dims=dim_coords_and_dims)
        return cube


class CubeCellConstraint(CellConstraint):
    """Constraint for constraining HyperPoints to be within an iris.coords.Cell.
    """

    def constrain_points(self, sample_point, data):
        """Returns HyperPoints lying within a cell.
        :param sample_point: HyperPoint of cells defining sample region
        :param data: list of HyperPoints to check
        :return: HyperPointList of points found within cell
        """
        con_points = HyperPointList()
        for point in data:
            include = True
            for idx in range(HyperPoint.number_standard_names):
                cell = sample_point[idx]
                if cell is not None:
                    if not (np.min(cell.bound) <= point[idx] < np.max(cell.bound)):
                        include = False
            if include:
                con_points.append(point)
        return con_points


class BinningCubeCellConstraint(IndexedConstraint):
    """Constraint for constraining HyperPoints to be within an iris.coords.Cell.

    Uses the index_data method to bin all the points
    """

    def __init__(self):
        super(BinningCubeCellConstraint, self).__init__()
        self.grid_cell_bin_index = None

    def constrain_points(self, sample_point, data):
        """Returns HyperPoints lying within a cell.

        This implementation returns the points that have been stored in the
        appropriate bin by the index_data method.
        :param sample_point: HyperPoint of indices of cells defining sample region
        :param data: list of HyperPoints to check
        :return: HyperPointList of points found within cell
        """
        point_list = self.grid_cell_bin_index.get_points_by_indices(sample_point)
        con_points = HyperPointList()
        if point_list is not None:
            for point in point_list:
                con_points.append(data[point])
        return con_points


class BinnedCubeCellOnlyConstraint(Constraint):
    """Constraint for constraining HyperPoints to be within an iris.coords.Cell. With an iterator which only
    travels over those cells with a value in.

    Uses the index_data method to bin all the points.
    """

    def __init__(self):
        super(BinnedCubeCellOnlyConstraint, self).__init__()
        self.grid_cell_bin_index_slices = None

    def constrain_points(self, sample_point, data):
        pass

    def get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data):

        for out_indices, slice_start_end in self.grid_cell_bin_index_slices.get_iterator():
            if not missing_data_for_missing_sample or points.data[out_indices] is not np.ma.masked:
                # iterate through the points which are within the same cell

                con_points = HyperPointList()
                slice_indicies = slice(*slice_start_end)

                for x in self.grid_cell_bin_index_slices.sort_order[slice_indicies]:
                    con_points.append(data_points[x])

                hp_values = [None] * HyperPoint.number_standard_names
                for (hpi, ci, shi) in coord_map:
                    hp_values[hpi] = coords[ci].points[out_indices[shi]]
                hp = HyperPoint(*hp_values)

                yield out_indices, hp, con_points

    def get_iterator_for_data_only(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points,
                                   values):
        """
        The method returns an iterator over the output indices and a numpy array slice of the data values. This may not
        be called by all collocators who may choose to iterate over all sample points instead.

        :param missing_data_for_missing_sample: If true anywhere there is missing data on the sample then final point is
         missing; otherwise just use the sample
        :param coord_map: Not needed for the data only kernel
        :param coords: Not needed for the data only kernel
        :param data_points: The (non-masked) data points
        :param shape: Not needed
        :param points: The original points object, these are the points to collocate
        :param values: Not needed
        :return: Iterator which iterates through (sample indices and data slice) to be placed in these points
        """
        data_points_sorted = data_points.data[self.grid_cell_bin_index_slices.sort_order]
        if missing_data_for_missing_sample:
            for out_indices, slice_start_end in self.grid_cell_bin_index_slices.get_iterator():
                if points.data[out_indices] is not np.ma.masked:
                    data_slice = data_points_sorted[slice(*slice_start_end)]
                    yield out_indices, data_slice
        else:
            for out_indices, slice_start_end in self.grid_cell_bin_index_slices.get_iterator():
                data_slice = data_points_sorted[slice(*slice_start_end)]
                yield out_indices, data_slice


def make_coord_map(points, data):
    """
    Create a map for how coordinates from the sample points map to the standard hyperpoint coordinates. Ignoring
    coordinates which are not present in the data
    :param points: sample points
    :param data: data to map
    :return: list of tuples, each tuple is index of coordinate to use
    tuple is (hyper point coord index, sample point coord index, output coord index)
    """
    # If there are coordinates in the sample grid that are not present for the data,
    # omit the from the set of coordinates in the output grid. Find a mask of coordinates
    # that are present to use when determining the output grid shape.
    coordinate_mask = [False if c is None else True for c in data.find_standard_coords()]

    # Find the mapping of standard coordinates to those in the sample points and those to be used
    # in the output data.
    return _find_standard_coords(points, coordinate_mask)


def _find_standard_coords(cube, coordinate_mask):
    """Finds the mapping of sample point coordinates to the standard ones used by HyperPoint.

    :param cube: cube among the coordinates of which to find the standard coordinates
    :param coordinate_mask: list of booleans indicating HyperPoint coordinates that are present
    :return: list of tuples relating index in HyperPoint to index in coords and in coords to be iterated over
    """
    coord_map = []
    cube_coord_lookup = {}

    cube_coords = cube.coords()
    for idx, coord in enumerate(cube_coords):
        cube_coord_lookup[coord] = idx

    shape_idx = 0
    for hpi, name in enumerate(HyperPoint.standard_names):
        if coordinate_mask[hpi]:
            # Get the dimension coordinates only - these correspond to dimensions of data array.
            cube_coords = cube.coords(standard_name=name, dim_coords=True)
            if len(cube_coords) > 1:
                msg = ('Expected to find exactly 1 coordinate, but found %d. They were: %s.'
                       % (len(cube_coords), ', '.join(coord.name() for coord in cube_coords)))
                raise cis.exceptions.CoordinateNotFoundError(msg)
            elif len(cube_coords) == 1:
                coord_map.append((hpi, cube_coord_lookup[cube_coords[0]], shape_idx))
                shape_idx += 1
    return coord_map


def _find_longitude_range(coords):
    """Finds the start of the longitude range, assumed to be either 0,360 or -180,180
    :param coords: coordinates to check
    :return: starting value for longitude range or None if no longitude coordinate found
    """
    low = None
    for coord in coords:
        if coord.standard_name == 'longitude':
            low = 0.0
            min_val = coord.points.min()
            if min_val < 0.0:
                low = -180.0
    return low


def _fix_longitude_range(coords, data_points):
    """Sets the longitude range of the data points to match that of the sample coordinates.
    :param coords: coordinates for grid on which to collocate
    :param data_points: HyperPointList or GriddedData of data to fix
    """
    range_start = _find_longitude_range(coords)
    if range_start is not None:
        data_points.set_longitude_range(range_start)
