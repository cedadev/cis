import logging
import math

import iris
import numpy as np

from jasmin_cis.col_framework import (Colocator, Constraint, PointConstraint, CellConstraint,
                                      IndexedConstraint, Kernel)
import jasmin_cis.exceptions
from jasmin_cis.data_io.hyperpoint import HyperPoint, HyperPointList
from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData, Metadata
import jasmin_cis.utils


class DefaultColocator(Colocator):

    def __init__(self, var_name='', var_long_name='', var_units=''):
        super(DefaultColocator, self).__init__()
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator takes a list of HyperPoints and a data object (currently either Ungridded data or a Cube) and returns
             one new LazyData object with the values as determined by the constraint and kernel objects. The metadata
             for the output LazyData object is copied from the input data object.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube, or any other object containing metadata that the constraint object can read
        @param constraint: An instance of a Constraint subclass which takes a data object and returns a subset of that data
                            based on it's internal parameters
        @param kernel: An instance of a Kernel subclass which takes a number of points and returns a single value
        @return: A single LazyData object
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData
        import numpy as np

        metadata = data.metadata

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data_points = data.get_non_masked_points()
        else:
            data_points = data

        logging.info("--> colocating...")

        points = points.get_coordinates_points()

        # Fill will the FillValue from the start
        values = np.zeros(len(points)) + constraint.fill_value

        for i, point in enumerate(points):
            con_points = constraint.constrain_points(point, data_points)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                pass
        new_data = LazyData(values, metadata)
        if self.var_name: new_data.metadata._name = self.var_name
        if self.var_long_name: new_data.metadata.long_name = self.var_long_name
        if self.var_units: new_data.units = self.var_units
        new_data.metadata.shape = (len(points),)
        new_data.metadata.missing_value = constraint.fill_value

        return [new_data]


class AverageColocator(Colocator):

    def __init__(self, var_name='', var_long_name='', var_units='',stddev_name='',nopoints_name=''):
        super(AverageColocator, self).__init__()
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units
        self.stddev_name = stddev_name
        self.nopoints_name = nopoints_name

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator takes a list of HyperPoints and a data object (currently either Ungridded data or a Cube) and returns
             one new LazyData object with the values as determined by the constraint and kernel objects. The metadata
             for the output LazyData object is copied from the input data object.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube, or any other object containing metadata that the constraint object can read
        @param constraint: An instance of a Constraint subclass which takes a data object and returns a subset of that data
                            based on it's internal parameters
        @param kernel: An instance of a Kernel subclass which takes a number of points and returns a single value - This
                            should be full_average - no other kernels currently return multiple values
        @return: One LazyData object for the mean of the constrained values, one for the standard deviation and another
                    for the number of points in the constrained set for which the mean was calculated
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData, Metadata
        from jasmin_cis.exceptions import ClassNotFoundError

        import numpy as np

        metadata = data.metadata

        if not isinstance(kernel, full_average):
            raise ClassNotFoundError("Invalid kernel specified for this colocator. Should be 'full_average'.")

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data_points = data.get_non_masked_points()
        else:
            data_points = data

        logging.info("--> colocating...")

        # Fill will the FillValue from the start
        means = np.zeros(len(points)) + constraint.fill_value
        stddev = np.zeros(len(points)) + constraint.fill_value
        nopoints = np.zeros(len(points)) + constraint.fill_value

        for i, point in enumerate(points):
            con_points = constraint.constrain_points(point, data_points)
            try:
                means[i], stddev[i], nopoints[i] = kernel.get_value(point, con_points)
            except ValueError:
                pass

        mean_data = LazyData(means, metadata)
        if self.var_name:
            mean_data.metadata._name = self.var_name
        else:
            mean_data.metadata._name = mean_data.name() + '_mean'
        if self.var_long_name: mean_data.metadata.long_name = self.var_long_name
        if self.var_units: mean_data.units = self.var_units
        mean_data.metadata.shape = (len(points),)
        mean_data.metadata.missing_value = constraint.fill_value

        if not self.stddev_name:
            self.stddev_name = mean_data.name()+'_std_dev'
        stddev_data = LazyData(stddev, Metadata(name=self.stddev_name,
                                                long_name='Standard deviation from the mean in '+metadata._name,
                                                shape=(len(points),), missing_value=constraint.fill_value, units=mean_data.units))

        if not self.nopoints_name:
            self.nopoints_name = mean_data.name()+'_no_points'
        nopoints_data = LazyData(nopoints, Metadata(name=self.nopoints_name,
                                                    long_name='Number of points used to calculate the mean of '+metadata._name,
                                                    shape=(len(points),), missing_value=constraint.fill_value, units='1'))

        return [mean_data, stddev_data, nopoints_data]


