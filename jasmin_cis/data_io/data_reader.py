import iris

from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.data_io.products.AProduct import get_data, get_coordinates


class DataReader(object):
    """
    High level class to manage reading data from a file
    Principally, manages operations between one or multiple variables, and gridded or un-gridded data.
    """

    def __init__(self, get_data_func=get_data, get_coords_func=get_coordinates):
        """
        Construct a new DataReader object
        :param get_data_func: Function to read data from a file and return a CubeList
        :param get_coords_func:
        :return:
        """
        self._get_data_func = get_data_func
        self._get_coords_func = get_coords_func

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

        if len(variables) == 1:
            return self._get_data_func(filenames, variables[0], product)
        else:
            gridded = None
            data_list = []
            for variable in variables:
                var_data = self._get_data_func(filenames, variable, product)
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