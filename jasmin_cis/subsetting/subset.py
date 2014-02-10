import logging
import sys

from iris import cube, coords
from iris.exceptions import IrisError
import iris.unit
import iris.util

import jasmin_cis.exceptions as ex
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.data_io.read import read_data
from jasmin_cis.subsetting.subsetter import Subsetter
from jasmin_cis.subsetting.subset_constraint import (GriddedSubsetConstraint, UngriddedOnGridSubsetConstraint,
                                                     UngriddedSubsetConstraint)
import jasmin_cis.time_util as time_util
from jasmin_cis.data_io.write_netcdf import add_data_to_file, write_coordinates
from jasmin_cis.cis import __version__


#TODO There should be a single fatal error exit function.
def _fatal_error(e):
    """
    Prints error message and exits the program.

    @param e: An error object or any string
    """
    sys.stderr.write(str(e) + "\n")
    exit(1)


class Subset(object):
    def __init__(self, variable, filenames, product, limits, output_file):
        self._variable = variable
        self._filenames = filenames
        self._product = product
        self._limits = limits
        self._output_file = output_file

    def subset(self):
        # Read the input data - the parser limits the number of data groups to one for this command.
        data = None
        try:
            # Read the data into a data object (either UngriddedData or Iris Cube), concatenating data from
            # the specified files.
            logging.info("Reading data for variable: %s", self._variable)
            data = read_data(self._filenames, self._variable, self._product)
        except (IrisError, ex.InvalidVariableError, ex.ClassNotFoundError) as e:
            _fatal_error(e)
        except IOError as e:
            _fatal_error("There was an error reading one of the files: \n" + str(e))

        # Set subset constraint type according to the type of the data object.
        if isinstance(data, cube.Cube):
            # Gridded data on Cube
            subset_constraint = GriddedSubsetConstraint()
        elif data.coords_on_grid:
            # UngriddedData object with data lying on grid
            subset_constraint = UngriddedOnGridSubsetConstraint()
        else:
            # Generic ungridded data
            subset_constraint = UngriddedSubsetConstraint()

        self._set_constraint_limits(data, subset_constraint)
        subsetter = Subsetter()
        subset = subsetter.subset(data, subset_constraint)

        if subset is None:
            # Constraints exclude all data.
            raise ex.NoDataInSubsetError("Constraints exclude all data")
        else:
            history = "Subsetted using CIS version " + __version__ + \
                      "\nvariable: " + str(self._variable) + \
                      "\nfrom files: " + str(self._filenames) + \
                      "\nusing limits: " + str(subset_constraint)

            if isinstance(subset, cube.Cube):
                subset.add_history(history)
                iris.save(subset, self._output_file)
            else:
                if hasattr(subset.metadata, 'history') and len(subset.metadata.history) > 0:
                    subset.metadata.history += '\n' + history
                else:
                    subset.metadata.history = history
                write_coordinates(subset.coords(), self._output_file)
                add_data_to_file(subset, self._output_file)

    def _set_constraint_limits(self, data, subset_constraint):
        for coord in data.coords():
            # Match user-specified limits with dimensions found in data.
            limit_dim = None
            guessed_axis = self._guess_coord_axis(coord)
            guessed_axis = None if guessed_axis is None else guessed_axis.lower()
            if coord.name() in self._limits:
                limit_dim = coord.name()
                limit = self._limits[coord.name()]
            elif (guessed_axis is not None) and (guessed_axis in self._limits):
                limit_dim = coord.name()
                limit = self._limits[guessed_axis]

            if limit_dim is not None:
                if limit.is_time or guessed_axis == 't':
                    # Ensure that the limits are date/times.
                    dt = parse_datetime.convert_datetime_components_to_datetime(limit.start, True)
                    limit_start = self._convert_datetime_to_coord_unit(coord, dt)
                    # limit_start = time_util.convert_datetime_to_std_time(dt)
                    dt = parse_datetime.convert_datetime_components_to_datetime(limit.end, False)
                    limit_end = self._convert_datetime_to_coord_unit(coord, dt)
                    # limit_end = time_util.convert_datetime_to_std_time(dt)
                else:
                    # Assume to be a non-time axis.
                    limit_start = float(limit.start)
                    limit_end = float(limit.end)
                subset_constraint.set_limit(limit_dim, coord, limit_start, limit_end)

    @staticmethod
    def _guess_coord_axis(coord):
        #TODO Can more be done for ungridded based on units, as with iris.util.guess_coord_axis?
        standard_names = {'longitude': 'X', 'grid_longitude': 'X', 'projection_x_coordinate': 'X',
                          'latitude': 'Y', 'grid_latitude': 'Y', 'projection_y_coordinate': 'Y',
                          'altitude': 'Z', 'time': 'T'}
        if isinstance(coord, iris.coords.Coord):
            guessed_axis = iris.util.guess_coord_axis(coord)
        else:
            guessed_axis = standard_names.get(coord.standard_name.lower())
        return guessed_axis

    @staticmethod
    def _convert_datetime_to_coord_unit(coord, dt):
        if isinstance(coord, iris.coords.Coord):
            # The unit class is then iris.unit.Unit.
            iris_unit = coord.units
        else:
            iris_unit = iris.unit.Unit(coord.units)
        return iris_unit.date2num(dt)
