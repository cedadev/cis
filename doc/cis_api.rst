=============================
CIS as a Python library (API)
=============================


Main API
========

As a command line tool, CIS has not been designed with a python API in mind. There are however some utility functions
that may provide a useful start for those who wish to use CIS as a python library. For example, the functions in the
base cis module provide a straightforward way to load your data. They can be easily import using, for example: :code:`from cis import read_data`.
One of the advantages of using CIS as a Python library is that you are able to perform multiple operations in one go,
that is without writing to disk in between. In certain cases this may provide a significant speed-up.

.. note::
    This section of the documentation expects a greater level of Python experience than the other sections. There
    are many helpful Python guides and tutorials available around the web if you wish to learn more.

The :func:`read_data` function is a simple way to read a single gridded or ungridded data object (e.g. a NetCDF
variable) from one or more files. CIS will determine the best way to interpret the datafile by comparing the file
signature with the built-in data reading plugins and any user defined plugins. Specifying a particular ``product``
allows the user to override this automatic detection.

.. autofunction:: cis.read_data

The :func:`read_data_list` function is very similar to :func:`read_data` except that it allows the user to specify
more than one variable name. This function returns a list of data objects, either all of which will be gridded, or all
ungridded, but not a mix. For ungridded data lists it is assumed that all objects share the same coordinates.

.. autofunction:: cis.read_data_list

The :func:`get_variables` function returns a list of variable names from one or more specified files. This can be useful
to inspect a set of files before calling the read routines described above.

.. autofunction:: cis.get_variables


Data Objects
------------

Each of the above methods return either :class:`~GriddedData` or :class:`~UngriddedData` objects. These objects are the main
data handling objects used within CIS, and their main methods are discussed in the following section. These classes
share a common interface, defined by the :class:`CommonData` class, which is detailed below. For technical reasons some
methods which are common to both :class:`~GriddedData` and :class:`~UngriddedData` are not defined in the
:class:`CommonData` interface. The most useful of these methods are probably :meth:`summary` and :meth:`save_data`.

These objects can also be 'sliced' analogously to the underlying numpy arrays, and will return a *copy* of the requested
data as a new :class:`CommonData` object with the correct data, coordinates and metadata.

.. autoclass:: cis.data_io.common_data.CommonData
    :noindex:
    :inherited-members:

Pandas
------
All :class:`CommonData` objects can be converted to `Pandas <http://pandas.pydata.org>`_ DataFrames using the
:meth:`as_data_frame` methods. This provides an easy interface to the powerful statistical tools available in Pandas.


Analysis Methods
================

Collocation
-----------
Each data object provides both :meth:`collocated_onto` and :meth:`sampled_from` methods, which are different ways of
calling the collocation depending on whether the object being called is the source or the sample. For example the
function performed by the command line::

  $ cis col Temperature:2010.nc 2009.nc:variable=Temperature

can be performed in Python using::

    temperature_2010 = cis.read_data('Temperature', '2010.nc')
    temperature_2009 = cis.read_data('Temperature', '2009.nc')
    temperature_2010.sampled_from(temperature_2009)


or, equivalently::

    temperature_2009.collocated_onto(temperature_2010)

Aggregation
-----------
:class:`~UngriddedData` objects provide the :meth:`aggregate` method to allow easy aggregation. Each dimension of the
desired grid is specified as a keyword and the start, end and step as the argument (as a tuple, list or slice).

For example::

    data.aggregate(x=[-180, 180, 360], y=slice(-90, 90, 10))

or::

    data.aggregate(how='mean', t=[PartialDateTime(2008,9), timedelta(days=1))

Datetime objects can be used to specify upper and lower datetime limits, or a
single PartialDateTime object can be used to specify a datetime range. The gridstep can be specified as a
DateTimeDelta object.

The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
axis and var_name.

:class:`~GriddedData` objects provide the :meth:`collapsed` method which shadows the Iris method of the same name. Our
implementation is a slight extension of the Iris method which allows partial collapsing of multi-dimensional auxilliary
coordinates.

Subsetting
----------
All objects have a :meth:`subset` method for easily subsetting data across arbitrary dimensions. Constraints on
arbitrary coordinates are specified using keyword arguments. Each constraint must have two entries (a maximum and a
minimum) although one of these can be None. Datetime objects can be used to specify upper and lower datetime limits, or
a single PartialDateTime object can be used to specify a datetime range.

The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
axis and var_name.

For example::

    data.subset(time=[datetime.datetime(1984, 8, 28), datetime.datetime(1984, 8, 29)],
                altitude=[45.0, 75.0])

will subset the data from the start of the 28th of August 1984, to the end of the 29th, and between altitudes of
45 and 75 (in whatever units ares used for that Coordinate).

And::

    data.subset(time=[PartialDateTime(1984, 9)])

will subset the data to all of September 1984.


Plotting
--------
Plotting can also easily be performed on these objects. Many options are available depending on the plot type, but CIS
will attempt to make a sensible default plot regardless of the datatype or dimensionality. The default method for
series data is 'line', otherwise (for e.g. a map plot) is 'scatter2d' for UngriddedData and 'heatmap' for GriddedData.

A matplotlib Axes is created if none is provided, meaning the user is able to reformat, or export the plot however they
like.