class DifferenceColocator(Colocator):

    def __init__(self, var_name='', var_long_name='', var_units='', diff_name='difference', diff_long_name=''):
        super(DifferenceColocator, self).__init__()
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units
        self.diff_name = diff_name
        self.diff_long_name= diff_long_name

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator takes a list of HyperPoints and a data object (currently either Ungridded data or a Cube) and returns
             one new LazyData object with the values as determined by the constraint and kernel objects. The metadata
             for the output LazyData object is copied from the input data object.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube, or any other object containing metadata that the constraint object can read
        @param constraint: An instance of a Constraint subclass which takes a data object and returns a subset of that data
                            based on it's internal parameters
        @param kernel: An instance of a Kernel subclass which takes a number of points and returns a single value
        @return: One LazyData object for the colocated data, and another for the difference between that data and the sample data
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData, Metadata
        import numpy as np

        metadata = data.metadata

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data_points = data.get_non_masked_points()
        else:
            data_points = data

        logging.info("--> colocating...")

        # Fill will the FillValue from the start
        values = np.zeros(len(points)) + constraint.fill_value
        difference = np.zeros(len(points)) + constraint.fill_value

        for i, point in enumerate(points):
            con_points = constraint.constrain_points(point, data_points)
            try:
                values[i] = kernel.get_value(point, con_points)
                difference[i] = values[i] - point.val[0]
            except ValueError:
                pass

        val_data = LazyData(values, metadata)
        if self.var_name: val_data.metadata._name = self.var_name
        if self.var_long_name: val_data.metadata.long_name = self.var_long_name
        if self.var_units: val_data.units = self.var_units
        val_data.metadata.shape = (len(points),)
        val_data.metadata.missing_value = constraint.fill_value

        if not self.diff_long_name: self.diff_long_name = 'Difference between given variable and sampling values'
        diff_data = LazyData(difference, Metadata(name=self.diff_name, long_name=self.diff_long_name, shape=(len(points),),
                                                  missing_value=constraint.fill_value, units=val_data.units))

        return [val_data, diff_data]


class DebugColocator(Colocator):

    def __init__(self, max_vals=1000, print_step=10.0):
        super(DebugColocator, self).__init__()
        self.max_vals = int(max_vals)
        self.print_step = float(print_step)

    def colocate(self, points, data, constraint, kernel):
        # This is the same colocate method as above with extra logging and timing steps. This is useful for debugging
        #  but will be slower than the default colocator.
        from jasmin_cis.data_io.ungridded_data import LazyData, UngriddedData
        import numpy as np
        import math
        from time import time

        metadata = data.metadata

        # Convert ungridded data to a list of points
        if isinstance(data, UngriddedData):
            data_points = data.get_non_masked_points()
        else:
            data_points = data

        logging.info("--> colocating...")

        # Only colocate a certain number of points, as a quick test
        short_points = points if len(points)<self.max_vals else points[:self.max_vals-1]

        # We still need to output the full size list, to match the size of the coordinates
        values = np.zeros(len(points)) + constraint.fill_value

        times = np.zeros(len(short_points))
        for i, point in enumerate(short_points):

            t1 = time()

            # colocate using a constraint and a kernel
            con_points = constraint.constrain_points(point, data_points)
            try:
                values[i] = kernel.get_value(point, con_points)
            except ValueError:
                pass

            # print debug information to screen
            times[i] = time() - t1
            frac, rem = math.modf(i/self.print_step)
            if frac == 0: print str(i) + " - took: " + str(times[i]) + "s" + " -  sample: " + str(point) + " - colocated value: " + str(values[i])

        logging.info("Average time per point: " + str(np.sum(times)/len(short_points)))
        new_data = LazyData(values, metadata)
        new_data.metadata.shape = (len(points),)
        new_data.metadata.missing_value = constraint.fill_value
        return [new_data]


