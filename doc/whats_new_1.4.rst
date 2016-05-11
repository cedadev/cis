
=====================
What's new in CIS 1.4
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.3. See all changes here: https://github.com/cedadev/cis/compare/1.3.1...1.4.0


CIS 1.4 features
================

 * CIS no longer prepends ungridded output files with 'cis-'. Instead CIS creates a global attribute in the output file
   called source which contains 'CIS<version>'. This is checked in the updated CIS plugin when reading any NetCDF file.

.. note::
   While this is much neater going forward and will hopefully save a lot of head scratching it will mean CIS is unable
   to read old files produced by CIS automatically. All commands can be forced to use the CIS product by including the
   product=cis keyword argument. Alternatively you can update the data file manually using the following command:
   ``ncatted -O -a source,global,a,c,"CIS" in.nc``

Bugs fixed
==========

