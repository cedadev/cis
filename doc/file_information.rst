========================
Getting file information
========================

Running `` ./cis.py info $filename `` will print a list of the variables available in that input file such as::

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

  $ ./cis.py info $filename --variable $var1 $var2 $var3

where ``$var1``, ``$var2`` and ``$var3`` are the names of the variables to get the information for.

Here is an example::

  <type 'netCDF4.Variable'>
  float32 mass(t, unspecified_1, latitude, longitude_1)
      _FillValue: 2e+20
      date: 01/09/08
      long_name: TOTAL COLUMN DRY MASS  RHO GRID
      missing_value: 2e+20
      name: mass
      source: Unified Model Output (Vn 7.3):
      time: 00:00
      title: TOTAL COLUMN DRY MASS  RHO GRID
      units: kg m-2
  unlimited dimensions: t
  current shape = (1, 1, 145, 192)
