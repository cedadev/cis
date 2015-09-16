===========================
Analysis plugin development
===========================

Users can write their own plugins for performing the collocation of two data sets.
There are three different types of plugin available for collocation, first we will describe the overall design and how
these different components interact, then each will be described in more detail.

Basic collocation design
========================

The diagram below demonstrates the basic design of the collocation system, and the roles of each of the components.
In the simple case of the default collocator (which returns only one value) the :ref:`Collocator <collocator_description>`
loops over each of the sample points, calls the relevant :ref:`Constraint <constraint_description>` to reduce the
number of data points, and then the :ref:`Kernel <kernel_description>` which returns a single value, which the
collocator stores.

.. image:: img/CollocationDiagram.png
   :width: 600px

.. _kernel_description:

Kernel
======

A kernel is used to convert the constrained points into values in the output. There are two sorts of kernel one
which act on the final point location and a set of data points (these derive from :class:`.Kernel`) and the more specific kernels
which act upon just an array of data (these derive from :class:`.AbstractDataOnlyKernel`, which in turn derives from :class:`.Kernel`).
The data only kernels are less flexible but should execute faster. To create a new kernel inherit from :class:`.Kernel` and
implement the abstract method :meth:`.Kernel.get_value`. To make a data only kernel inherit from :class:`.AbstractDataOnlyKernel`
and implement :meth:`.AbstractDataOnlyKernel.get_value_for_data_only` and optionally overload :meth:`.AbstractDataOnlyKernel.get_value`.
These methods are outlined below.

.. automethod:: cis.collocation.col_framework.Kernel.get_value
    :noindex:

.. automethod:: cis.collocation.col_framework.AbstractDataOnlyKernel.get_value_for_data_only
    :noindex:

.. _constraint_description:

Constraint
==========

The constraint limits the data points for a given sample point.
The user can also add a new constraint mechanism by subclassing :class:`.Constraint` and providing an implementation for
:meth:`.Constraint.constrain_points`. If more control is needed over the iteration sequence then the
:meth:`.Constraint.get_iterator` method can also be
overloaded. Note however that this may not be respected by all collocators, who may still iterate over all
sample data points. It is possible to write your own collocator (or extend an existing one) to ensure the correct
iterator is used - see the next section. Both these methods, and their signatures, are outlined below.

.. automethod:: cis.collocation.col_framework.Constraint.constrain_points
    :noindex:

.. automethod:: cis.collocation.col_framework.Constraint.get_iterator
    :noindex:

To enable a constraint to use a :class:`.AbstractDataOnlyKernel`, the method
:meth:`get_iterator_for_data_only` should be implemented (again though, this may be ignored by a collocator). An
example of this is the :meth:`.BinnedCubeCellOnlyConstraint.get_iterator_for_data_only` implementation.

.. _collocator_description:

Collocator
==========

Another plugin which is available is the collocation method itself. A new one can be created by subclassing :class:`.Collocator` and
providing an implementation for :meth:`.Collocator.collocate`. This method takes a number of sample
points and applies the given constraint and kernel methods on the data for each of those points. It is responsible for
returning the new data object to be written to the output file. As such, the user could create a collocation routine
capable of handling multiple return values from the kernel, and hence creating multiple data objects, by creating a
new collocation method.

.. note::

    The collocator is also responsible for dealing with any missing values in sample points. (Some sets of sample points may
    include values which may or may not be masked.) Sometimes the user may wish to mask the output for such points, the
    :attr:`missing_data_for_missing_sample` attribute is used to determine the expected behaviour.

The interface is detailed here:

.. automethod:: cis.collocation.col_framework.Collocator.collocate
    :noindex:

Implementation
==============

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

