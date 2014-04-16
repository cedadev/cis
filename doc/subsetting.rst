==========
Subsetting
==========

Subsetting allows the reduction of data by extracting a variable and restricting to ranges of one or more coordinates.

To perform subsetting, run a command of the format::

  $ cis subset datagroup limits -o outputfile

where:

``datagroup``
  is of the format ``variable:filenames[:product]`` in which product is optional. Each is described in more detail below.

    * ``variable`` is a non-optional argument used to specify the variable to use.
    * ``filenames`` is a non-optional argument used to specify the files to read the variable from. These can be specified as a comma seperated list of the following possibilities:

      #. A single filename - this should be the full path to the file
      #. A single directory - all files in this directory will be read
      #. A wildcarded filename - A filename with any wildcards compatible with the python module glob, so that *, ? and [] can all be used. E.g. ``/path/to/my/test*file_[0-9]``.

      Note that when using option (b), the filenames in the directory will be automatically sorted into alphabetical order. When using option (c), the filenames matching the wildcard will also be sorted into alphabetical order.

      The order of the comma separated list will however remain as the user specified, e.g.``filename1,filename2,wildc*rd,/my/dir/,filename3 `` would read filename1, then filename2, then all the files that match "wildc*rd" (in alphabetical order), then all the files in the directory "/my/dir/" (in alphabetical order) and then finally filename3.

    * ``product`` is an optional argument used to specify the type of files being read. If omitted, the program will attempt to figure out which product to use based on the filename. See :ref:`data-products-reading` to see a list of available products and their file signatures. As there is only one optional argument available the ``product=`` keyword, as used elsewhere, is optional.

``limits``
  is a comma separated sequence of one or more coordinate range assignments of the form ``variable=[start,end]`` or ``variable=[value]`` in which

    * ``variable`` is the name of the variable to be subsetted, or one of x, y, z or t, which refer to longitude, latitude, altitude or time, respectively.
    * ``start`` is the value at the start of the coordinate range to be included
    * ``end`` is the value at the end of the coordinate range to be included
    * ``value`` is taken as the start and end value.
    * Date/times are specified in the format: ``YYYY-MM-DDThh:mm:ss`` in which ``YYYY-MM-DD`` is a date and ``hh:mm:ss`` is a time. A colon or space can be used instead of the 'T' separator (but if a space is used, the argument must be quoted). Any trailing components of the date/time may be omitted. When a date/time is used as a range start, the earliest date/time compatible with the supplied components is used (e.g., ``2010-04`` is treated as ``2010-04-01T00:00:00``) and when used as a range end, the latest compatible date/time is used. Including optional and alternative components, the syntax is ``YYYY[-MM[-DD[{T|:| }hh[:mm[:ss]]]]]``. When the ``t=[value]`` form is used, value is interpretted as both the start and end value, as described above, giving a range spanning the specified date/time, e.g., ``t=[2010]`` gives a range spanning the whole of the year 2010.
    * Longitude coordinates are considered to be circular, so that 370 is equivalent to 10. The values are constrained to be within the range 0 to 360 or -180 to 180, depending on the coordinate values found in the file, as follows: If the subset range is already within the range of the coordinate no change is made. If the range of values for the coordinate in the file is such that 180 <= coord_min < 0 and coord_max <= 180.0 the range -180 to 180 is used. Otherwise, if 0 <= coord_min and coord_max <= 360, the range 0 to 360 is used.
    * Other coordinates ranges are interpreted so that the subset includes values for which the coordinate value is greater than the smaller of start and end, and less than the larger of start and end (so the order in which start and end are specified is not significant).

``outputfile``
  is an optional argument to specify the name to use for the file output. This is automatically given a ``.nc` extension and prepended with ``cis-`, if it contains ungridded data, to make it distinguishable as a colocated file. The default filename is ``cis-out.nc`` for ungridded data, and ``out.nc`` for gridded data.

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
  $ cis plot solar_3:cis-Xglnwa_vprof-out.nc

  $ cis subset solar_3:xglnwa.pm.k8dec-k9nov.col.tm.nc x=[0,180],y=[0,90] -o Xglnwa-out
  $ cis plot solar_3:cis-Xglnwa-out.nc

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

