"""
CIS is an open source command-line tool and Python library for easy collocation, visualization, analysis, and
comparison of diverse gridded and ungridded datasets used in the atmospheric sciences.

.. note ::

    The CIS documentation has detailed usage information, including a :doc:`user guide <../index>`
    for new users.

The :func:`read_data` function is a simple way to read a single gridded or ungridded data object (e.g. a NetCDF
variable) from one or more files. CIS will determine the best way to interpret the datafile by comparing the file
signature with the built-in data reading plugins and any user defined plugins. Specifying a particular ``product``
allows the user to override this automatic detection.

The :func:`read_data_list` function is very similar to :func:`read_data` except that it allows the user to specify
more than one variable name. This function returns a list of data objects, either all of which will be gridded, or all
ungridded, but not a mix. For ungridded data lists it is assumed that all objects share the same coordinates.
"""
__author__ = "David Michel, Daniel Wallis, Duncan Watson-Parris, Richard Wilkinson, Ian Bush, Matt Kendall, John Holt"
__version__ = "2.0.0"
__status__ = "Dev"
__website__ = "http://www.cistools.net/"

__all__ = ['read_data', 'read_data_list', 'get_variables', 'cis_readers']


from contextlib import contextmanager


@contextmanager
def cis_readers():
    import iris.fileformats
    from cis.plugin import find_plugin_classes

    #   The e.g. ECHAM plugins which only need a callback can call the iris.fileformats.netcdf.load_cubes(..,
    # callback='') method and pass this through

    # TODO Iris currently can only take one FileElement argument and so only provide one 'constraint' on finding the
    #  right file. Phil agreed that adding this could be done and shouldn't take long. I can add it as an issue at
    # some point if needed

    cis_specs = find_plugin_classes()
    # Register the loader with iris, use extend rather than adding each one at a time
    iris.fileformats.FORMAT_AGENT._format_specs.extend(cis_specs)
    # Sort the agents (which takes priority into account)
    iris.fileformats.FORMAT_AGENT._format_specs.sort()
    yield
    # The spec should have unique keys so remove should be fine
    for spec in cis_specs:
        iris.fileformats.FORMAT_AGENT._format_specs.remove(spec)


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


def read_data_list(filenames, variables=None, product=None):
    """
    Read multiple data objects from a list of files. Files can be either gridded or ungridded but not a mix of both.

    :param filenames:   The filenames of the files to read. This can be either a single filename as a string, a comma
     separated list, or a :class:`list` of string filenames. Filenames can include directories which will be expanded to
     include all files in that directory, or wildcards such as ``*`` or ``?``.
    :type filenames: string or list
    :param variables: One or more variables to read from the files
    :type variables: string or list
    :param str product: The name of the data reading plugin to use to read the data (e.g. ``Cloud_CCI``).
    :return:  A list of the data read out (either a :class:`GriddedDataList` or :class:`UngriddedDataList` depending on
     the type of data contained in the files)
    """
    from cis.data_io.data_reader import expand_filelist
    from iris.fileformats import FORMAT_AGENT
    import iris

    try:
        file_set = expand_filelist(filenames)
    except ValueError as e:
        raise IOError(e)
    if len(file_set) == 0:
        raise IOError("No files found which match: {}".format(filenames))

    if product is not None:
        try:
            file_spec = next(fs for fs in FORMAT_AGENT._format_specs if
                             fs.name == product)
        except StopIteration:
            raise ValueError("Invalid product: {}".format(product))
    else:
        file_spec = iris

    return file_spec.load_cubes(file_set, variables)


def get_variables(filenames, product=None):
    """
    Get a list of variables names from a list of files. Files can be either gridded or ungridded but not a mix of both.

    :param filenames:   The filenames of the files to read. This can be either a single filename as a string, a comma
     separated list, or a :class:`list` of string filenames. Filenames can include directories which will be expanded to
     include all files in that directory, or wildcards such as ``*`` or ``?``.
    :type filenames: string or list
    :param str product: The name of the data reading plugin to use to read the data (e.g. ``Cloud_CCI``).
    :param str type: The type of HDF data to read, i.e. 'VD' or 'SD'
    :return:  A list of the variables
    """
    data_list = read_data_list(filenames, product)
    return [c.name() for c in data_list]

