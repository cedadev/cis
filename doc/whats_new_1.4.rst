
=====================
What's new in CIS 1.4
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.3. See all changes here: https://github.com/cedadev/cis/compare/1.3.1...1.4.0


CIS 1.4 features
================

 * CIS now includes full support for Python 3, as well as Python 2.7
 * Significant optimizations have been made in gridded -> ungridded collocation which should now be considerably faster.
   Also, when collocating multiple gridded source datasets the interpolation indices are now cached internally leading
   to further time savings.
 * CIS no longer prepends ungridded output files with 'cis-'. Instead CIS creates a global attribute in the output file
   called source which contains 'CIS<version>'. This is checked in the updated CIS plugin when reading any NetCDF file.

   .. note::
      While this is much neater going forward and will hopefully save a lot of head scratching it will mean CIS is unable
      to read old files produced by CIS automatically. All commands can be forced to use the CIS product by including the
      product=cis keyword argument. Alternatively you can update the data file manually using the following command:
      ``ncatted -O -a source,global,a,c,"CIS" in.nc``
 * Any ``valid_range`` attributes in supported NetCDF or HDF files (including MODIS, CALIOP and CloudSat) files are now
   automatically respected by CIS. All data values outside of the valid range are masked. Data from NetCDF files with
   ``valid_min`` or ``valid_max`` attributes is also masked appropriately.
 * CloudSat ``missing`` and ``missop`` attributes are now read and combined to mask out values which don't conform to the
   inequality defined.


Bugs fixed
==========

 * [JASCIS-34] MODIS L3 data is now correctly treated as gridded data.