.. _subsetting:
.. include:: <isonum.txt>

==========
Subsetting
==========

Subsetting allows the reduction of data by extracting variables and restricting them to ranges of one or more coordinates.

To perform subsetting, run a command of the format::

  $ cis subset <datagroup> <limits> [-o <outputfile>]

where:

``<datagroup>``
  is a :ref:`CIS datagroup <datagroups>` specifying the variables and files to read and is of the format
  ``<variable>...:<filename>[:product=<productname>]`` where:

    * ``variable`` is a mandatory variable or list of variables to use.
    * ``filenames`` is a mandatory file or list of files to read from.
    * ``product`` is an optional CIS data product to use (see :ref:`Data Products <data-products-reading>`):

  See :ref:`datagroups` for a more detailed explanation of datagroups.

``<limits>``
  is a comma separated sequence of one or more coordinate range assignments of the form ``variable=[start,end]`` or ``variable=[value]`` in which

    * ``variable`` is the name of the variable to be subsetted, or one of x, y, z or t, which refer to longitude, latitude, altitude or time, respectively.
    * ``start`` is the value at the start of the coordinate range to be included
    * ``end`` is the value at the end of the coordinate range to be included
    * ``value`` is taken as the start and end value.

    .. note::
      Longitude coordinates are considered to be circular, so that -10 is equivalent to 350. The start and end must
      describe a monotonically increasing coordinate range, so ``x=[90,-90]`` is invalid, but could be specified
      using ``x=[90,270]``. The range between the start and end must not be greater than 360 degrees. The output
      coordinates will be on the requested grid, not the grid of the source data.

    .. note::
      Date/times are specified in the format: ``YYYY-MM-DDThh:mm:ss`` in which ``YYYY-MM-DD`` is a date and ``hh:mm:ss``
      is a time. A colon or space can be used instead of the 'T' separator (but if a space is used, the argument must be
      quoted). Any trailing components of the date/time may be omitted. When a date/time is used as a range start, the
      earliest date/time compatible with the supplied components is used (e.g., ``2010-04`` is treated as
      ``2010-04-01T00:00:00``) and when used as a range end, the latest compatible date/time is used. Including
      optional and alternative components, the syntax is ``YYYY[-MM[-DD[{T|:| }hh[:mm[:ss]]]]]``. When the
      ``t=[value]`` form is used, value is interpreted as both the start and end value, as described above, giving a
      range spanning the specified date/time, e.g., ``t=[2010]`` gives a range spanning the whole of the year 2010.


``outputfile``
  is an optional argument to specify the name to use for the file output. This is automatically given a ``.nc`` extension and prepended with ``cis-`, if it contains ungridded data, to make it distinguishable as a colocated file. The default filename is ``cis-out.nc`` for ungridded data, and ``out.nc`` for gridded data.

A full example would be::

  $ cis subset solar_3:xglnwa.pm.k8dec-k9nov.col.tm.nc x=[0,180],y=[0,90] -o Xglnwa-solar_3

Gridded netCDF data is output as gridded data, while ungridded and non-netCDF gridded data is output as ungridded data.

Examples
========

Below are examples of subsetting using each of the supported products (together with a command to plot the output)::

  $ cis subset AO2CO2:RF04.20090114.192600_035100.PNI.nc t=[2009-01-14:19:26:00,2009-01-14:19:36:00] -o RF04-AO2CO2-out
  $ cis plot AO2CO2:cis-RF04-AO2CO2-out.nc

  $ cis subset IO_RVOD_ice_water_content:2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf t=[2007-06-29:13:00,2007-06-29:13:30] -o CloudSAT-out
  $ cis plot IO_RVOD_ice_water_content:cis-CloudSAT-out.nc --xaxis=time --yaxis=altitude

  $ cis subset Cloud_Top_Temperature:MYD06_L2.A2011100.1720.051.2011102130126.hdf x=[-50,-40],y=[0,10] -o MODIS_L2-out
  $ cis plot Cloud_Top_Temperature:cis-MODIS_L2-out.nc

  $ cis subset cwp:20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc x=[85,90],y=[-3,3] -o Cloud_CCI-out
  $ cis plot atmosphere_mass_content_of_cloud_liquid_water:cis-Cloud_CCI-out.nc

  $ cis subset AOD870:20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc x=[-5,20],y=[15,25] -o Aerosol_CCI-out
  $ cis plot atmosphere_optical_thickness_due_to_aerosol:cis-Aerosol_CCI-out.nc

  $ cis subset 440675Angstrom:920801_121229_Abracos_Hill.lev20 t=[2002] -o Aeronet-out
  $ cis plot 440675Angstrom:cis-Aeronet-out.nc --xaxis=time --yaxis=440675Angstrom

  $ cis subset solar_3:xglnwa.pm.k8dec-k9nov.vprof.tm.nc y=[0,90] -o Xglnwa_vprof-out
  $ cis plot solar_3:Xglnwa_vprof-out.nc

  $ cis subset solar_3:xglnwa.pm.k8dec-k9nov.col.tm.nc x=[0,180],y=[0,90] -o Xglnwa-out
  $ cis plot solar_3:Xglnwa-out.nc

  $ cis subset Cloud_Top_Temperature_Mean_Mean:MOD08_E3.A2010009.005.2010026072315.hdf x=[0,179.9],y=[0,90] -o MODIS_L3-out
  $ cis plot Cloud_Top_Temperature_Mean_Mean:cis-MODIS_L3-out.nc


The files used above can be found at::

  /group_workspaces/jasmin/cis/jasmin_cis_repo_test_files/
    2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf
    20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc
    20080620072500-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv1.0.nc
    MOD08_E3.A2010009.005.2010026072315.hdf
    MYD06_L2.A2011100.1720.051.2011102130126.hdf
    RF04.20090114.192600_035100.PNI.nc
    xglnwa.pm.k8dec-k9nov.col.tm.nc
    xglnwa.pm.k8dec-k9nov.vprof.tm.nc
  /group_workspaces/jasmin/cis/data/aeoronet/AOT/LEV20/ALL_POINTS/
    920801_121229_Abracos_Hill.lev20

