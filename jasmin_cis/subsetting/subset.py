import logging
import math

from iris import cube, coords
from iris.exceptions import IrisError
import iris.unit
import iris.util

import jasmin_cis.exceptions as ex
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.data_io.read import read_data
from jasmin_cis.subsetting.subsetter import Subsetter
from jasmin_cis.subsetting.subset_constraint import GriddedSubsetConstraint, UngriddedSubsetConstraint
from jasmin_cis.data_io.write_netcdf import add_data_to_file, write_coordinates
from jasmin_cis.cis import __version__
from jasmin_cis.utils import remove_file_prefix, guess_coord_axis


class Subset(object):
    def __init__(self, limits, output_file):
        self._limits = limits
        self._output_file = output_file

    def subset(self, variable, filenames, product):
        # Read the input data - the parser limits the number of data groups to one for this command.
        data = None
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variable: %s", variable)
            data = read_data(filenames, variable, product)
        except (IrisError, ex.InvalidVariableError) as e:
            raise ex.CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise ex.CISError("There was an error reading one of the files: \n" + str(e))

        # Set subset constraint type according to the type of the data object.
        if isinstance(data, cube.Cube):
            # Gridded data on Cube
            subset_constraint = GriddedSubsetConstraint()
        else:
            # Generic ungridded data
            subset_constraint = UngriddedSubsetConstraint()

        self._set_constraint_limits(data, subset_constraint)
        subsetter = Subsetter()
        subset = subsetter.subset(data, subset_constraint)

        if subset is None:
            # Constraints exclude all data.
            raise ex.NoDataInSubsetError("No output created - constraints exclude all data")
        else:
            history = "Subsetted using CIS version " + __version__ + \
                      "\nvariable: " + str(variable) + \
                      "\nfrom files: " + str(filenames) + \
                      "\nusing limits: " + str(subset_constraint)
            subset.add_history(history)

            subset.save_data(self._output_file, subset, True)

    def _set_constraint_limits(self, data, subset_constraint):
        for coord in data.coords():
            # Match user-specified limits with dimensions found in data.
            guessed_axis = guess_coord_axis(coord)
            limit = None
            if coord.name() in self._limits:
                limit = self._limits[coord.name()]
            elif guessed_axis is not None:
                if guessed_axis in self._limits:
                    limit = self._limits[guessed_axis]
                elif guessed_axis.lower() in self._limits:
                    limit = self._limits[guessed_axis.lower()]

            if limit is not None:
                wrapped = False
                if limit.is_time or guessed_axis == 'T':
                    # Ensure that the limits are date/times.
                    dt = parse_datetime.convert_datetime_components_to_datetime(limit.start, True)
                    limit_start = self._convert_datetime_to_coord_unit(coord, dt)
                    dt = parse_datetime.convert_datetime_components_to_datetime(limit.end, False)
                    limit_end = self._convert_datetime_to_coord_unit(coord, dt)
                elif guessed_axis == 'X':
                    # Handle circularity.
                    (limit_start, limit_end, wrapped) = self._fix_longitude_limits_for_coord(float(limit.start),
                                                                                             float(limit.end),
                                                                                             coord)
                else:
                    # Assume to be a non-time axis.
                    (limit_start, limit_end) = self._fix_non_circular_limits(float(limit.start), float(limit.end))
                subset_constraint.set_limit(coord, limit_start, limit_end, wrapped)

    @staticmethod
    def _convert_datetime_to_coord_unit(coord, dt):
        """Converts a datetime to be in the unit of a specified Coord.
        """
        if isinstance(coord, iris.coords.Coord):
            # The unit class is then iris.unit.Unit.
            iris_unit = coord.units
        else:
            iris_unit = iris.unit.Unit(coord.units)
        return iris_unit.date2num(dt)

    @staticmethod
    def _convert_coord_unit_to_datetime(coord, dt):
        """Converts a datetime to be in the unit of a specified Coord.
        """
        if isinstance(coord, iris.coords.Coord):
            # The unit class is then iris.unit.Unit.
            iris_unit = coord.units
        else:
            iris_unit = iris.unit.Unit(coord.units)
        return iris_unit.num2date(dt)

    @staticmethod
    def _fix_longitude_limits_for_coord(limit_start, limit_end, coord):
        #TODO Also check unit as degrees or degrees_east?
        # Would like to do the following but UngriddedData coord does not have circular attribute.
        # if hasattr(coord, 'circular') and coord.circular:
        if isinstance(coord, iris.coords.Coord):
            coord_min = coord.points.min()
            coord_max = coord.points.max()
        else:
            coord_min = coord.data.min()
            coord_max = coord.data.max()

        return Subset._fix_longitude_limits(limit_start, limit_end, coord_min, coord_max)

    @staticmethod
    def _fix_longitude_limits(limit_start, limit_end, coord_min, coord_max):
        new_limit_start = limit_start
        new_limit_end = limit_end
        limit_min = 0.0
        do_fix = False
        # Only attempt to modify limits if outside of range of coordinate values.
        if not ((coord_min <= limit_start <= coord_max) and (coord_min <= limit_end <= coord_max)):
            # Determine if -180,180 or 0,360 range is compatible - if neither: do not attempt to fix.
            if (-180.0 <= coord_min < 0.0) and (coord_max <= 180.0):
                do_fix = True
                limit_min = -180.0
            elif (0.0 <= coord_min) and (coord_max <= 360.0):
                do_fix = True
                limit_min = 0.0
        if do_fix:
            new_limit_start = Subset._fix_angular_limit(limit_start, limit_min)
            new_limit_end = Subset._fix_angular_limit(limit_end, limit_min)
            logging.info("Angular limits: original: %s  after fix: %s",
                         (limit_start, limit_end), (new_limit_start, new_limit_end))

        wrapped = new_limit_start > new_limit_end

        return new_limit_start, new_limit_end, wrapped

    @staticmethod
    def _fix_angular_limit(value, range_start):
        """Force an angular variable to be within the 360 range starting from limit_start.
        :param value: value to be fixed to be within the range
        :param range_start: value at start of 360 range assuming -180 <= range_start <= 0.0
        """
        # Narrow to range -360 to 360.
        ret = math.fmod(value, 360.0)
        # Restrict to 360 range starting at range_start.
        if ret < range_start:
            ret += 360.0
        if ret > range_start + 360.0:
            ret -= 360.0
        return ret

    @staticmethod
    def _fix_non_circular_limits(limit_start, limit_end):
        if limit_start <= limit_end:
            new_limits = (limit_start, limit_end)
        else:
            new_limits = (limit_end, limit_start)
            logging.info("Real limits: original: %s  after fix: %s", (limit_start, limit_end), new_limits)

        return new_limits
