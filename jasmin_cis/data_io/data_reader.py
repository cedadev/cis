import fnmatch
import logging
import iris

from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.data_io.products.AProduct import get_data, get_coordinates, get_variables


class DataReader(object):
    """
    High level class to manage reading data from a file
    Principally, manages operations between one or multiple variables, and gridded or un-gridded data.
    """

    def __init__(self, get_data_func=get_data, get_coords_func=get_coordinates, get_variables_func=get_variables):
        """
        Construct a new DataReader object
        :param get_data_func: Function to read data from a file and return a CubeList
        :param get_coords_func:
        :return:
        """
        self._get_data_func = get_data_func
        self._get_coords_func = get_coords_func
        self._get_vars_func = get_variables_func

    def read_data(self, filenames, variables, product=None):
        """
        Read a specific variable from a list of files
        Files can be either gridded or ungridded but not a mix of both.
        First tries to read data as gridded, if that fails, tries as ungridded.
        :param filenames:   The filenames of the files to read
        :param variables:    The variables to read from the files
        :return:  The specified data with unnecessary dimensions removed (or a list if multiple variables)
        """

        # if filenames or variables are not lists, make them lists of 1 element
        if not isinstance(filenames, list):
            filenames = [filenames]
        if not isinstance(variables, list):
            variables = [variables]

        variables = self._expand_wildcards(variables, filenames)

        if len(variables) == 1:
            return self._get_data_func(filenames, variables[0], product)
        else:
            gridded = None
            data_list = []
            for variable in variables:
                var_data = self._get_data_func(filenames, variable, product)
                var_data.filenames = filenames
                var_is_gridded = isinstance(var_data, iris.cube.Cube)
                if gridded is None:
                    gridded = var_is_gridded
                elif not gridded == var_is_gridded:
                        # Data should always be the same type (ungridded vs gridded) but check anyway.
                        raise TypeError("Error reading variables from file: "
                                        "cannot read multiple datasets where some are gridded and some are ungridded")
                data_list.append(var_data)
            if gridded:
                return GriddedDataList(data_list)
            else:
                return UngriddedDataList(data_list)

    def _expand_wildcards(self, variables, filenames):
        """
        Convert any wildcards into actual variable names by inspecting the file
        :param variables: List of variables names, some of which may be wilcards
        :param filenames: Filenames
        :return: List of variable names to use.
        """
        valid_vars = []
        for variable in variables:
            is_wildcard = any(wildcard in variable for wildcard in ['*', '?', ']', '}'])
            file_variables = None
            if is_wildcard:
                if file_variables is None:
                    file_variables = self._get_vars_func(filenames)
                matches = fnmatch.filter(file_variables, variable)
                if len(matches) == 0:
                    logging.warning("No variables matching wildcard '%s' found in file." % variable)
                else:
                    logging.info("Wildcard '%s' found matching variables: %s" % (variable, matches))
                valid_vars.extend(matches)
            else:
                valid_vars.append(variable)
        if len(valid_vars) == 0:
            raise ValueError("No matching variables could be found for the variables supplied")
        return valid_vars

    def read_coordinates(self, filenames, product=None):
        """
        Read the coordinates from a file
        :param filenames:   The filename of the files to read
        :return: A CoordList object
        """

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames, list):
            filenames = [filenames]

        return self._get_coords_func(filenames, product)