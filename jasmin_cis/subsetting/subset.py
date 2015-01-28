import logging
import math

from iris import cube, coords
from iris.exceptions import IrisError
import iris.unit
import iris.util

from jasmin_cis.data_io.data_reader import DataReader
from jasmin_cis.data_io.data_writer import DataWriter
import jasmin_cis.exceptions as ex
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.subsetting.subsetter import Subsetter
from jasmin_cis.subsetting.subset_constraint import GriddedSubsetConstraint, UngriddedSubsetConstraint
from jasmin_cis.cis import __version__
from jasmin_cis.utils import guess_coord_axis


class Subset(object):
    def __init__(self, limits, output_file, subsetter=Subsetter(), data_reader=DataReader(), data_writer=DataWriter()):
        self._limits = limits
        self._output_file = output_file
        self._subsetter = subsetter
        self._data_reader = data_reader
        self._data_writer = data_writer

    def subset(self, variables, filenames, product):
        # Read the input data - the parser limits the number of data groups to one for this command.
        data = None
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variables: %s", variables)
            data = self._data_reader.read_data(filenames, variables, product)
        except (IrisError, ex.InvalidVariableError) as e:
            raise ex.CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise ex.CISError("There was an error reading one of the files: \n" + str(e))

        # Set subset constraint type according to the type of the data object.
        if isinstance(data, cube.Cube) or isinstance(data, cube.CubeList):
            # Gridded data on Cube
            subset_constraint = GriddedSubsetConstraint()
        else:
            # Generic ungridded data
            subset_constraint = UngriddedSubsetConstraint()

        self._set_constraint_limits(data, subset_constraint)
        subset = self._subsetter.subset(data, subset_constraint)

        if subset is None:
            # Constraints exclude all data.
            raise ex.NoDataInSubsetError("No output created - constraints exclude all data")
        else:
            history = "Subsetted using CIS version " + __version__ + \
                      "\nvariables: " + str(variables) + \
                      "\nfrom files: " + str(filenames) + \
                      "\nusing limits: " + str(subset_constraint)
            subset.add_history(history)
            self._data_writer.write_data(subset, self._output_file)

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
        """
        Move the requested longitude subset limits to match the range of the coordinates in the data. E.g. if the
        requested limits are 'x=[-90, 90]' and the data coordinates actually go from 0 -> 360 rather than -180 -> 180
        then those limits should be moved to '90, 270 (and wrapped)'
        :param limit_start: Start limit requested
        :param limit_end: End limit requested
        :param coord_min: Coordinate min
        :param coord_max: Coordinate max
        :return: tuple of new_limit_start, new_limit_end, wrapped (boolean indicating if the coordinates 'wrap around')
        """
        new_limit_start = limit_start
        new_limit_end = limit_end
        data_below_zero = coord_min < 0
        data_above_180 = coord_max > 180
        limits_below_zero = limit_start < 0 or limit_end < 0
        limits_above_180 = limit_start > 180 or limit_end > 180

        if data_below_zero and not data_above_180:
            # i.e. data is in the range -180 -> 180
            # Only convert the limits if they are above 180:
            if limits_above_180 and not limits_below_zero:
                # Convert limits from 0-360 to -180 to 180
                range_start = -180
                new_limit_start = Subset._fix_angular_limit(limit_start, range_start)
                new_limit_end = Subset._fix_angular_limit(limit_end, range_start)
        elif data_above_180 and not data_below_zero:
            # i.e. data is in the range 0 -> 360
            if limits_below_zero and not limits_above_180:
                # Convert limits from -180 to 180 to 0-360
                range_start = 0
                new_limit_start = Subset._fix_angular_limit(limit_start, range_start)
                new_limit_end = Subset._fix_angular_limit(limit_end, range_start)
        # Either data is all within the bounds 0-180 OR it's both below zero AND above 360
        # Never need to convert the limits in this case
        wrapped = new_limit_start > new_limit_end or (new_limit_start == new_limit_end and not limit_start == limit_end)

        # Output to the log if the limits were changed:
        if (new_limit_start, new_limit_end) == (limit_start, limit_end):
            log_text = "Angular limits: original: %s  after fix: %s" % ((limit_start, limit_end),
                                                                        (new_limit_start, new_limit_end))
            if wrapped:
                log_text += ' (limits wrapped)'
            logging.info(log_text)
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
