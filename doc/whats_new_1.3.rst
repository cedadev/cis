
=====================
What's new in CIS 1.3
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.2. See all changes here: https://github.com/cedadev/cis/compare/1.2.1...1.3.0


CIS 1.3 features
================

 * Compatibility updates for newer versions of Numpy and SciPy. The minimum require version of SciPy is now 0.16.0
 * Swapped out Basemap plotting routines for Cartopy. This removed a dependancy (as Cartopy was already required by Iris), and has given us more flexibility for plotting different projections in the future
 * Plots now automatically try to use the most appropriate resolution background images for plots over coastlines NASA blue marble images.

Bugs fixed
==========

 * JASCIS-279 - This release removes the basemap dependency and means we can use a much newer version of GEOS which doesn't clash with the SciTools version
 * JASCIS-267 - Fixed ASCII file reading to be compatible with Numpy 1.9
 * JASCIS-259 - Fixed Stats unit tests to reflect updates in SciPy (>0.15.0) linear regression routines for masked arrays
 * JASCIS-211 - Subsetting now accepts variable names (rather than axes shorthands) more consistently, the docs have been updated to make the dangers of relying on axes shorthands clear and an error is now thrown if a specific subset coordinate is not found.
