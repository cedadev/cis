********
Plotting
********

Plotting is straightforward::

  $ cis plot variable:filenames

This will attempt to locate the variable ``variable`` in all of the specified ``filenames``, work out its metadata, such as units, labels, etc. and the appropriate chart type to plot, so that a line graph is used for two dimensional data, a scatter plot is used for three dimensional ungridded data and a heatmap for three dimensional gridded data. Other types of chart can be specified using the ``--type`` option. Available types are:

``line``
  a simple line plot, for three dimensional data the third variable is represented by the line colour

``scatter``
  a scatter plot

``scatter2d``
  a scatter plot with two coordinate axis and the data represented by the colour of the marker

``heatmap``
  a heatmap especially suitable for gridded data

``contour``
  a standard contour plot, see :ref:`contour options <contour-options>`

``contourf``
  a filled contour plot, see :ref:`contour options <contour-options>`

``histogram2d``

``histogram``

``comparativescatter``
  allows two variables to be plotted against each other, specified as ``cis plot variable1:filename1 variable2:filename2 --type comparativescatter``

``taylor``
  a Taylor diagram for comparing collocated datasets. See Taylor, K. E. (2001), 'Summarizing multiple aspects of model performance in a single diagram', J. Geophys. Res., 106(D7), 7183–7192, doi:10.1029/2000JD900719 for a detailed description.


Note that ``filenames`` is a non-optional argument used to specify the files to read the variable from. These can be specified as a comma separated list of the following possibilities:

  #. A single filename - this should be the full path to the file
  #. A single directory - all files in this directory will be read
  #. A wildcarded filename - A filename with any wildcards compatible with the python module glob, so that \*, ? and [] can all be used. For example ``/path/to/my/test*file_[0-9]``.

Note that when using option 2, the filenames in the directory will be automatically sorted into alphabetical order. When using option 3, the filenames matching the wildcard will also be sorted into alphabetical order. The order of the comma separated list will however remain as the user specified, e.g.::

  $ cis plot $var:filename1,filename2,wildc*rd,/my/dir/,filename3

would read ``filename1``, then ``filename2``, then all the files that match ``wildc*rd`` (in alphabetical order), then all the files in the directory ``/my/dir/`` (in alphabetical order) and then finally ``filename3``.

Plot Options
============

There are a number of optional arguments, which should be entered as a comma separated list after the mandatory arguments, for example ``variable:filename:product=Cis,edgecolor=black``. The options are:

``color``
  colour of markers, e.g. for scatter plot points or contour lines, see :ref:`colours-and-markers`

``cmap``
  colour map to use, e.g. for contour lines or heatmap, see :ref:`colours-and-markers`

``vmin``
  the minimum value for the colourmap

``vmax``
  the maximum value for the colourmap

``edgecolor``
  colour of scatter marker edges (can be used to differentiate scatter markers with a colourmap from the background plot)

``itemstyle``
  shape of scatter marker, see :ref:`colours-and-markers`

``itemwidth``
  width of an item. Units are points in the case of a line, and points^2 in the case of a scatter point

``label``
  name of datagroup for the legend

``product``
  the data product to use for the plot

``type``
  the type of plot for that layer. This can't be set if the global type has been set.

``alpha``
  the transparancy of that layer

``cbarlabel``
  The label for the colorbar

``cbarorient``
  The orientation of the colour bar, either horizontal or vertical

``nocolourbar``
 Hides the colour bar on a 3D plot

``cbarscale``
  this can be used to change the size of the colourbar when plotting and defaults to 0.55 for vertical colorbars, 1.0
  for horizontal.

.. _contour-options:

Additional datagroup options for contour plots only:

``contnlevels``
  the number of levels for the contour plot

``contlevels``
  a list of levels for the contour plot, e.g. ``contlevels=[0,1,3,10]``

``contlabel``
  options are ``true`` or ``false``, if true then contour labels are shown

``contwidth``
  width of the contour lines

Note that ``label`` refers to the label the plot will have on the legend, for example if a multi-series line graph or scatter plot is plotted. To set the labels of the axes, use ``--xlabel`` and ``--ylabel``. ``--cbarlabel`` can be used to set the label on the colour bar.

The axes can be specified with ``--xaxis`` and ``--yaxis``. Gridded data supports any coordinate axes available in the file, while ungridded data supports the following coordinate options (if available in the data):

  * ``latitude``
  * ``longitude``
  * ``time``
  * ``altitude``
  * ``air_pressure``
  * ``variable`` - the variable being plotted

