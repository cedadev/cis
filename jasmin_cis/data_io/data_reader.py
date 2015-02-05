import fnmatch
import logging

from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.data_io.products.AProduct import get_data, get_coordinates, get_variables
from jasmin_cis.utils import deprecated, listify


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

    @deprecated
    def read_data(self, filenames, variables, product=None):
        """
        Read a specific variable from a list of files
        Files can be either gridded or ungridded but not a mix of both.
        First tries to read data as gridded, if that fails, tries as ungridded.
        :param filenames:   The filenames of the files to read
        :param variables:    The variables to read from the files
        :return:  The specified data with unnecessary dimensions removed (or a list if multiple variables)
        """
        data_list = self.read_data_list(filenames, variables, product)
        if len(data_list) == 1:
            return data_list[0]
        return data_list

    def read_data_list(self, filenames, variables, product=None, aliases=None):
        """
        Read multiple data objects
        Files can be either gridded or ungridded but not a mix of both.
        :param filenames: The filenames of the files to read
        :param variables: The variables to read from the files
        :param product: Name of data product to use
        :param aliases: List of variable aliases to put on each variables
        data object as an alternative means of identifying them.
        :return:  A list of the data read out (either a GriddedDataList or UngriddedDataList depending on the
        type of data contained in the files
        """
        # if filenames or variables are not lists, make them lists of 1 element
        filenames = listify(filenames)
        variables = listify(variables)

        variables = self._expand_wildcards(variables, filenames)

        data_list = None
        for idx, variable in enumerate(variables):
            var_data = self._get_data_func(filenames, variable, product)
            var_data.filenames = filenames
            if aliases:
                try:
                    var_data.alias = aliases[idx]
                except IndexError:
                    raise ValueError("Number of aliases does not match number of variables")
            if data_list is None:
                data_list = GriddedDataList() if var_data.is_gridded else UngriddedDataList()
            data_list.append(var_data)
        assert data_list is not None
        return data_list

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

    def read_datagroups(self, datagroups):
        """
        Read data from a set of datagroups
        :param datagroups: A list of datagroups. Each datagroup represents a grouping of files and variables, where the
        set of files may be logically considered to represent the same data (an example would be 2D model data split
        into monthly output files where the grid is the same).
        The following should be true of a datagroup:
        1) All variables in a datagroup are present in all the files in that datagroup
        2) The shape of the data returned from each variable must be the same in each file, so that they may be
        concatenated
        3) They should all be openable by the same CIS data product
        4) They should be dictionaries of the following format:
         { 'filenames': ['filename1.nc', 'filename2.nc'],
            'variables': ['variable1', 'variable2'],
            'product' : 'Aerosol_CCI'
         }

        :return: A list of data (either a GriddedDataList or an UngriddedDataList, depending on the data format)
        """
        data_list = None
        for datagroup in datagroups:
            aliases = datagroup.get('aliases', None)
            data = self.read_data_list(datagroup['filenames'], datagroup['variables'],
                                       datagroup['product'], aliases)
            if data_list is None:
                # This ensures the list is the right type (i.e. GriddedDataList or UngriddedDataList)
                data_list = data
            else:
                data_list.extend(data)
        return data_list

    def read_coordinates(self, filenames, product=None):
        """
        Read the coordinates from a file
        :param filenames:   The filename of the files to read
        :return: A CoordList object
        """

        # if filenames is not a list, make it a list of 1 element
        filenames = listify(filenames)

        return self._get_coords_func(filenames, product)