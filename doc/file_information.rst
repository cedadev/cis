========================
Getting file information
========================

The info command provides a visual summary of the data within any of the data files CIS supports.

To get this summary, run a command of the format::

  $ cis info <datagroup> [--type ["VD" | "SD"]]

where:

``<datagroup>``
  is a :ref:`CIS datagroup <datagroups>` specifying the variables and files to read and is of the format
  ``[<variable>...:]<filename>[:product=<productname>]`` where:

    * ``variable`` is an optional variable or list of variables to use.
    * ``filenames`` is a mandatory file or list of files to read from.
    * ``product`` is an optional CIS data product to use (see :ref:`Data Products <data-products-reading>`):

  See :ref:`datagroups` for a more detailed explanation of datagroups.

``--type`` allows the user to list only ``SD`` or ``VD`` variables from an HDF file, the default is ``All``


Running without a variable (``$ cis info <filenames>``) will print a list of the variables available in those files
such as::

  Trop
  latitude
  longitude_1
  surface
  unspecified_1
  level6
  ht
  msl
  latitude_1

To get more specific information about one or more variables in those files, simply pass those as well::

  $ cis info var1,var2:<filenames>

where ``$var1`` and ``$var2`` are the names of the variables to get the information for.

Here is an example output::

    Ungridded data: SO4 / (ug m-3)
         Shape = (6478,)
         Total number of points = 6478
         Number of non-masked points = 6478
         Long name = Sulphate
         Standard name = SO4
         Units = ug m-3
         Missing value = -9999
         Range = (-0.57346399999999997, 7.0020300000000004)
         History =
         Coordinates:
           time
              Long name = Starting time
              Standard name = time
              Units = days since 1600-01-01 00:00:00
              Calendar = gregorian
              Missing value = -9999
              Range = ('2008-07-10 02:04:35', '2008-07-20 09:50:33')
              History =
           latitude
              Long name = Latitude
              Standard name = latitude
              Units = N degree
              Missing value = -9999
              Range = (4.0211802, 7.14886)
              History =
           longitude
              Long name = Longitude
              Standard name = longitude
              Units = E degree
              Missing value = -9999
              Range = (114.439, 119.733)
              History =
           altitude
              Long name = Altitude
              Standard name = altitude
              Units = m
              Missing value = -9999
              Range = (51.164299, 6532.6401)
              History =