If the product is not specified, the program will attempt to figure out which product should be used based on the filename.  See :doc:`data_products` to see a list of available products and their file signatures, or run ``cis plot -h``.


Saving to a File
================

By default a plot will be displayed on screen. To save it to an image file instead, use the ``--output`` option. Available output types are png, pdf, ps, eps and svg, which can be selected using the appropriate filename extension, for example ``--output plot.svg``.


Plot Formatting
===============

There are a number of plot formatting options available:

``--xlabel``
  The label for the x axis

``--ylabel``
  The label for the y axis

``--title``
  The title of the plot

``--fontsize``
  The size of the font in points

``--cmap``
  The colour map to be used when plotting a 3D plot, see :ref:`colours-and-markers`

``--projection``
  The projection to use for the map-plot. All Cartopy projections are supported, see http://scitools.org.uk/cartopy/docs/latest/crs/projections.html for a full list.

``--height``
  The height of the plot, in inches

``--width``
  The width of the plot, in inches

``--xbins``
  The number of bins on the x axis of a histogram

``--ybins``
  The number of bins on the y axis of a histogram

``--grid``
  Shows grid lines

``--coastlinescolour``
  The colour of the coastlines on a map, see :ref:`colours-and-markers`

``--nasabluemarble``
  Use the NASA Blue Marble for the background, instead of coastlines, when doing lat-lon plots

.. _taylor-options:

``--bias``
  Plot the bias between the data sets using specified mechanism. Can be either 'color', 'colour', 'size' or 'flag'

``--solid``
  Use solid markers

``--extend``
  Extend plot for negative correlation

``--fold``
  Fold plot for negative correlation or large variance

``--gammamax``
  Fix maximum extent of radial axis

``--stdbiasmax``
  Fix maximum standardised bias


Setting Plot Ranges
===================

The arguments ``--xmin``, ``--xmax``, ``--xstep``, ``--ymin``, ``--ymax``, ``--ystep``, ``--vmin``, ``--vmax``, ``--vstep`` can be used to specify the range of values to plot, where x and y correspond to the axes and v corresponds to the colours.

When the arguments refer to dates or times, they should be in the format ``YYYY-MM-DDThh:mm:ss``, where the time is optional. A colon or a space is also a valid date and time separator (if using a space quotes are necessary).

The ``step`` arguments are used to specify the tick spacing on the axes and ``vstep`` is used to specify the tick spacing on the colorbar.

When the ``step`` arguments refer to an amount of time, they should be in the ISO 8601 format ``PnYnMnDTnHnMnS``, where any particular time group is optional, case does not matter, and ``T`` can be substituted for either a colon or a space (if using a space quotes are necessary).

For example, to specify a tick spacing of one month and six seconds on the x axis, the following argument should be given:
``--xstep 1m6S`` 

Note: If a value is negative, then an equals sign must be used, e.g.
``--xmin=-5``.

To plot using a log scale:

``--logx``
  The x axis will be plotted using a log scale of base 10

``--logy``
  The y axis will be plotted using a log scale of base 10

``--logv``
  The values (colours) will be plotted using a log scale of base 10


.. _overlay-plots:

Overlaying Multiple Plots
=========================

Overlaying multiple plots is straightforward, simply use the plot command as before but specify multiple files and variables, e.g.::

  $ cis plot $var1:$filename1:edgecolor=black $var2:$filename2:edgecolor=red

To plot two variables from the same file, simply use the above command with `$filename1` in place of `$filename2`.

The ``type`` paramter can be used to specify different types for each layer. For example, to plot a heatmap and a contour plot the following options can be used::

  cis plot var1:file1:type=heatmap var2:file2:type=contour,color=white --width 20 --height 15 --cbarscale 0.5 -o overlay.png

Note that the default plot dimensions are deduced from the first datagroup specified.

Many more examples are available in the :doc:`overlay examples <overlay_examples>` page.


.. _colours-and-markers:

Available Colours and Markers
=============================

CIS recognises any valid  `html colour`_, specified using its name e.g. `red` for options such as item colour (line/scatter colour) and the colour of the coast lines.

A list of available colour maps for 3D plots, such as heatmaps, scatter and contour plots, can be found here: `colour maps`_.

For a list of available scatter point styles, see here: `scatter point styles`_.

.. _`html colour`: http://www.w3schools.com/html/html_colornames.asp
.. _`colour maps`: http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps
.. _`scatter point styles`: http://matplotlib.org/api/markers_api.html#module-matplotlib.markers

