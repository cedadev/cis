***********
Aggregation
***********

The Community Intercomparison Suite (CIS) has the ability to aggregate along one or more coordinates, currently for **gridded data only**. This page describes how to perform aggregation and the options available.

To perform aggregation, run a command of the format::

  $ cis aggregate variable:filenames[:options] grid -o outputfile

where:

``variable``
  A non-optional argument used to specify the name of the variable to aggregate

``filenames`` 
  A non-optional argument used to specify the files to read the variable from. These can be specified as a comma separated list of the following possibilities:

    #. A single filename - this should be the full path to the file
    #. A single directory - all files in this directory will be read
    #. A wildcarded filename - A filename with any wildcards compatible with the python module glob, so that \*, ? and [] can all be used. E.g. /path/to/my/test*file_![0-9]. 

  Note that when using option 2, the filenames in the directory will be automatically sorted into alphabetical order. When using option 3, the filenames matching the wildcard will also be sorted into alphabetical order. The order of the comma separated list will however remain as the user specified, e.g. ``filename1,filename2,wildc*rd,/my/dir/,filename3``, would read ``filename1``, then ``filename2``, then all the files that match ``"wildc*rd"`` (in alphabetical order), then all the files in the directory ``"/my/dir/"`` (in alphabetical order) and then finally ``filename3``.

``options``
  Optional arguments given as keyword=value in a comma separated list. Options are:

  * ``kernel`` - either ``mean``, ``max``, ``min`` or ``stddev`` depending on the type of aggregation required. If not specified the default is ``mean``.
  * ``product`` - the data product to use for the plot (see :ref:`data-products-reading`).

``grid``
  The coordinates to aggregate are specified, along with a start, end and step size if not completely collapsing a dimension. For example, to completely collapse time and to aggregate latitude on a grid from -45 degrees to 45 degrees, using a step size of 10 degrees:

  * ``t,y=[-45,45,10]``

  Date/times are specified in the format: ``YYYY-MM-DDThh:mm:ss`` in which ``YYYY-MM-DD`` is a date and ``hh:mm:ss`` is a time. A colon or space can be used instead of the 'T' separator (but if a space is used, the argument must be quoted). Any trailing components of the date/time may be omitted. When a date/time is used as a range start, the earliest date/time compatible with the supplied components is used (e.g., ``2010-04`` is treated as ``2010-04-01T00:00:00``) and when used as a range end, the latest compatible date/time is used. Including optional and alternative components, the syntax is ``YYYY[-MM[-DD[{T|:| }hh[:mm[:ss]]]]]``. When the ``t=[value]`` form is used, value is interpretted as both the start and end value, as described above, giving a range spanning the specified date/time, e.g., ``t=[2010]`` gives a range spanning the whole of the year 2010.

  Date/time steps are specified as ``$y$m$d$H$M$s``, where any particular time period is optional, for example ``1m30M`` would specify a time interval of 1 month and 30 minutes. Years and months are treated as calendar years and months, meaning they are not necessarily fixed in length. For example a date interval of 1 year and 1 month would mean going from 12:00 15th April 2013 to 12:00 15th May 2013. The are two exceptions to this, in rare cases such as starting at 30th January and going forward 1 month, the month is instead treated as a period of 28 days. Also, for the purposes of finding midpoints for the start in a month the month is always treated as 30 days. For example, to start on the 3rd November 2011 at 12:00 and aggregate over each month up to 3rd January 2013 at 12:00:

  * ``t=[2011-11-03T12:00,2013-01,1m]``

.. note::  
   The range specified is the very start and end of the grid, the actual midpoints of the aggregation cells will start at ``start + delta/2``.  CIS will throw a warning and automatically reduce the range if the grid requested goes outside the range of the gridded data. The start and end of the gridded data are considered to be from the start of the bounding box of the first cell to the end of the bounding box for the last cell.
  
``outputfile``
  is an optional argument to specify the name to use for the file output. This is automatically given a .nc extension and prepended with cis- to make it distinguishable as a colocated file. The default filename is cis-out.nc.

A full example would be::

  $ cis aggregate rsutcs:rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.nc:product=NetCDFGriddedByVariableName,kernel=mean t,y=[-90,90,20],x -o rsutcs-mean

Aggregation Examples
====================

Gridded-gridded aggregation
---------------------------

Aggregating onto a coarser grid::

  $ cis aggregate rsutcs:rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.nc:product=NetCDFGriddedByVariableName,kernel=mean t,y=[-90,90,20],x=[-0.9375,359.0625,20]
  $ cis plot rsutcs:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s --type scatter --itemwidth 400 --ymin -90 --ymax 90

.. figure:: img/aggregation/lat-lon-coarser.png
   :width: 400px
   :align: center

Aggregating a subset of latitude, ignoring longitude::

  $ cis aggregate rsutcs:rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.nc:product=NetCDFGriddedByVariableName,kernel=mean t,y=[-45,45,15]
  $ cis plot rsutcs:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s --ymin -45 --ymax 45 --type scatter --itemwidth 300

.. figure:: img/aggregation/lat-subset.png
   :width: 400px
   :align: center

Aggregating in time - years::

  $ cis aggregate rsutcs:rsutcs_Amon_HadGEM2-A_sstClim_r1i1p1_185912-188911.nc:product=NetCDFGriddedByVariableName,kernel=mean t=[1859-11-27,1869-11-27,1y],y=[-90,90,20],x
  $ cis plot rsutcs:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s --xaxis time --yaxis latitude --type scatter --itemwidth 400 --ymin -90 --ymax 90

.. figure:: img/aggregation/years.png
   :width: 400px
   :align: center

Aggregating in time - months, days and hours::

  $ cis aggregate tas:tas_day_HadGEM2-ES_rcp45_r1i1p1_20051201-20151130.nc:product=NetCDFGriddedByVariableName,kernel=mean t=[2003,2015,1m1d1H],x
  $ cis plot tas:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s --xaxis time --yaxis latitude --type scatter --itemwidth 10 

.. figure:: img/aggregation/months-days.png
   :width: 400px
   :align: center

Maximum kernel::

  $ cis aggregate tas:tas_day_HadGEM2-ES_rcp45_r1i1p1_20051201-20151130.nc:product=NetCDFGriddedByVariableName,kernel=max t
  $ cis plot tas:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s

.. figure:: img/aggregation/max.png
   :width: 400px
   :align: center

Standard deviation kernel::

  $ cis aggregate tas:tas_day_HadGEM2-ES_rcp45_r1i1p1_20051201-20151130.nc:product=NetCDFGriddedByVariableName,kernel=stddev t
  $ cis plot tas:cis-out.nc:product=NetCDFGriddedByVariableName,itemstyle=s

.. figure:: img/aggregation/stddev.png
   :width: 400px
   :align: center

