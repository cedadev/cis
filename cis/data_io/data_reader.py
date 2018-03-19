import fnmatch
import logging

from cis.data_io.gridded_data import GriddedDataList
from cis.data_io.ungridded_data import UngriddedDataList
from cis.data_io.products.AProduct import get_data, get_coordinates, get_variables
from cis.utils import listify


def expand_filelist(filelist):
    """
    :param filelist: A single element, or list, or comma seperated string of filenames, wildcarded filenames or
     directories
    :return: A flat list of files which exist - with no duplicates
    :raises ValueError: if any of the files in the list do not exist.
    """
    import os
    import six
    from glob import glob
    from cis.utils import OrderedSet

    if isinstance(filelist, six.string_types):
        input_list = filelist.split(',')
    else:
        input_list = listify(filelist)

    # Ensure we don't get duplicates by making file_set a set
    file_set = OrderedSet()
    for element in input_list:
        if any(wildcard in element for wildcard in ['*', '?', ']', '}']):
            filelist = glob(element)
            filelist.sort()
            for filename in filelist:
                file_set.add(filename)
        elif os.path.isdir(element):
            filelist = os.listdir(element)
            filelist.sort()
            for a_file in filelist:
                full_file = os.path.join(element, a_file)
                if os.path.isfile(full_file):
                    file_set.add(full_file)
        elif os.path.isfile(element):
            file_set.add(element)
        else:
            raise ValueError("{} is not a valid filename".format(element))
    return list(file_set)


class DataReader(object):
    """
    High level class to manage reading data from a file.
    Principally, manages operations between one or multiple variables, and gridded or un-gridded data.
    """

    def __init__(self, get_data_func=get_data, get_coords_func=get_coordinates, get_variables_func=get_variables):
        """
        Construct a new DataReader object

        :param get_data_func: Function to read data from file and return a CommonDataList
        :param get_coords_func: Function to read data from a file and return a CoordList
        :param get_variables_func: Function to read variables from a file and return a list of variable strings
        """
        self._get_data_func = get_data_func
        self._get_coords_func = get_coords_func
        self._get_vars_func = get_variables_func

    def read_data_list(self, filenames, variables, product=None, aliases=None):
        """
        Read multiple data objects. Files can be either gridded or ungridded but not a mix of both.

        :param filenames: One or more filenames of the files to read
        :type filenames: string or list
        :param variables: One or more variables to read from the files
        :type variables: string or list
        :param str product: Name of data product to use (optional)
        :param aliases: List of variable aliases to put on each variables
         data object as an alternative means of identifying them. (Optional)
        :return:  A list of the data read out (either a GriddedDataList or UngriddedDataList depending on the
         type of data contained in the files)
        """
        # if filenames or variables are not lists, make them lists of 1 element
        filenames = listify(filenames)
        variables = listify(variables)
        aliases = listify(aliases) if aliases else None

        variables = self._expand_wildcards(variables, filenames, product)

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

    def _expand_wildcards(self, variables, filenames, product):
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
                    file_variables = self._get_vars_func(filenames, product)
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

         1. All variables in a datagroup are present in all the files in that datagroup
         2. The shape of the data returned from each variable must be the same in each file, so that they may be
            concatenated
         3. They should all be openable by the same CIS data product
         4. They should be dictionaries of the following format::

                 {'filenames': ['filename1.nc', 'filename2.nc'],
                   'variables': ['variable1', 'variable2'],
                   'product' : 'Aerosol_CCI_L2'}

        :return list: A list of CommonData objects (either GriddedData or UngriddedData, *or a combination*)
        """
        data_list = list()
        for datagroup in datagroups:
            data_list.extend(self.read_single_datagroup(datagroup))
        return data_list

    def read_single_datagroup(self, datagroup):
        """
        Read data from a set of datagroups

        :param datagroup: A datagroup: a grouping of files and variables, where the
         set of files may be logically considered to represent the same data (an example would be 2D model data split
         into monthly output files where the grid is the same).
         The following should be true of a datagroup:

         1. All variables in a datagroup are present in all the files in that datagroup
         2. The shape of the data returned from each variable must be the same in each file, so that they may be
            concatenated
         3. They should all be openable by the same CIS data product
         4. They should be dictionaries of the following format::

                 {'filenames': ['filename1.nc', 'filename2.nc'],
                   'variables': ['variable1', 'variable2'],
                   'product' : 'Aerosol_CCI_L2'}

        :return CommonDataList: Either a GriddedDataLise or an UngriddedDataList
        """
        aliases = datagroup.get('aliases', None)
        data = self.read_data_list(datagroup['filenames'], datagroup['variables'],
                                   datagroup.get('product', None), aliases)
        return data

    def read_coordinates(self, filenames, product=None):
        """
        Read the coordinates from a file
        :param filenames:   The filename of the files to read
        :return: A CoordList object
        """

        # if filenames is not a list, make it a list of 1 element
        filenames = listify(filenames)

        return self._get_coords_func(filenames, product)
