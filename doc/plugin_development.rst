How can I read my own data?
===========================

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
the community Use the upload form `here <http://cistools.net/add-plugin>`__ to submit your plugin to the
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

.. _easy:

Easy
----

A simple plugin to start with is the plugin for reading native ungridded
CIS data.

One of the first things to consider is which type of file our plugin is
going to be aimed at reading. It is advisable to not make the definition
too broad, it’s easy to have multiple plugins so don’t try and over
complicate the plugin by having it read many different types of file.
Roughly, one plugin should describe a set of data with the same
metadata.

Since the CIS plugin is designed to read any data which CIS produces,
the signature matches any file which starts with `cis-` and ends with
`.nc`::

    def get_file_signature(self):
        return [r'cis\\-.\*\\.nc']

This uses a wildcard string to tell CIS which files do and don’t match
for our product.

.. note::

    For an introduction to regular expressions see, for example,
    https://docs.python.org/2/howto/regex.html

The next step is to complete the :meth:`.AProduct.create_coords` method. CIS uses this
method to create a set of coordinates from the data, so it needs to
return any appropriate coordinates in the shape that CIS expects it.

There are a number of low-level data reading routines within CIS that
can help you read in your data. For the CIS plugin (which is reading
netCDF data) we use two methods from the :mod:`cis.data_io.netcdf`
module: :meth:`read_many_files_individually <cis.data_io.netcdf.read_many_files_individually>` and
:meth:`get_metadata <cis.data_io.netcdf.get_metadata>`. We also
import the :class:`.Coord` data type, which is where we store the coordinates that
we’ve read, and :class:`.UngriddedCoordinates` - which is what we return to CIS.

.. note::

    In python it’s very easy to import classes and methods from other
    modules within your package, and across packages using the from and
    import commands. The file-reading routines used here are used by many of
    the other data products. See the :doc:`API <api/cis>` section for further
    details about using CIS as a python library.

Don’t worry too much about what these methods do at this stage, just use
the import lines below and you should be fine.

::

    def create_coords(self, filenames, usr_variable=None):
        from cis.data_io.netcdf import read_many_files_individually, get_metadata
        from cis.data_io.Coord import Coord, CoordList
        from cis.data_io.ungridded_data import UngriddedCoordinates

Next, we create a list of netCDF variable names which we know are stored
in our file and send that to the file reading routine::

    var_data = read_many_files_individually(filenames, ["longitude","latitude", "time"])

Then we create a :class:`.CoordList` to store our coordinates in, a :class:`.Coord` for each
of those coordinate variables, and then just give them a short label for
plotting purposes (x,y,z etc) – it is strongly advisable that you use
the standard definitions used below for your axis definitions (and use z
for altitude and p for pressure).

