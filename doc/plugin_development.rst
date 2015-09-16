
===========================
How can I read my own data?
===========================

Introduction
============

One of the key strengths of CIS is the ability for users to create their
own plugins to read data which CIS doesn't currently support. These
plugins can then be shared with the community to allow other users
access to that data. Although the plugins are written in Python this
tutorial assumes no experience in Python. Some programming experience is
however assumed.

.. note::

    Any technical details that may be useful to experienced Python
    programmers will be highlighted in this style - they aren’t necessary
    for completing the tutorial.

Here we describe the process of creating and sharing a plugin. A CIS
plugin is simply a python (.py) file with a set of methods (or
functions) to describe how the plugin should behave.

.. note::

    The methods for each plugin are described within a Class, this gives the
    plugin a name and allows CIS to ensure that all of the necessary methods
    have been implemented.

There are a few methods that the plugin must contain, and some which are
optional. A skeleton plugin would look like this::

    class MyProd(AProduct):
        def get_file_signature(self):
        # Code goes here

        def create_coords(self, filenames):
            ...

        def create_data_object(self, filenames, variable):
            ...

Note that in python whitespace matters! When filling in the above
methods the code for the method should be indented from the signature by
four spaces like this::

    Class MyProd(AProduct):

        def get_file_signature(self):
            # Code goes here
            foo = bar

Note also that the name of the plugin (MyProd) in this case should be
changed to describe the data which it will read. (Don’t change the
AProduct part though – this is important for telling CIS that this is a
plugin for reading data.)

.. note::

    The plugin class subclasses :class:`.AProduct` which is the abstract class which
    defines the methods that the plugin needs to override. It also includes
    a few helper functions for error catching.

    When CIS looks for data plugins it searches for all classes which sub-class
    :class:`.AProduct`. There are also plugins available for collocation with their own abstract base classes,
    so that users can store multiple plugin types in the same plugin directory.

In order to turn the above skeleton into a working plugin we need to
fill in each of the methods with the some code, which turns our data
into something CIS will understand. Often it is easiest to start from an
existing plugin that reads closely matching data. For example creating a
plugin to read some other CCI data would probably be easiest to start
from the Cloud or Aerosol CCI plugins. We have created three different
tutorials to walk you through the creation of some of the existing
plugins to try and illustrate the process. The :ref:`easy` tutorial walks
through the creation of a basic plugin, the :ref:`medium` tutorial builds on
that by creating a plugin which has a bit more detail, and finally the
:ref:`advanced` plugin talks through some of the main considerations when
creating a large and complicated plugin.

A more general template plugin is included `here <https://github.com/cedadev/cis/blob/master/doc/plugin/myprod.py>`__
in case no existing plugin matches your need. We have also created a
short reference describing the purpose of each method the plugins
implement :ref:`here <plugin_content>`.

.. note::

    Plugins aren’t the only way you can contribute though. CIS is an open
    source project hosted on `GitHub <https://github.com/cedadev/cis>`__, so please feel free to submit
    pull-requests for new features or bug-fixes – just check with the
    community first so that we’re not duplicating our effort.

Using and testing your plugin
-----------------------------

It is important that CIS knows where to look to find your new plugin,
and this is easily done by setting the environment variable
CIS_PLUGIN_HOME to point to the directory within which your plugin is
stored.

Once you have done this CIS will automatically use your plugin for
reading any files which match the file signature you used.

If you have any issues with this (because for example the file signature
clashes with a built-in plugin) you can tell CIS to use your plugin when
reading data by simply specifying it after the variable and filename in
most CIS commands, e.g.::

    cis subset a_variable:filename.nc:product=MyProd ...

Sharing your plugin
-------------------

This is the easy bit! Once you’re happy that your plugin can fairly
reliably read a currently unsupported dataset you should share it with
the community. Use the upload form `here <http://cistools.net/add-plugin>`__ to submit your plugin to the
community.

We moderate the plugins we receive to ensure the plugins received are
appropriate and meet a minimum level of quality. We’re not expecting the
plugins to necessarily be production quality code but we do expect them
to work for the subset of data they claim to. Having said that, if we
feel a plugin provides really a valuable capability and is of high
quality we may incorporate that plugin into the core CIS data readers –
with credit to the author of course!

Tutorials
=========

.. toctree::
    easy_plugin_tutorial
    medium_plugin_tutorial
    advanced_plugin_tutorial

.. _plugin_content:

Data plugin reference
=====================

This section provides a reference describing the expected behaviour of
each of the functions a plugin can implement. The following methods are mandatory:

.. automethod:: cis.data_io.products.AProduct.AProduct.get_file_signature
    :noindex:

.. automethod:: cis.data_io.products.AProduct.AProduct.create_coords
    :noindex:

.. automethod:: cis.data_io.products.AProduct.AProduct.create_data_object
    :noindex:


While these may be implemented optionally:

.. automethod:: cis.data_io.products.AProduct.AProduct.get_variable_names
    :noindex:

.. automethod:: cis.data_io.products.AProduct.AProduct.get_file_type_error
    :noindex:

.. automethod:: cis.data_io.products.AProduct.AProduct.get_file_format
    :noindex:

