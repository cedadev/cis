import logging
import sys

from iris import cube
from iris.exceptions import IrisError
import iris.util

import jasmin_cis.exceptions as ex
import jasmin_cis.parse_datetime as parse_datetime
from jasmin_cis.data_io.read import read_data
from jasmin_cis.subsetting.subset_constraint import SubsetConstraint
import jasmin_cis.time_util as time_util
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

        # Perform subsetting.
        if isinstance(data, cube.Cube):
            # Gridded data
            self._subset_gridded(data)
        else:
            raise Exception("Subsetting of ungridded data is not supported")

    def _subset_gridded(self, data):
        # Create constraint.
        sc = SubsetConstraint()
        limit_metadata = []
        for coord in data.coords():
            # Match user-specified limits with dimensions found in data.
            limit_dim = None
            guessed_axis = iris.util.guess_coord_axis(coord)
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
                    limit_start = time_util.convert_datetime_to_std_time(dt)
                    dt = parse_datetime.convert_datetime_components_to_datetime(limit.end, False)
                    limit_end = time_util.convert_datetime_to_std_time(dt)
                else:
                    # Assume to be a non-time axis.
                    limit_start = float(limit.start)
                    limit_end = float(limit.end)
                sc.set_limit(limit_dim, limit_start, limit_end)
                logging.info("Setting limit for dimension '%s' [%s, %s]",
                             limit_dim, str(limit_start), str(limit_end))
                limit_metadata.append("{}: [{}, {}]".format(limit_dim, str(limit_start), str(limit_end)))

        # Apply constraint to data.
        constraint = sc.make_iris_constraint()
        subset = data.extract(constraint)

        if subset is None:
            # Constraints exclude all data.
            raise ex.NoDataInSubsetError("Constraints exclude all data")
        else:
            history = "Subsetted using CIS version " + __version__ + \
                      "\nvariable: " + str(self._variable) + \
                      "\nfrom files: " + str(self._filenames) + \
                      "\nusing limits: " + ', '.join(limit_metadata)
            subset.add_history(history)

            iris.save(subset, self._output_file)
