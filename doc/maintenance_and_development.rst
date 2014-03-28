===============================
Maintenance and Developer Guide
===============================

Experimental Branches
=====================

To checkout a particular branch, simply type ``git checkout branchname``

 - 'slice': this branch has a slicing functionality that can be used via the command line argument --slice
 - 'griddedgriddedcolocation': includes functionality for CF-compliant gridded-gridded colocation using the Iris library.

Note that these branches are deemed experimental and therefore not stable (that's why they are in branch and not the in main trunk!), so it comes with no warranty.

Unit test suite
===============

The unit tests suite can be ran using Nose readily. Just go the root of the repository (i.e. jasmin_cis) and type ``nose`` and this will run the full suite of tests.
A comprehensive set of test data sets can be found under the ``test/test_files`` directory. A ``harness`` directory is provided and contains a couple of test harness for those data files.
Finally, integration system-level tests are provided under the ``test/plot_tests`` directory and be ran using the ``run_all.sh`` script.


Dependencies
============

A graph representing the dependency tree can be found at ``doc/cis_dependency.dot`` (use [http://code.google.com/p/jrfonseca/wiki/XDot XDot] to read it)

.. image:: img/dep.png
   :width: 900px


API Documentation
=================

.. todo:: change API documentation engine?

The API reference can be generated using the following command

`` python setup.py gendoc``

This will automatically generates the documentation using [http://epydoc.sourceforge.net/ Epydoc] in html under the directory ''doc/api'' from the [http://epydoc.sourceforge.net/docstrings.html docstrings] in the code.


Plugin development
==================

Users can write their own "plugins" for providing extra functionality for reading and colocation. The main program will look at the environment variable ``CIS_PLUGIN_HOME`` for any classes that subclass the relevant top level class - as described for data products and colocation below.

The simplest way to set this environment variable is to add this to your ``.bashrc`` file::

  $ export CIS_PLUGIN_HOME=/path/to/dir


Data Products
-------------

Users can write their own plugins for reading in different types of data. CIS uses the notion of a 'data product' to encapsulate the information about different types of data. They are concerned with 'understanding' the data and it's coordinates and producing a single self describing data object. 

In order to create a data product one has to write their own subclass of AProduct that implements the abstract methods ``create_data_object(self, filenames, variable)``, ``get_file_signature(self)`` and ``create_coords(self, filenames)``. The ``get_file_signature(self)`` method should just return a list of regular expressions which are used to decided when this data product should be used and the others are self explanatory. Here is an example of what such implementation could look like::

  class MyProd(AProduct):
  
      def get_file_signature(self):
          return [r'.*something*']
  
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



Colocation
----------

Users can write their own plugins for performing the colocation of two data sets. There are three different types of plugin available for colocation and each will be described briefly below. 

The user can add a new kernel by writing their own subclass of Kernel that implements the abstract method ``get_value(self, point, data)``. This method should return a single value based on some calculation on the data given a single point. The data is deliberately left unspecified in the interface as it may be any type of data, however it is expected that each implementation will only work with a specific type of data (gridded, ungridded etc.) Note that this method will be called for every sample point and so could become a bottleneck for calculations, it is advisable to make it as quick as is practical. If this method is unable to provide a value (for example if no data points were given) a ValueError should be thrown.

The user can also add a new constraint method by subclassing Constraint and providing an implementation for ``constrain_points(self, ref_point, data)``. This method should return a subset of the data given a single reference point. It is expected that the data returned should be of the same type as that given - but this isn't mandatory. It is possible that this function will return zero points, or no data. The colocation class is responsible for providing a fill_value.

Another plugin which is available is the colocation method itself. A new one can be created by subclassing Colocator and providing an implementation for ``colocate(self, points, data, constraint, kernel)``. This method takes a number of points and applies the given constraint and kernel methods on the data for each of those points. It is responsible for returning the new data object to be written to the output file. As such, the user could create a colocation routine capable of handling multiple return values from the kernel, and hence creating multiple data objects, by creating a new colocation method.

For all of these plugins any new variables, such as limits, constraint values or averaging parameters, are automatically set as attributes in the relevant object. For example, if the user wanted to write a new constraint method (``AreaConstraint``, say) which needed a variable called ``area``, this can be accessed with ``self.area`` within the constraint object. This will be set to whatever the user specifies at the command line for that variable, e.g.::

  $ ./cis.py col my_sample_file rain:"model_data_?.nc"::AreaConstraint,area=6000,fill_value=0.0:nn_gridded

Example implementations of new colocation plugins are demonstrated below for each of the plugin types::


  class MyColocator(Colocator):
  
      def colocate(self, points, data, constraint, kernel):
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
  
