=============================
CIS as a Python library (API)
=============================

.. todo:: Add some examples here

Main API
========

As a commmand line tool, CIS has not been designed with a python API in mind. There are however some utility functions
that may provide a useful start for those who wish to use CIS as a python library. For example, the functions in the
base cis module provide a straightforward way to load your data. They can be easily import using, for example: :code:`from cis import read_data`.
One of the advantages of using CIS as a Python library is that you are able to perform multiple operations in one go,
that is without writing to disk in between. In certain cases this may provide a significant speed-up.

.. note::
    This section of the documentation expects a greater level of Python experience than the other sections. There
    are many helpful Python guides and tutorials available around the web if you wish to learn more.

The :func:`read_data` function is a simple way to read a single gridded or ungridded data object (e.g. a NetCDF
variable) from one or more files. CIS will determine the best way to interperet the datafile by comparing the file
signature with the built-in data reading plugins and any user defined plugins. Specifying a particular ``product``
allows the user to override this automatic detection.

.. autofunction:: cis.read_data

The :func:`read_data_list` function is very similar to :func:`read_data` except that it allows the user to specify
more than one variable name. This function returns a list of data objects, either all of which will be gridded, or all
ungridded, but not a mix. For ungridded data lists it is assumed that all objects share the same coordinates.

.. autofunction:: cis.read_data_list


Data Objects
------------

Each of the above methods return either :class:`~GriddedData` or :class:`~UngriddedData` objects. These objects are the main
data handling objects used within CIS, and although they share a common interface (defined by the :class:`CommonData`
class) there are some differences. The methods on each of these types are documented in the
:doc:`data modules <cis.data_io_objects>` section. The most useful methods on these objects are probably
:attr:`summary()` and :attr:`save()`.

Unsupported API
===============

.. warning::
    While the above interfaces are designed as a 'public' API and unlikely to change over CIS versions, those documented
    below are not yet standardised and may change or be removed even between minor version revisions. It is expected
    however that these particular classes will be developed and stabilised over time to form part of the 'public' API.

Collocation
-----------
The main collocation class can be imported using :code:`from cis.collocation import Collocate`, it's methods are outlined below:

.. autoclass:: cis.collocation.Collocate
   :special-members:


Aggregation
-----------
The main collocation class can be imported using :code:`from cis.aggregation import Aggregate`, it's methods are outlined below.
Note that currently this object saves the output directly to file, but it is expected that in the future it will return
the result for the user to output as needed.

.. autoclass:: cis.aggregation.Aggregate
   :special-members:


Subsetting
----------
The main collocation class can be imported using :code:`from cis.subsetting import Subset`, it's methods are outlined below:
Note that currently this object saves the output directly to file, but it is expected that in the future it will return
the result for the user to output as needed.

.. autoclass:: cis.subsetting.Subset
   :special-members:


.. todo:: Fix the plotting interface
.. Plotting
   --------
   The main collocation class can be imported using :code:`from cis.plotting import Plotter`, it's methods are outlined below:
   .. automethod:: cis.plotting.Plotter.__init__


Stats
-----
The main collocation class can be imported using :code:`from cis.stats import StatsAnalyzer`, it's methods are outlined below:

.. autoclass:: cis.stats.StatsAnalyzer
    :noindex:
    :special-members:
    :member-order: bysource


Full Python reference documentation
-----------------------------------
The rest of the documentation below documents internal CIS functions and modules which are not intended to be used as an
API at all. They are documented here as a reference for developers and other interested parties.

.. toctree::

    cis.data_io
    cis.aggregation
    cis.collocation
    cis.plotting
    cis.subsetting
    cis_stats
    cis_utils
    cis_exceptions