class DummyColocator(Colocator):

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator does no colocation at all - it just returns the original data values. This might be useful
            if the input data for one variable is already known to be on the same grid as points. This routine could
            check the coordinates are the same but currently does no such check.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube
        @param constraint: Unused
        @param kernel: Unused
        @return: A single LazyData object
        '''
        from jasmin_cis.data_io.ungridded_data import LazyData

        logging.info("--> colocating...")

        new_data = LazyData(data.data, data.metadata)
        return [new_data]


class DummyConstraint(Constraint):

    def constrain_points(self, point, data):
        # This is a null constraint - all of the points just get passed back
        return data


class SepConstraint(PointConstraint):

    def __init__(self, h_sep=None, a_sep=None, p_sep=None, t_sep=None, fill_value=None):
        from jasmin_cis.exceptions import InvalidCommandLineOptionError

        super(SepConstraint, self).__init__()
        if fill_value is not None:
            try:
                self.fill_value = float(fill_value)
            except ValueError:
                raise InvalidCommandLineOptionError('Separation Constraint fill_value must be a valid float')
        self.checks = []
        if h_sep is not None:
            self.h_sep = jasmin_cis.utils.parse_distance_with_units_to_float_km(h_sep)
            self.checks.append(self.horizontal_constraint)
        if a_sep is not None:
            self.a_sep = jasmin_cis.utils.parse_distance_with_units_to_float_m(a_sep)
            self.checks.append(self.alt_constraint)
        if p_sep is not None:
            try:
                self.p_sep = float(p_sep)
            except:
                raise InvalidCommandLineOptionError('Separation Constraint p_sep must be a valid float')
            self.checks.append(self.pressure_constraint)
        if t_sep is not None:
            from jasmin_cis.time_util import parse_datetimestr_delta_to_float_days
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


class mean(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using the mean of any points left after a constraint.
        '''
        from numpy import mean
        values = data.vals
        if len(values) == 0: raise ValueError
        return mean(values)