::

    coords = CoordList()
    coords.append(Coord(var_data[“longitude”,get_metadata(var_data[“longitude”][0]),axis=”x”))
    coords.append(Coord(var_data[“latitude”,get_metadata(var_data[“latitude”][0]),axis=”y”))
    coords.append(Coord(var_data[“time”,get_metadata(var_data[“time”][0]),axis=”t”))

That’s it, now we can return those coordinates in a way that CIS will
understand::

    return UngriddedCoordinates(coords)

The last method we have to write is the :meth:`.AProduct.create_data_object` method,
which is used by CIS to pull together the coordinates and a particular
data variable into an :class:`.UngriddedData` object. It’s even simpler than the
previous method. We can use the same :meth:`read_many_files_individually <cis.data_io.netcdf.read_many_files_individually>`
method as we did before, and this time pass it the variable the user has
asked for::

    def create_data_object(self, filenames, variable):
        from cis.data_io.ungridded_data import UngriddedData
        usr_var_data = read_many_files_individually(filenames,variable)[variable]

Then we create the coordinates using the :meth:`create_coords` method we’ve
just written::

    coords = self.create_coords(filename)

And finally we return the ungridded data, this combines the coordinates
from the file and the variable requested by the user::

    return UngriddedData(usr_var_data, get_metadata(usr_var_data[0]),coords)

Bringing it all together, tidying it up a bit and including some error
catching gives us::

    import logging
    from cis.data_io.products.AProduct import AProduct
    from cis.data_io.netcdf import read_many_files_individually, get_metadata

    class cis(AProduct):

         def get_file_signature(self):
             return [r'cis\-.*\.nc']

         def create_coords(self, filenames, usr_variable=None):
             from cis.data_io.Coord import Coord, CoordList
             from cis.data_io.ungridded_data import UngriddedCoordinates
             from cis.exceptions import InvalidVariableError

             variables = [("longitude", "x"), ("latitude", "y"), ("altitude", "z"), ("time", "t"), ("air_pressure", "p")]

             logging.info("Listing coordinates: " + str(variables))

             coords = CoordList()
             for variable in variables:
                 try:
                     var_data = read_many_files_individually(filenames,variable[0])[variable[0]]
                     coords.append(Coord(var_data, get_metadata(var_data[0]),axis=variable[1]))
                 except InvalidVariableError:
                     pass

             return UngriddedCoordinates(coords)

         def create_data_object(self, filenames, variable):
             from cis.data_io.ungridded_data import UngriddedData
             usr_var_data = read_many_files_individually(filenames,variable)[variable]
             coords = self.create_coords(filename)
             return UngriddedData(usr_var_data, get_metadata(usr_var_data[0]), coords)


.. _medium:

Medium
------

For this example we will look at the Aeronet data reading plugin.
Aeronet is a ground based sun-photometer network that produces
time-series data for each groundstation in a csv based text file. There
is some information about the ground station in the header of the file,
and then a table of data with a time column, and a column for each of
the measured values.

The :meth:`.AProduct.get_file_signature` method is straightforward, so we first consider
the :meth:`.AProduct.create_coords` method. Here we have actually shifted all of the work
to a private method called :meth:`_create_coord_list`, for reasons which we
will explain shortly::

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

.. note::

    In python there is not really such a thing as a 'private’ method as
    there is in Java and C#, but we can signify that a method shouldn’t be
    accessed externally by starting its name with one or two underscores.

In this method we import an Aeronet data reading routine::

    def _create_coord_list(self, filenames, data=None):
        from cis.data_io.ungridded_data import Metadata
        from cis.data_io.aeronet import load_multiple_aeronet

This data reading routine actually performs much of the hard work in
reading the aeronet file::

    if data is None:
        data = load_multiple_aeronet(filenames)

Note that we only read the files if Data is None, that is if we haven’t
been passed any data already.

.. note::

    The load_multiple_aeronet routine uses the numpy genfromtext method to
    read in the csv file. This is a very useful method for reading text
    based files as it allows you to define the data formats of each of the
    columns, tell it which lines to ignore as comments and, optionally, mask
    out any missing values. This method would provide a useful example for
    reading different kinds of text based file.

We just have to describe (add metadata to) each of the components in
this method::

    coords = CoordList()
    coords.append(Coord(data['longitude'], Metadata(name="Longitude",shape=(len(data),),units="degrees_east", range=(-180, 180))))
    coords.append(Coord(data['latitude'], Metadata(name="Latitude",shape=(len(data),),units="degrees_north", range=(-90, 90))))
    coords.append(Coord(data['altitude'], Metadata(name="Altitude",shape=(len(data),), units="meters")))
    time_coord = Coord(data["datetime"], Metadata(name="DateTime",standard_name='time', shape=(len(data),),units="DateTime Object"), "X")

Note that we’ve explicitly added things like units and a shape. These
are sometimes already populated for us when reading e.g. NetCDF files,
but in the case of AERONET data we have to fill it out 'by hand'.

Internally CIS uses a ‘standard’ time defined as fractional days since
the 1\ :sup:`st` January 1600, on a Gregorian calendar. This allows us
to straightforwardly compare model and measurement times regardless of
their reference point. There are many helper methods for converting
different date-time formats to this standard time, here we use
:meth:`.Coord.convert_datetime_to_standard_time`, and then include the coordinate
in the coordinate list::

    time_coord.convert_datetime_to_standard_time()
    coords.append(time_coord)

Finally we return the coordinates::

    return coords

For the :meth:`create_data_object` method we have the familiar signature and
import statements::

    def create_data_object(self, filenames, variable):
        from cis.data_io.aeronet import load_multiple_aeronet
        from cis.exceptions import InvalidVariableError

We can pass the job of reading the data to our Aeronet reading routine –
catching any errors which occur because the variable doesn’t exist.

::

    try:
        data_obj = load_multiple_aeronet(filenames, [variable])
    except ValueError:
        raise InvalidVariableError(variable + " does not exist in " + str(filenames))

.. note::

    Notice here that we’re catching a :class:`ValueError` – which Numpy throws when
    it can’t find the specified variable in the data, and rethrowing the
    same error as an :exc:`.InvalidVariableError`, so that CIS knows how to deal
    with it. Any plugins should use this error when a user specifies a
    variable which isn’t within the specified file.

Now we have read the data, we load the coordinate list, but notice that
we also pass in the data we’ve just read. This is why we created a
separate coordinate reading routine earlier: The data containing the
coordinates has already been read in the line above, so we don’t need to
read it twice, we just need to pull out the coordinates. This saves time
opening the file multiple times, and can be a useful pattern to remember
for files which aren’t direct access (such as text files).

::

    coords = self._create_coord_list(filenames, data_obj)

Finally we return the complete data object, including some associated
metadata and the coordinates.

::

    return UngriddedData(data_obj[variable], Metadata(name=variable, long_name=variable, shape=(len(data_obj),), missing_value=-999.0), coords)

Here’s the plugin in full::

    class Aeronet(AProduct):

        def get_file_signature(self):
            return [r'.*\.lev20']

        def _create_coord_list(self, filenames, data=None):
            from cis.data_io.ungridded_data import Metadata
            from cis.data_io.aeronet import load_multiple_aeronet

            if data is None:
                data = load_multiple_aeronet(filenames)

            coords = CoordList()
            coords.append(Coord(data['longitude'], Metadata(name="Longitude", shape=(len(data),),
                                                            units="degrees_east", range=(-180, 180))))
            coords.append(Coord(data['latitude'], Metadata(name="Latitude", shape=(len(data),),
                                                           units="degrees_north", range=(-90, 90))))
            coords.append(Coord(data['altitude'], Metadata(name="Altitude", shape=(len(data),), units="meters")))
            time_coord = Coord(data["datetime"], Metadata(name="DateTime", standard_name='time', shape=(len(data),),
                                                          units="DateTime Object"), "X")
            time_coord.convert_datetime_to_standard_time()
            coords.append(time_coord)

            return coords

        def create_coords(self, filenames, variable=None):
            return UngriddedCoordinates(self._create_coord_list(filenames))

        def create_data_object(self, filenames, variable):
            from cis.data_io.aeronet import load_multiple_aeronet
            from cis.exceptions import InvalidVariableError

            try:
                data_obj = load_multiple_aeronet(filenames, [variable])
            except ValueError:
                raise InvalidVariableError(variable + " does not exist in " + str(filenames))

            coords = self._create_coord_list(filenames, data_obj)

            return UngriddedData(data_obj[variable],
                                 Metadata(name=variable, long_name=variable, shape=(len(data_obj),), missing_value=-999.0),
                                 coords)

.. _advanced:

Advanced
--------

This more advanced tutorial will cover some of the difficulties when
reading in data which differs significantly from the structure CIS
expects, and/or has little metadata in the associated files. We take the
MODIS L2 plugin as our example, and discuss each method in turn.

There are a number of specific MODIS L2 products which we have tested
using this plugin, each with their own file signature, and so in this
plugin we take advantage of the fact that the regular expression
returned by get_file_signature can be a list. This way we create a
simple regular expression for each MODIS L2 products that we’re
supporting - rather than trying to create one, more complicated, regular
expression which matches just these products at the exclusion of all
others::

    def get_file_signature(self):
        product_names = ['MYD06_L2', 'MOD06_L2', 'MYD04_L2', 'MOD04_L2']
        regex_list = [r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

We have implemented the optional get_variable_names method here
because MODIS files sometimes contain variables which CIS is unable to
handle due to their irregular shape. We only want to report the variable
which CIS can read so we check each variable before adding it to the
list of variables we return. We know that MODIS only contains SD
variables so we can ignore any other types.

.. note::

    HDF files can contain both Vdatas (VD) and Scientific Datasets (SD) data
    collections (among others). These are stored and accessed quite
    differently, which makes dealing with these files quite fiddly - we
    often have to treat each case separately. In this case we know MODIS
    files only have SD datasets which makes things a bit simpler.

::

    def get_variable_names(self, filenames, data_type=None):
        import pyhdf.SD

        # Determine the valid shape for variables
        sd = pyhdf.SD.SD(filenames[0])
        datasets = sd.datasets()
        valid_shape = datasets['Latitude'][1]  # Assumes that latitude shape == longitude shape (it should)

        variables = set([])
        for filename in filenames:
            sd = pyhdf.SD.SD(filename)
            for var_name, var_info in sd.datasets().iteritems():
                if var_info[1] == valid_shape:
                    variables.add(var_name)

        return variables


MODIS data often has a scale factor built in, and stored against each
variable, this method reads that scale factor for a particular variable
and checks it against our built-in list of scale factors.

::

    def __get_data_scale(self, filename, variable):
        from cis.exceptions import InvalidVariableError
        from pyhdf import SD

        try:
            meta = SD.SD(filename).datasets()[variable][0][0]
        except KeyError:
            raise InvalidVariableError("Variable "+variable+" not found")

        for scaling in self.modis_scaling:
            if scaling in meta:
                return scaling
        return None

In order to use data which has been scaled, we re-scale it on reading.
This creates some overhead in the reading of the data, but saves
considerable time when performing other operations on it later in the
process. Routines like this can often be adapted from available Fortran
or IDL routines (assuming no python routines are available) for your
data.

::

    def __field_interpolate(self,data,factor=5):
        '''
        Interpolates the given 2D field by the factor,
        edge pixels are defined by the ones in the centre,
        odd factors only!
        '''
        import numpy as np

        logging.debug("Performing interpolation...")

        output = np.zeros((factor*data.shape[0],factor*data.shape[1]))*np.nan
        output[int(factor/2)::factor,int(factor/2)::factor] = data
        for i in range(1,factor+1):
            output[(int(factor/2)+i):(-1*factor/2+1):factor,:] = i*((output[int(factor/2)+factor::factor,:]-output[int(factor/2):(-1*factor):factor,:])
                                                                    /float(factor))+output[int(factor/2):(-1*factor):factor,:]
        for i in range(1,factor+1):
            output[:,(int(factor/2)+i):(-1*factor/2+1):factor] = i*((output[:,int(factor/2)+factor::factor]-output[:,int(factor/2):(-1*factor):factor])
                                                                    /float(factor))+output[:,int(factor/2):(-1*factor):factor]
        return output

Next we read the coordinates from the file (using the same method of
factoring out as we used in the Aeronet case).

::

    def _create_coord_list(self, filenames, variable=None):
        import datetime as dt

        variables = ['Latitude', 'Longitude', 'Scan_Start_Time']
        logging.info("Listing coordinates: " + str(variables))

As usual we rely on the lower level IO reading routines to provide the
raw data, in this case using the hdf.read routine.

::

    sdata, vdata = hdf.read(filenames, variables)

.. note::

    Notice we have to put the vdata data somewhere, even though we don’t use
    it in this case.

We have to check whether we need to scale the coordinates to match the
variable being read::

        apply_interpolation = False
        if variable is not None:
            scale = self.__get_data_scale(filenames[0], variable)
            apply_interpolation = True if scale is "1km" else False

Then we can read the coordinates, one at a time. We know the latitude
information is stored in an SD dataset called Latitude, so we read that
and interpolate it if needed.

::

        lat = sdata['Latitude']
        sd_lat = hdf.read_data(lat, "SD")
        lat_data = self.__field_interpolate(sd_lat) if apply_interpolation else sd_lat
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata,'Y')

The same for Longitude::

        lon = sdata['Longitude']
        lon_data = self.__field_interpolate(hdf.read_data(lon,"SD")) if apply_interpolation else hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_coord = Coord(lon_data, lon_metadata,'X')


Next we read the time variable, remembering to convert it to our
internal standard time. (We know that the MODIS’ atomic clock time is
referenced to the 1\ :sup:`st` January 1993.)

::

        time = sdata['Scan_Start_Time']
        time_metadata = hdf.read_metadata(time,"SD")
        # Ensure the standard name is set
        time_metadata.standard_name = 'time'
        time_coord = Coord(time,time_metadata,"T")
        time_coord.convert_TAI_time_to_std_time(dt.datetime(1993,1,1,0,0,0))

        return CoordList([lat_coord,lon_coord,time_coord])

::

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))


For the create_data_object we are really just pulling the above
methods together to read the specific variable the user has requested
and combine it with the coordinates.

::

    def create_data_object(self, filenames, variable):
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self._create_coord_list(filenames, variable)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)

We have also implemented the :meth:`.AProduct.get_file_format` method which allows some
associated tools (for example the `CEDA_DI <https://github.com/cedadev/ceda-di>`__ tool) to use CIS to index
files which they wouldn’t otherwise be able to read. We just return a
file format descriptor as a string.

::

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "HDF4/ModisL2"

The full MODIS L2 plugin is rather long to show but can be downloaded
`here <https://github.com/cedadev/cis/blob/master/cis/data_io/products/MODIS.py>`__.

.. _plugin_content:

Plugin contents
===============

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

