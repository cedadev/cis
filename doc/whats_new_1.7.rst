
=====================
What's new in CIS 1.7
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.6.0. See all changes here:
https://github.com/cedadev/cis/compare/1.6.0...1.7.0

CIS 1.7 features
================
 * Extended the definition of the MODIS_L3 plugin to include monthly files.
 * Added plugins Aerosol_CCI_L3 and Cloud_CCI_L3 to read Level 3 CCI products.
 * Extended the Aeronet plugin to read files from:
    * The Version 3 Direct Sun Algorithm,
    * The Maritime Aerosol Network,
    * All versions of the Spectral Decomposition Algorithm,
    * The All_Sites_Times_*.dat files now distributed under the "Download All Sites" link.

Incompatible changes
====================
 * Renamed the plugins Aerosol_CCI and Cloud_CCI to Aerosol_CCI_L2 and Cloud_CCI_L2 to be consistent with MODIS.
 * Updated to Iris 2.0.0 and pyHDF 0.9.0 (removing previous workarounds).
 * Gridded / gridded collocation of time coordinates is no longer supported since iris no longer allows the
   determination of whether a point lies within a bounded region for datetime-like objects

Bugs fixed
==========
 * In a PP file, if a var_name contains spaces the plugin will now attempt to replace them with underscores.

CIS 1.7.1 fixes
===============
 * Fixed an issue where interpolation would unmask masked source arrays
 * Support for Pandas 0.24