class full_average(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using the mean of any points left after a constraint. Also returns the standard
             deviation and the number of points
        '''
        from numpy import mean, std
        values = data.vals
        num_values = len(values)
        if num_values == 0: raise ValueError
        return (mean(values), std(values), num_values)


class nn_horizontal(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours along the face of the earth where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        iterator = data.__iter__()
        try:
            nearest_point = iterator.next()
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.compdist(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_altitude(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in altitude, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        iterator = data.__iter__()
        try:
            nearest_point = iterator.next()
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.compalt(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_pressure(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in pressure, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        iterator = data.__iter__()
        try:
            nearest_point = iterator.next()
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.comppres(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_time(Kernel):

    def get_value(self, point, data):
        '''
            Colocation using nearest neighbours in time, where both points and
              data are a list of HyperPoints. The default point is the first point.
        '''
        iterator = data.__iter__()
        try:
            nearest_point = iterator.next()
        except StopIteration:
            # No points to check
            raise ValueError
        for data_point in iterator:
            if point.comptime(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val[0]


class nn_gridded(Kernel):
    def get_value(self, point, data):
        '''
            Co-location routine using nearest neighbour algorithm optimized for gridded data.
             This calls out to iris to do the work.
        '''
        from iris.analysis.interpolate import nearest_neighbour_data_value
        return nearest_neighbour_data_value(data, point.coord_tuple)


class li(Kernel):
    def get_value(self, point, data):
        '''
            Co-location routine using iris' linear interpolation algorithm. This only makes sense for gridded data.
        '''
        from iris.analysis.interpolate import linear
        return linear(data, point.coord_tuple).data


class GriddedColocator(DefaultColocator):

    def __init__(self, var_name='', var_long_name='', var_units=''):
        super(DefaultColocator, self).__init__()
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units

    def colocate(self, points, data, constraint, kernel):
        '''
            This colocator takes a list of HyperPoints and a data object (currently either Ungridded data or a Cube) and returns
             one new LazyData object with the values as determined by the constraint and kernel objects. The metadata
             for the output LazyData object is copied from the input data object.
        @param points: A list of HyperPoints
        @param data: An UngriddedData object or Cube, or any other object containing metadata that the constraint object can read
        @param constraint: An instance of a Constraint subclass which takes a data object and returns a subset of that data
                            based on it's internal parameters
        @param kernel: An instance of a Kernel subclass which takes a numberof points and returns a single value
        @return: A single LazyData object
        '''
        import iris
        from jasmin_cis.exceptions import ClassNotFoundError

        if not (isinstance(kernel, gridded_gridded_nn) or isinstance(kernel, gridded_gridded_li)):
            raise ClassNotFoundError("Expected kernel of one of classes {}; found one of class {}".format(
                str([jasmin_cis.utils.get_class_name(gridded_gridded_nn),
                    jasmin_cis.utils.get_class_name(gridded_gridded_li)]),
                    jasmin_cis.utils.get_class_name(type(kernel))))

        new_data = iris.analysis.interpolate.regrid(data, points, mode=kernel.name)#, **kwargs)

        return [new_data]


class gridded_gridded_nn(Kernel):
    def __init__(self):
        self.name = 'nearest'

    def get_value(self, point, data):
        '''Not needed for gridded/gridded co-location.
        '''
        raise ValueError("gridded_gridded_nn kernel selected for use with colocator other than GriddedColocator")

class gridded_gridded_li(Kernel):
    def __init__(self):
        self.name = 'bilinear'

    def get_value(self, point, data):
        '''Not needed for gridded/gridded co-location.
        '''
        raise ValueError("gridded_gridded_li kernel selected for use with colocator other than GriddedColocator")


class UngriddedGriddedColocator(Colocator):
    """Performs co-location of ungridded data onto a the points of a cube.
    """
    def __init__(self, var_name='', var_long_name='', var_units=''):
        super(UngriddedGriddedColocator, self).__init__()
        #TODO These are not used - use or remove everywhere.
        self.var_name = var_name
        self.var_long_name = var_long_name
        self.var_units = var_units

    def colocate(self, points, data, constraint, kernel):
        """
        @param points: cube defining the sample points
        @param data: UngriddedData object providing data to be co-located
        @param constraint: instance of a Constraint subclass, which takes a data object and returns a subset of that
                           data based on it's internal parameters
        @param kernel: instance of a Kernel subclass which takes a number of points and returns a single value
        @return: Cube of co-located data
        """
        from jasmin_cis.exceptions import ClassNotFoundError

        # Constraint must be appropriate for gridded sample.
        if not (isinstance(constraint, CellConstraint) or isinstance(constraint, IndexedConstraint)):
            raise ClassNotFoundError("Expected constraint of subclass of one of {}; found one of class {}".format(
                str([jasmin_cis.utils.get_class_name(CellConstraint),
                     jasmin_cis.utils.get_class_name(IndexedConstraint)]),
                jasmin_cis.utils.get_class_name(type(constraint))))

        # Only support the mean kernel currently.
        # if not isinstance(kernel, mean):
        #     raise ClassNotFoundError("Expected kernel of class {}; found one of class {}".format(
        #         jasmin_cis.utils.get_class_name(mean), jasmin_cis.utils.get_class_name(type(kernel))))

        if isinstance(data, UngriddedData):
            data_points = data.get_non_masked_points()
        else:
            raise ValueError("UngriddedGriddedColocator requires ungridded data to colocate")

        # If there are coordinates in the sample grid that are not present for the data,
        # omit the from the set of coordinates in the output grid. Find a mask of coordinates
        # that are present to use when determining the output grid shape.
        # coordinate_mask = self._find_data_coords(data)
        coordinate_mask = [False if c is None else True for c in data.coords().find_standard_coords()]

        # Work out how to iterate over the cube and map HyperPoint coordinates to cube coordinates.
        coord_map = self._find_standard_coords(points, coordinate_mask)
        coords = points.coords()
        shape = []
        output_coords = []

        # Find shape of coordinates to be iterated over.
        for (hpi, ci, shi) in coord_map:
            if ci is not None:
                coord = coords[ci]
                if coord.ndim > 1:
                    raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                              " than one is not supported (coordinate %s)", coord.name())
                # Ensure that bounds exist.
                if not coord.has_bounds():
                    logging.info("Creating guessed bounds as none exist in file")
                    coord.guess_bounds()
                shape.append(coord.shape[0])
                output_coords.append(coord)

        self._fix_longitude_range(coords, data_points)

        # Create index if constraint supports it.
        indexed_constraint = isinstance(constraint, IndexedConstraint)
        if indexed_constraint:
            logging.info("--> Indexing data...")
            constraint.index_data(coords, data_points, coord_map)

        # Initialise output array as initially all masked, and set the appropriate fill value.
        values = np.ma.zeros(shape)
        values.mask = True
        values.fill_value = constraint.fill_value

        logging.info("--> Co-locating...")

        # Iterate over cells in cube.
        num_cells = np.product(shape)
        cell_count = 0
        cell_total = 0
        for indices in jasmin_cis.utils.index_iterator(shape):
            hp_values = [None] * HyperPoint.number_standard_names
            hp_cell_values = [None] * HyperPoint.number_standard_names
            for (hpi, ci, shi) in coord_map:
                if ci is not None:
                    hp_values[hpi] = coords[ci].points[indices[shi]]
                    hp_cell_values[hpi] = coords[ci].cell(indices[shi])

            hp_cell = HyperPoint(*hp_cell_values)
            hp = HyperPoint(*hp_values)
            if indexed_constraint:
                arg = indices
            else:
                arg = hp_cell
            con_points = constraint.constrain_points(arg, data_points)
            # logging.debug("UngriddedGriddedColocator: point {} number constrained points {}".format(str(hp), len(con_points)))
            try:
                values[indices] = kernel.get_value(hp, con_points)
            except ValueError:
                pass

            # Log progress periodically.
            cell_count += 1
            cell_total += 1
            if cell_count == 10000:
                logging.info("    Processed %d points of %d (%d%%)", cell_total, num_cells, int(cell_total * 100 / num_cells))
                cell_count = 0

        # Construct an output cube containing the colocated data.
        cube = self._create_colocated_cube(points, data, values, output_coords, constraint.fill_value)

        return [cube]

    def _find_data_coords(self, data):
        """Checks the first data point to determine which coordinates are present.
        @param data: HyperPointList of data
        @return: list of booleans indicating HyperPoint coordinates that are present
        """
        point = data[0]
        coordinate_mask = [True] * HyperPoint.number_standard_names
        for idx in xrange(HyperPoint.number_standard_names):
            if point[idx] is None:
                coordinate_mask[idx] = False
        return coordinate_mask

    def _find_standard_coords(self, cube, coordinate_mask):
        """Finds the mapping of cube coordinates to the standard ones used by HyperPoint.

        @param cube: cube among the coordinates of which to find the standard coordinates
        @param coordinate_mask: list of booleans indicating HyperPoint coordinates that are present
        @return: list of tuples relating index in HyperPoint to index in coords and in coords to be iterated over
        """
        coord_map = []
        coord_lookup = {}
        for idx, coord in enumerate(cube.coords()):
            coord_lookup[coord] = idx

        shape_idx = 0
        for hpi, name in enumerate(HyperPoint.standard_names):
            if coordinate_mask[hpi]:
                coords = cube.coords(standard_name=name)
                if len(coords) > 1:
                    msg = ('Expected to find exactly 1 coordinate, but found %d. They were: %s.'
                           % (len(coords), ', '.join(coord.name() for coord in coords)))
                    raise jasmin_cis.exceptions.CoordinateNotFoundError(msg)
                elif len(coords) == 1:
                    coord_map.append((hpi, coord_lookup[coords[0]], shape_idx))
                    shape_idx += 1
                else:
                    coord_map.append((hpi, None, None))
            else:
                # Ignore this coordinate.
                coord_map.append((hpi, None, None))
        return coord_map

    def _find_longitude_range(self, coords):
        """Finds the start of the longitude range, assumed to be either 0,360 or -180,180
        @param coords: coordinates to check
        @return: starting value for longitude range or None if no longitude coordinate found
        """
        low = None
        for coord in coords:
            if coord.standard_name == 'longitude':
                low = 0.0
                min_val = coord.points.min()
                if min_val < 0.0:
                    low = -180.0
        return low

    def _fix_longitude_range(self, coords, data_points):
        """
        @param coords: coordinates for grid on which to colocate
        @param data_points: HyperPointList of data to fix
        """
        range_start = self._find_longitude_range(coords)
        if range_start is not None:
            range_end = range_start + 360.0
            for idx, point in enumerate(data_points):
                modified = False
                if point.longitude < range_start:
                    new_long = point.longitude + 360.0
                    modified = True
                elif point.longitude > range_end:
                    new_long = point.longitude - 360.0
                    modified = True
                if modified:
                    new_point = point.modified(lon=new_long)
                    data_points[idx] = new_point

    def _create_colocated_cube(self, src_cube, src_data, data, coords, fill_value):
        """Creates a cube using the metadata from the source cube and supplied data.

        @param src_cube: cube of sample points
        @param src_data: ungridded data that was to be colocated
        @param data: colocated data values
        @param coords: coordinates for output cube
        @param fill_value: value that has been used as the fill value in data
        @return: cube of colocated data
        """
        dim_coords_and_dims = []
        for idx, coord in enumerate(coords):
            dim_coords_and_dims.append((coord, idx))
        metadata = src_data.metadata
        metadata.missing_value = fill_value
        cube = iris.cube.Cube(data, standard_name=src_data.standard_name,
                              long_name=src_data.long_name,
                              var_name=metadata._name,
                              units=src_data.units,
                              dim_coords_and_dims=dim_coords_and_dims)
        #TODO Check if any other keyword arguments should be set:
        # cube = iris.cube.Cube(data, standard_name=None, long_name=None, var_name=None, units=None,
        #                       attributes=None, cell_methods=None, dim_coords_and_dims=None, aux_coords_and_dims=None,
        #                       aux_factories=None, data_manager=None)
        return cube


class CubeCellConstraint(CellConstraint):
    """Constraint for constraining HyperPoints to be within an iris.coords.Cell.
    """
    def __init__(self, fill_value=None):
        super(CubeCellConstraint, self).__init__()
        if fill_value is not None:
            try:
                self.fill_value = float(fill_value)
            except ValueError:
                raise jasmin_cis.exceptions.InvalidCommandLineOptionError(
                    'Cube Cell Constraint fill_value must be a valid float')

    def constrain_points(self, sample_point, data):
        """Returns HyperPoints lying within a cell.
        @param sample_point: HyperPoint of cells defining sample region
        @param data: list of HyperPoints to check
        @return: HyperPointList of points found within cell
        """
        con_points = HyperPointList()
        for point in data:
            include = True
            for idx in xrange(HyperPoint.number_standard_names):
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
    def __init__(self, fill_value=None):
        super(BinningCubeCellConstraint, self).__init__()
        self.index = None
        if fill_value is not None:
            try:
                self.fill_value = float(fill_value)
            except ValueError:
                raise jasmin_cis.exceptions.InvalidCommandLineOptionError(
                    'Cube Cell Constraint fill_value must be a valid float')

    def constrain_points(self, sample_point, data):
        """Returns HyperPoints lying within a cell.

        This implementation returns the points that have been stored in the
        appropriate bin by the index_data method.
        @param sample_point: HyperPoint of cells defining sample region
        @param data: list of HyperPoints to check
        @return: HyperPointList of points found within cell
        """
        point_list = self.index[tuple(sample_point)]
        con_points = HyperPointList()
        if point_list is not None:
            for point in point_list:
                con_points.append(data[point])
        return con_points

    def index_data(self, coords, data, coord_map):
        """
        @param coords: coordinates of grid
        @param data: list of HyperPoints to index
        @param coord_map: list of tuples relating index in HyperPoint to index in coords and in
                          coords to be iterated over
        """
        # Create an index array matching the shape of the coordinates to be iterated over.
        shape = []
        for (hpi, ci, shi) in coord_map:
            if ci is not None:
                shape.append(len(coords[ci].points))
        num_cell_indices = len(shape)

        # Set a logging interval.
        num_bin_checks = sum([math.log(x) for x in shape])
        log_every_points = 2000000 / num_bin_checks
        log_every_points -= log_every_points % 100
        log_every_points = max(log_every_points, 100)

        # Create the index, which will be an array containing of a lists of data points that are
        # within each cell.
        self.index = np.empty(tuple(shape), dtype=np.dtype(object))
        self.index.fill(None)

        coord_descreasing = [False] * len(coords)
        coord_lengths = [0] * len(coords)
        for (hpi, ci, shi) in coord_map:
            if ci is not None:
                coord = coords[ci]
                # Coordinates must be monotonic; determine whether increasing or decreasing.
                if len(coord.points) > 1:
                    if coord.points[1] < coord.points[0]:
                        coord_descreasing[ci] = True
                coord_lengths[ci] = len(coord.points)

        # Populate the index by finding the cell containing each data point.
        num_points = len(data)
        pt_count = 0
        pt_total = 0
        for pt_idx, point in data.enumerate_non_masked_points():
            if point.val[0] is np.ma.masked:
                continue
            point_cell_indices = [None] * num_cell_indices

            # Find the interval that the point resides in for each relevant coordinate.
            for (hpi, ci, shi) in coord_map:
                if ci is not None:
                    coord = coords[ci]
                    if coord_descreasing[ci]:
                        # Use reversed view of bounds array.
                        lower_bounds = coord.bounds[::-1, 1]
                        upper_bounds = coord.bounds[::-1, 0]
                        search_index = np.searchsorted(lower_bounds, point[hpi], side='right') - 1
                        cell_index = coord_lengths[ci] - search_index - 1
                    else:
                        lower_bounds = coord.bounds[::, 0]
                        upper_bounds = coord.bounds[::, 1]
                        search_index = np.searchsorted(lower_bounds, point[hpi], side='right') - 1
                        cell_index = search_index
                    if (search_index >= 0) and (point[hpi] <= upper_bounds[search_index]):
                        point_cell_indices[shi] = cell_index

            # Add point to index if a containing interval was found for each coordinate.
            if point_cell_indices.count(None) == 0:
                index_entry = self.index[tuple(point_cell_indices)]
                if index_entry is None:
                    index_entry = []
                index_entry.append(pt_idx)
                self.index[tuple(point_cell_indices)] = index_entry

            # Periodically log progress.
            pt_count += 1
            pt_total += 1
            if pt_count == log_every_points:
                logging.info("    Indexed %d points of %d (%d%%)",
                             pt_total, num_points, int(pt_total * 100 / num_points))
                pt_count = 0
