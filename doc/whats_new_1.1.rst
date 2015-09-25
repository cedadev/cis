
=====================
What's new in CIS 1.1
=====================

This page documents the new features added, and bugs fixed in CIS since version 1.0. For more detail see all changes here: https://github.com/cedadev/cis/compare/1.0.0...1.1.0

CIS 1.1 features
================

 * JASMIN-CIS is now called CIS, and the packages, modules and documentation have been renamed accordingly.
 * Conda packages are now available to allow much easier installation of CIS, and across more platforms: Linux, OSX and Windows.
 * PyHDF is now an optional dependency. This makes the installation of CIS on e.g. Windows much easier when HDF reading is not required.

Bugs fixed
==========

 * JASCIS-243 - Error when reading multiple GASSP aircraft files
 * JASCIS-139 - Updated ungridded aggregation to rename any variables which clash with coordinate variables, as this breaks during the output otherwise.
 * Compatibility fixes for Numpy versions >1.8 and Python-NetCDF versions >1.1.
 * Fix Caliop pressure units which were stored as hPA, but need to be hPa to conform to CF.
 * The integration test data has been moved completely out of the repository - making the download quicker and less bloated. It's location can be specified by setting the CIS_DATA_HOME environment variable.
 * A test runner has been created to allow easy running of the unit and integration test.


What's new in CIS 1.1.1
=======================

This section documents changes in CIS since version 1.1, these were primarily bug fixes and documentation updates. See all changes here: https://github.com/cedadev/cis/compare/1.1.0...1.1.1

Bugs fixed
==========

 * JASCIS-181 - Updated eval documentation
 * JASCIS-239 - Documented the requirement of PyHamCrest for running tests
 * JASCIS-249 - CIS will now accept variables and filenames (such as Windows paths) which include a colon as long as they are escaped with a backslash. E.g. ``cis plot my_var:C\:\my_file.nc``.
 * Occasionally HDF will exit when reading an invalid HDF file without throwing any exceptions. To protect against this the HDF reader will now insist on an .hdf extension for any files it reads.