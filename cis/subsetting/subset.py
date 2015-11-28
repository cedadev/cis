import logging

from iris import coords
from iris.exceptions import IrisError
import iris.unit
import iris.util

from cis.data_io.data_reader import DataReader
from cis.data_io.data_writer import DataWriter
import cis.exceptions as ex
import cis.parse_datetime as parse_datetime
from cis.subsetting.subsetter import Subsetter
from cis.subsetting.subset_constraint import GriddedSubsetConstraint, UngriddedSubsetConstraint
from cis import __version__
from cis.utils import guess_coord_axis


class Subset(object):
    """
    Class for subsetting Ungridded or Gridded data either temporally, or spatially or both.
    """

    def __init__(self, limits, output_file, subsetter=Subsetter(), data_reader=DataReader(), data_writer=DataWriter()):
        """
        Constructor

        :param dict limits: A dictionary of dimension_name:SubsetLimits key value pairs.
        :param output_file: The filename to output the result to
        :param subsetter: Optional :class:`Subsetter` configuration object
        :param data_reader: Optional :class:`DataReader` configuration object
        :param data_writer: Optional :class:`DataWriter` configuration object
        """
        self._limits = limits
        self._output_file = output_file
        self._subsetter = subsetter
        self._data_reader = data_reader
        self._data_writer = data_writer

    def subset(self, variables, filenames, product=None):
        """
        Subset the given variables based on the initialised limits

        :param variables: One or more variables to read from the files
        :type variables: string or list
        :param filenames: One or more filenames of the files to read
        :type filenames: string or list
        :param str product: Name of data product to use (optional)
        """
        # Read the input data - the parser limits the number of data groups to one for this command.
        data = None
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variables: %s", variables)
            data = self._data_reader.read_data_list(filenames, variables, product)
        except (IrisError, ex.InvalidVariableError) as e:
            raise ex.CISError("There was an error reading in data: \n" + str(e))
        except IOError as e:
            raise ex.CISError("There was an error reading one of the files: \n" + str(e))

        # Set subset constraint type according to the type of the data object.
        if data.is_gridded:
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
        """
        Identify and set the constraint limits on the subset_constraint object using the coordinates from the data
        object

        :param data: The data object containing the coordinates to subset
        :param subset_constraint: The constraint object on to which to apply the limits
        """
        from cis.exceptions import InvalidOperationError
        from utils import standard_axes

        for axis, limit in self._limits.iteritems():
            # Find the coordinate matching either the axis, or name, or guessed standard name
            # We use a set to remove any duplicates which might occur if we match for both axis and standard name.
            coords = set(data.coords(axis=axis) +
                         data.coords(name=axis) +
                         data.coords(standard_name=standard_axes[axis.upper()]))

            # Take out the single coordinate
            try:
                coord = coords.pop()
            except KeyError:
                raise (InvalidOperationError("Could not find a coordinate matching: " + axis))

            # Parse the limits
            if limit.is_time or axis == 'T':
                # Ensure that the limits are date/times.
                dt = parse_datetime.convert_datetime_components_to_datetime(limit.start, True)
                limit_start = self._convert_datetime_to_coord_unit(coord, dt)
                dt = parse_datetime.convert_datetime_components_to_datetime(limit.end, False)
                limit_end = self._convert_datetime_to_coord_unit(coord, dt)
            else:
                # Assume to be a non-time axis.
                (limit_start, limit_end) = self._fix_non_circular_limits(float(limit.start), float(limit.end))
            # Apply the limit to the constraint object
            subset_constraint.set_limit(coord, limit_start, limit_end)

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
    def _fix_non_circular_limits(limit_start, limit_end):
        if limit_start <= limit_end:
            new_limits = (limit_start, limit_end)
        else:
            new_limits = (limit_end, limit_start)
            logging.info("Real limits: original: %s  after fix: %s", (limit_start, limit_end), new_limits)

        return new_limits
