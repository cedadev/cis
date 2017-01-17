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
the signature matches any file which ends with `.nc` (we also check the
source attribute but that is beyond the scope of this tutorial)::

    def get_file_signature(self):
        return [r'\.nc']

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
    the other data products. See the :doc:`API <cis_api>` section for further
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

