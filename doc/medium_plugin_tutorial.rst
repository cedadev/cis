
.. _medium:

Medium
------

For this example we will look at the AERONET data reading plugin.
AERONET is a ground based sun-photometer network that produces
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
    there is in Java and C#, but we can signify that a method shouldn't be
    accessed externally by starting its name with one or two underscores.

In this method we import an AERONET data reading routine::

    def _create_coord_list(self, filenames, data=None):
        from cis.data_io.ungridded_data import Metadata
        from cis.data_io.aeronet import load_multiple_aeronet

This data reading routine actually performs much of the hard work in
reading the AERONET file::

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

We can pass the job of reading the data to our AERONET reading routine –
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

