
=====================
What's new in CIS 2.0
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.5.0. See all changes here: https://github.com/cedadev/cis/compare/1.5.0...2.0.0


CIS 2.0 features
================
 * Ungridded - ungridded collocation performance improvements


Incompatible changes
====================
 * Complete API overhaul

Bugs fixed
==========

 * In previous versions of CIS cartographic weights were calculated for all collapse operations regardless of the
 dimensions being collapsed. This may have given unexpected values in some cases. CIS now only calculates weights
 when collapsing over latitude.
 * Plot colourbars are now associated with the plot axes rather than the figure, which makes it easier to make
 multi-axes plots with CIS.
 * Fixed an issue where `UngriddedData.copy()` didn't copy metadata