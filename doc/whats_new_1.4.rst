
=====================
What's new in CIS 1.4
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.3.1. See all changes here: https://github.com/cedadev/cis/compare/1.3.1...1.4.0


CIS 1.4 features
================
 * An all new Python interface for subsetting any data read by CIS. Just call the :meth:`subset` method on any CIS GriddedData
   or UngriddedData object to access the same functionality as through the command line - without reading or writing to
   disk. See :doc:`CIS API<cis_api>` for more details.

 * CIS now includes full support for Python => 3.4, as well as Python 2.7
 * New verbose and quiet flags allow for control over how much CIS commands output to the screen. The default verbosity
   has also changed so that by default only warnings and errors will be output to the screen. The full debug output
   remains for the cis.log file.
 * Significant optimizations have been made in gridded -> ungridded collocation which should now be considerably faster.
   Also, when collocating multiple gridded source datasets the interpolation indices are now cached internally leading
   to further time savings.
 * Any ``valid_range`` attributes in supported NetCDF or HDF files (including MODIS, CALIOP and CloudSat) files are now
   automatically respected by CIS. All data values outside of the valid range are masked. Data from NetCDF files with
   ``valid_min`` or ``valid_max`` attributes is also masked appropriately.
 * CloudSat ``missing`` and ``missop`` attributes are now read and combined to mask out values which don't conform to the
   inequality defined.
 * [JASCIS-342] The extrapolation modes are now consistent across both gridded->gridded and gridded->ungridded collocation
   modes. The default is no extrapolation (gridded->gridded would previously extrapolate). This can still be overridden
   by the user.
 * [JASCIS-128] If the output file already exists the user is now prompted to overwrite it. This prompt can be disabled
   by using the --force-overwrite argument, or setting the ``CIS_FORCE_OVERWRITE`` environment variable to 'TRUE'.

Incompatible changes
====================
 * To accommodate the new verbose flags (-v) the info command now takes a single datagroup argument, and optional
   variable names, as reflected in the updated documentation.
 * CIS no longer prepends ungridded output files with 'cis-'. Instead CIS creates a global attribute in the output file
   called source which contains 'CIS<version>'. This is checked in the updated CIS plugin when reading any NetCDF file.

   .. note::
      While this is much neater going forward and will hopefully save a lot of head scratching it will mean CIS is unable
      to read old files produced by CIS automatically. All commands can be forced to use the CIS product by including the
      product=cis keyword argument. Alternatively you can update the data file manually using the following command:
      ``ncatted -O -a source,global,a,c,"CIS" in.nc``

Bugs fixed
==========

 * [JASCIS-34] MODIS L3 data is now correctly treated as gridded data.
 * [JASCIS-345] Product regular expression matching now matches the whole string rather than just the start.
 * [JASCIS-360] Collocation now correctly applies the 'missing_data_for_missing_sample' logic for all collocations.
 * [JASCIS-361] Fixed the CloudSat scale and offset transformation so that they are now applied correctly.
 * [JASCIS-281] Fixed a caching error when aggregating multiple ungridded datasets which could lead to incorrect values
 * CIS no longer crashes when the CIS_PLUGIN_HOME path cannot be found