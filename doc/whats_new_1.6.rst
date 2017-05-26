
=====================
What's new in CIS 1.6
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.5.0. See all changes here: https://github.com/cedadev/cis/compare/1.5.0...1.6.0


CIS 1.5 features
================
 * Ungridded - ungridded collocation performance improvements


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
