========================
Getting file information
========================

Running ``$ cis info <filenames>`` will print a list of the variables available in those files such as::

  Trop
  latitude
  longitude_1
  surface
  unspecified_1
  level6
  ht
  msl
  latitude_1

To get more specific information about a given variable, simply run::

  $ cis info <filenames> -v $var1 $var2 $var3

where ``$var1``, ``$var2`` and ``$var3`` are the names of the variables to get the information for.

Other options available include:
  * ``--product`` which allows the user to override the default product for the files, and
  * ``--type`` which allows the user to list only ``SD`` or ``VD`` variables from an HDF file, the default is ``All``

Here is an example::

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

