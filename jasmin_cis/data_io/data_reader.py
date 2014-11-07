from jasmin_cis.data_io.ungridded_data import UngriddedDataList


class DataReader(object):
    """
    High level class for reading data from a file
    """

    def read_data(self, filenames, variables, product=None):
        """
        Read a specific variable from a list of files
        Files can be either gridded or ungridded but not a mix of both.
        First tries to read data as gridded, if that fails, tries as ungridded.
        :param filenames:   The filenames of the files to read
        :param variables:    The variables to read from the files
        :return:  The specified data with unnecessary dimensions removed (or a list if multiple variables)
        """
        from jasmin_cis.data_io.products.AProduct import get_data

        # if filenames or variables are not lists, make them lists of 1 element
        if not isinstance(filenames, list):
            filenames = [filenames]
        if not isinstance(variables, list):
            variables = [variables]
        datalist = UngriddedDataList()
        for variable in variables:
            datalist.append(get_data(filenames, variable, product))
        if len(datalist) == 1:
            return datalist[0]
        return datalist

    def read_coordinates(self, filenames, product=None):
        """
        Read the coordinates from a file
        :param filenames:   The filename of the files to read
        :return: A CoordList object
        """
        from jasmin_cis.data_io.products.AProduct import get_coordinates

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames, list):
            filenames = [filenames]

        return get_coordinates(filenames, product)