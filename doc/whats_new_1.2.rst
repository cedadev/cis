
=====================
What's new in CIS 1.2
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.1. See all changes here: https://github.com/cedadev/cis/compare/1.1.0...1.2.0


CIS 1.2 features
================

 * All new ``cis info`` command provides much more detailed information about ungridded data variables and enables multiple variables to be output at a time.
 * Updated a number of routines to take advantage of Iris 1.8 features. In particular gridded-gridded collocation using the nearest neighbour kernel should be significantly faster. Iris 1.8 is now the minimum version required for CIS.
 * Gridded-ungridded collocation now supports collocation from cubes with hybrid height or hybrid pressure coordinates for both nearest neighbour and linear interpolation kernels.
 * Built-in support for reading multiple HadGEM .pp files directly.
 * All new API and plugin development documentation, including a number of tutorials

Bugs fixed
==========

 * JASCIS-253 - Any ungridded points which contain a NaN in any of its coordinate values will now be ignored by CIS
 * JASCIS-250 - Multiple HadGEM files can now be read correctly through the new data plugins.
 * JASCIS-197 - Gridded-gridded collocation now respects scalar coordinates
 * JASCIS-199 - Aggregation now correctly uses the bounds supplied by the user, even when collapsing to length one coordinates.
 * Speed improvement to the ungridded-gridded collocation using linear interpolation
 * Several bug fixes for reading multiple GASSP ship files
 * Renamed and restructured the collocation modules for consistency
 * Many documentation spelling and formatting updates
 * Many code formatting updates for PEP8 compliance