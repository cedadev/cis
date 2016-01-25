"""
CIS is an open source command-line tool for easy collocation, visualization, analysis, and
comparison of diverse gridded and ungridded datasets used in the atmospheric sciences.

.. note ::

    The CIS documentation has detailed usage information, including a :doc:`user guide <../index>`
    for new users.

As a commmand line tool, CIS has not been designed with a python API in mind. There are however some utility functions
that may provide a useful start for those who wish to use CIS as a python library. The functions in this module provide
the main way to load your data. They can be easily import using, for example: `from cis import read_data`.

The :func:`read_data` function is a simple way to read a single gridded or ungridded data object (e.g. a NetCDF
variable) from one or more files. CIS will determine the best way to interperet the datafile by comparing the file
signature with the built-in data reading plugins and any user defined plugins. Specifying a particular ``product``
allows the user to override this automatic detection.

The :func:`read_data_list` function is very similar to :func:`read_data` except that it allows the user to specify
more than one variable name. This function returns a list of data objects, either all of which will be gridded, or all
ungridded, but not a mix. For ungridded data lists it is assumed that all objects share the same coordinates.
"""
__author__ = "David Michel, Daniel Wallis, Duncan Watson-Parris, Richard Wilkinson, Ian Bush, Matt Kendall, John Holt"
__version__ = "1.3.2"
__status__ = "Stable"
__website__ = "http://www.cistools.net/"

__all__ = ['read_data', 'read_data_list']


def read_data(filenames, variable, product=None):
    """
    Read a specific variable from a list of files
    Files can be either gridded or ungridded but not a mix of both.
    First tries to read data as gridded, if that fails, tries as ungridded.

    :param filenames:   The filenames of the files to read. This can be either a single filename as a string, a comma
     separated list, or a :class:`list` of string filenames. Filenames can include directories which will be expanded to
     include all files in that directory, or wildcards such as ``*`` or ``?``.
    :type filenames: string or list
    :param str variable: The variable to read from the files
    :param str product:  The name of the data reading plugin to use to read the data (e.g. ``Cloud_CCI``).
    :return:  The specified data as either a :class:`GriddedData` or :class:`UngriddedData` object.
    """
    data_list = read_data_list(filenames, variable, product)
    if len(data_list) > 1:
        raise ValueError("More than one {} variable found".format(variable))
    return data_list[0]


def read_data_list(filenames, variables, product=None, aliases=None):
    """
    Read multiple data objects from a list of files. Files can be either gridded or ungridded but not a mix of both.

    :param filenames:   The filenames of the files to read. This can be either a single filename as a string, a comma
     separated list, or a :class:`list` of string filenames. Filenames can include directories which will be expanded to
     include all files in that directory, or wildcards such as ``*`` or ``?``.
    :type filenames: string or list
    :param variables: One or more variables to read from the files
    :type variables: string or list
    :param str product: The name of the data reading plugin to use to read the data (e.g. ``Cloud_CCI``).
    :param aliases: List of aliases to put on each variable's data object as an alternative means of identifying them.
    :type aliases: string or list
    :return:  A list of the data read out (either a :class:`GriddedDataList` or :class:`UngriddedDataList` depending on
     the type of data contained in the files)
    """
    from cis.data_io.data_reader import DataReader, expand_filelist
    try:
        file_set = expand_filelist(filenames)
    except ValueError as e:
        raise IOError(e)
    if len(file_set) == 0:
        raise IOError("No files found which match: {}".format(filenames))
    return DataReader().read_data_list(expand_filelist(filenames), variables, product, aliases)
