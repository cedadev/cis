
=====================
What's new in CIS 1.6
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.5.0. See all changes here: https://github.com/cedadev/cis/compare/1.5.4...1.6.0


CIS 1.6 features
================
 * Implemented ungridded - ungridded collocation performance improvements (#9)
 * Improved reading of NCAR-RAF style NetCDF files
 * Performance improvement when reading many (100s of) NetCDF files
 * Improved support for reading CALIOP L2 data

Incompatible changes
====================
 *

Bugs fixed
==========

 * In previous versions of CIS cartographic weights were calculated for all collapse operations regardless of the
 dimensions being collapsed. This may have given unexpected values in some cases. CIS now only calculates weights
 when collapsing over latitude.
 * Plot colourbars are now associated with the plot axes rather than the figure, which makes it easier to make
 multi-axes plots with CIS.
 * Fixed an issue where `UngriddedData.copy()` didn't copy metadata
 * [JASCIS-373] get_variable_names now gets passed the product argument from read_data_list
 * Fix #11 by relying on shapely exception which moved
 * [JASCIS-375] Ensure the mask is retained when expanding coordinates from 1d to 2d
 * The Cloudsat reader no longer expands coordinate arrays for 1-d datasets (such as ice-water path)
