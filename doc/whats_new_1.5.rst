
=====================
What's new in CIS 1.5
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.4.0. See all changes here: https://github.com/cedadev/cis/compare/1.4.0...1.5.0


CIS 1.5 features
================
 * The biggest change is that CIS can now be used as a Python library, all of the command line tools are now easily
   available through Python. This allows commands to be run sequentially in memory, slicing of gridded or ungridded
   datasets and easy integration with other Python packages such as Iris and Pandas.
 * Taylor diagrams - CIS is now able to plot Taylor diagrams which are an excellent way of quantitatively comparing two
   or more (collocated) datasets
 * All map plots are now able to be plotted in any of the available Cartopy projections, see
   http://scitools.org.uk/cartopy/docs/latest/crs/projections.html for a full list.


Incompatible changes
====================
 * Since aggregation of gridded datasets has quite a different set of options as compared to the aggregation of
   ungridded datasets, the ``aggregate`` command has been deprecated for gridded datasets. It is still supported through
   command line for the time being, but will be removed in future releases. Please use the ``collapse`` command instead.

Bugs fixed
==========

 * [JASCIS-268] The plotting routines have been re-architected to allow easier testing and extension.
 * [JASCIS-357] Added deprecation for the aggregation of gridded datasets
 * [JASCIS-329] Metadata objects now attempt to use cf_units for all units, but will fall back to strings if needed. In
   future releases we may insist on plugins providing standard units.

CIS 1.5.1 fixes
===============
 * Minor fix in interpreting units when reading some NetCDF data in Python 2
 * Fixed an issue where line and scatter plots weren't respecting the yaxis keyword

CIS 1.5.2 fixes
===============
 * Gridded and ungridded datasets can now be subset to an arbitrary lat/lon (shapely) shape.
 * Slicing and copying Coords now preserves the axis
 * Fixed an issue where subsetting gridded data over multiple coordinates sometimes resulted in an error
 * CIS will now catch errors when writing out metadata values which might have special types and can't be safely
   cast (e.g. VALID_RANGE).
 * Minor fix for log scale color bars
 * Minor fix for parsing the command aliases
 * Minor fix for creating data lists from iterators

CIS 1.5.3 fixes
===============
 * Fixed a (potentially serious) bug in unit parsing which would convert any string to lowercase.
 * Minor fix when reading variables from PP files with spaces in the name