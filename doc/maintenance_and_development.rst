===============================
Maintenance and Developer Guide
===============================

Unit test suite
===============

The unit tests suite can be ran using Nose readily. Just go the root of the repository (i.e. cis) and type ``nosetests cis/test/unit`` and this will run the full suite of tests.
A comprehensive set of integration tests are also provided. These require data sets which can be found in the JASMIN CIS group workspace under the ``cis_repo_test_files`` directory. To run the integration tests set the environment variable ``CIS_DATA_HOME`` to the location of the data sets, and then run ``nosetests cis/test/integration``.
There are also a number of plot tests available under the ``test/plot_tests`` directory which can be run using the ``run_all.sh`` script. These perform a diff of some standard plots against reference plots, however small changes in the platform libraries and fonts can break these tests so they shouldn't be relied on.


Dependencies
============

A graph representing the dependency tree can be found at ``doc/cis_dependency.dot`` (use [http://code.google.com/p/jrfonseca/wiki/XDot XDot] to read it)

.. image:: img/dep.png
   :width: 900px


Anaconda Build
==============

The Anaconda build recipes for CIS and the dependencies which can't be found either in the core channel, or in SciTools are stored in their own github repository [https://github.com/cistools/conda-recipes here].
To build a new CIS package clone the conda-recipes repository and then run the following command:
    $ conda build -c cistools -c scitools cis --numpy 1.8

By default this will run the full unit-test suite before successful completion. You can also optionally run the integration test suite by specifying the CIS_DATA_HOME environment variable.

To upload the package to the cistools channel on Anaconda.org use:
    $ binstar upload <package_location> -u cistools


API Documentation
=================

.. todo:: change API documentation engine?

The API reference can be generated using the following command

`` python setup.py gendoc``

This will automatically generates the documentation using [http://epydoc.sourceforge.net/ Epydoc] in html under the directory ''doc/api'' from the [http://epydoc.sourceforge.net/docstrings.html docstrings] in the code.


Plugin development
==================

Users can write their own "plugins" for providing extra functionality for reading and collocation. The main program will look at the environment variable ``CIS_PLUGIN_HOME`` for any classes that subclass the relevant top level class - as described for data products and collocation below.

The simplest way to set this environment variable is to add this to your ``.bashrc`` file::

  $ export CIS_PLUGIN_HOME=/path/to/dir


Data Products
-------------

Users can write their own plugins for reading in different types of data. CIS uses the notion of a 'data product' to encapsulate the information about different types of data. They are concerned with 'understanding' the data and it's coordinates and producing a single self describing data object. 

A data product is a subclass of AProduct and as such must implement the abstract methods:

``get_file_signature(self)``
  Returns a list of regex's to match the product's file naming convention. CIS will use this to decide which data product to
  use for a given file. The first product with a signature that matches the filename will be used. The order in which
  the products are searched is determined by the priority property, highest value first; internal products generally have
  a priority of 10. The product can open the file to determine whether it can read it see ``get_file_type_error``.

``create_coords(self, filenames)``
  Create a Coordinate object from the data files in the ``filenames`` parameter.

``create_data_object(self, filenames, variable)``
  Create and returns an ungridded data object for a given variable from many files. The ``filenames`` parameters is a list of
  filenames for the data. The parameter ``variable`` is the name of the variable to read from the dataset.

and may choose to implement:

``get_variable_names(self, filenames, data_type=None)``
  This return a list of valid variables names from the ``filenames`` list passed in. If not implemented the base function will be used.
  The ``data_type`` parameter can be used to specify extra information.

``get_file_type_error(self, filenames)``
  Check the ``filename`` to see if it is of the correct type and if not return a list of errors. If the return is
  None then there are no error and this is the correct data product to use for this file. This gives a mechanism for a data
  product to identify itself as the correct product to use even if a specific file signature can not be specified. For
  example GASSP is a type of NetCDF file and so filenames end with .nc but so do other NetCDF files, so the data product opens
  the file and looks for the GASSP version attribute, and if it doesn't find it returns a error.

``get_file_format(self, filenames)``
  Returns a file format hierarchy separated by slashes, of the form TopLevelFormat/SubFormat/SubFormat/Version,
  e.g. NetCDF/GASSP/1.0, ASCII/ASCIIHyperpoint, HDF4/CloudSat
  This is used within the ceda di indexing tool. If not set it will default to the products name.

Here is a sketch of a data product implementation::

  class MyProd(AProduct):

      #set the priority to be higher than the other netcdf file types
      priority = 20

      def get_file_signature(self):
          return [r'.*something*', r'.*somethingelse*']
  
      def create_coords(self, filenames):
  
          logging.info("gathering coordinates")
          for filename in filenames:
              data1 = []
              data2 = []
              data3 = []
  
          logging.info("gathering coordinates metadata")
          metadata1 = Metadata()
          metadata2 = Metadata()
          metadata3 = Metadata()
  
          coord1 = Coord(data1,metadata1,'X') # this coordinate will be used as the 'X' axis when plotting
          coord2 = Coord(data2,metadata2,'Y') # this coordinate will be used as the 'Y' axis when plotting
          coord3 = Coord(data3,metadata3)
  
          return CoordList([coord1,coord2,coord3])
  
      def create_data_object(self, filenames, variable):
  
          logging.info("gathering data for variable " + str(variable))
          for filename in filenames:
              data = []
  
          logging.info("gatherings metadata for variable " + str(variable))
          metadata = Metadata()
  
          coords = self.create_coords(filenames)
          return UngriddedData(data,metadata,coords)

      def get_file_type_error(self, filename):

          if not os.path.isfile(filename):
              return ["File does not exist"]

          if not file_has_attribute("file_type", filename):
             return ["File has wrong file type"]

          return None

      def get_variable_names(self, filenames, data_type=None):
          vars = variable_names_from_file
          del vars['Not useful']
          return vars


.. _collocation_design:

Collocation
-----------

Users can write their own plugins for performing the collocation of two data sets.
There are three different types of plugin available for collocation and each will be described briefly below.

Kernel
""""""

A kernel is used to convert the constrained points into values in the output. There are two sorts of kernel one
which act on the final point location and a set of data points (these derive from Kernel) and the more specific kernels
which act upon just an array of data (these derive from AbstractDataOnlyKernel, which in turn derives from Kernel).
The data only kernels are less flexible but should execute faster. To create a new kernel inherit from ``Kernel`` and
implement the abstract method ``get_value(self, point, data)``. To make a data only kernel inherit from AbstractDataOnlyKernel
and implement ``get_value_for_data_only(self, values)`` and optionally overload ``get_value(self, point, data)``.

``get_value(self, point, data)``

  This method should return a single value (if ``Kernel.return_size`` is 1) or a list of n values (if ``Kernel.return_size`` is n)
  based on some calculation on the data given a single point.
  The data is deliberately left unspecified in the interface as it may be any type of data, however it is expected that
  each implementation will only work with a specific type of data (gridded, ungridded etc.) Note that this method will
  be called for every sample point and so could become a bottleneck for calculations, it is advisable to make it as
  quick as is practical. If this method is unable to provide a value (for example if no data points were given)
  a ValueError should be thrown.

``get_value_for_data_only(self, values)``

  This method should return a single value (if ``Kernel.return_size`` is 1) or a list of n values (if ``Kernel.return_size`` is n)
  based on some calculation on the values (a numpy array).
  Note that this method will
  be called for every sample point in which data can be placed and so could become a bottleneck for calculations,
  it is advisable to make it as quick as is practical. If this method is unable to provide a value
  (for example if no data points were given) a ValueError should be thrown. This method will not be called if there is no
  values to be used for calculations.

Constraint
""""""""""

The constraint limits the data points for a given sample point.
The user can also add a new constraint method by subclassing Constraint and providing an implementation for
``constrain_points``. If more control is needed over the iteration sequence then the method
``get_iterator`` can be
overloaded in additional to constrain_points, this may not be respected by all collocators who may still iterate over all
sample data points. To enable a constraint to use a AbstractDataOnlyKernel the method
``get_iterator_for_data_only`` should be implemented (again this may be ignored by a collocator).

``constrain_points(self, ref_point, data)``

 This method should return a subset of the data given a single reference point.
 It is expected that the data returned should be of the same type as that given - but this isn't mandatory. It is
 possible that this function will return zero points, or no data. The collocation class is responsible for providing a
 fill_value.

``get_iterator(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, output_data)``

 The method should return an iterator over the output indices, hyper point for the output and data points for that output
 hyper point. This may not be called by all collocators who may choose to iterate over all sample points instead.
 The arguments are:
 * ``missing_data_for_missing_sample`` if True the iterator should not iterate over any points in the sample points which are missing.
 * ``coord_map`` is a list of tuples of indexes of sample points coords, data coords and output coords
 * ``coords`` are the coords that the data should be mapped on
 * ``data_points`` are the non-masked data points
 * ``shape`` is the final shape of the data
 * ``points`` is the original sample points object
 * ``output_data`` is the output data

``get_iterator_for_data_only(self, missing_data_for_missing_sample, coord_map, coords, data_points, shape, points, values)``

 The method should return an iterator over the output indices and a numpy array of the data values.
 This may not be called by all collocators who may choose to iterate over all sample points instead. The parameters are
 the same as ``get_iterator``.

Collocator
""""""""""

Another plugin which is available is the collocation method itself. A new one can be created by subclassing Collocator and
providing an implementation for ``collocate(self, points, data, constraint, kernel)``. This method takes a number of
points and applies the given constraint and kernel methods on the data for each of those points. It is responsible for
returning the new data object to be written to the output file. As such, the user could create a collocation routine
capable of handling multiple return values from the kernel, and hence creating multiple data objects, by creating a
new collocation method.

Plugins
"""""""

For all of these plugins any new variables, such as limits, constraint values or averaging parameters,
are automatically set as attributes in the relevant object. For example, if the user wanted to write a new
constraint method (``AreaConstraint``, say) which needed a variable called ``area``, this can be accessed with ``self.area``
within the constraint object. This will be set to whatever the user specifies at the command line for that variable, e.g.::

  $ ./cis.py col my_sample_file rain:"model_data_?.nc"::AreaConstraint,area=6000,fill_value=0.0:nn_gridded

Example implementations of new collocation plugins are demonstrated below for each of the plugin types::


  class MyCollocator(Collocator):
  
      def collocate(self, points, data, constraint, kernel):
          values = []
          for point in points:
              con_points = constraint.constrain_points(point, data)
              try:
                  values.append(kernel.get_value(point, con_points))
              except ValueError:
                  values.append(constraint.fill_value)
          new_data = LazyData(values, data.metadata)
          new_data.missing_value = constraint.fill_value
          return new_data


  class MyConstraint(Constraint):
  
      def constrain_points(self, ref_point, data):
          con_points = []
          for point in data:
              if point.value > self.val_check:
                  con_points.append(point)
          return con_points
  
  
  class MyKernel(Kernel):
  
      def get_value(self, point, data):
          nearest_point = point.furthest_point_from()
          for data_point in data:
              if point.compdist(nearest_point, data_point):
                  nearest_point = data_point
          return nearest_point.val
  
