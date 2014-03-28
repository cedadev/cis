====================================
What kind of data can CIS deal with?
====================================

Writing
=======

When creating files (from co-located data) CIS uses the NetCDF 4 classic format.

Reading
=======

CIS has built-in support for NetCDF and HDF4 file formats. That said, most data requires some sort of pre-processing before being ready to be plotted or analysed (this could be scale factors or offsets needing to applied, or even just knowing what the dependencies between variables are). For that reason, the way CIS deals with reading in data files is via the concept of "data products". Each product has its own very specific way of reading and massaging the data in order for it to be ready to be plotted, analysed, etc.

So far, CIS can read the following ungridded data files:

+------------------+----------------------+-----------------+----------------------+--------------------------------------------------------------------------------------------------------+
| Dataset          | Product name         | Type            | Scientific Product   | File Signature                                                                                         |
+------------------+----------------------+-----------------+----------------------+--------------------------------------------------------------------------------------------------------+
| Flight campaigns | NCAR_NetCDF_RAF      | Airplane        | masses               | RF.*\.nc                                                                                               |
| CloudSAT         | Cloudsat_2B_CWC_RVOD | Satellite       | LWP,precip,Z(2,3,3D) | .*2B.CWC.RVOD.*.hdf                                                                                    |
| MODIS L2         | MODIS_L2             | Satellite       | AOT(2D),CTP(2D)      | .*MYD06_L2.*.hdf,.*MOD06_L2.*.hdf,.*MYD04_L2.*.hdf,.*MOD04_L2.*.hdf, .*MYDATML2.*.hdf,.*MODATML2.*.hdf |
| Cloud CCI        | Cloud_CCI            | Satellite       | ?                    | .*ESACCI.*CLOUD.*                                                                                      |
| Aerosol CCI      | Aerosol_CCI          | Satellite       | ?                    | .*ESACCI.*AEROSOL.*                                                                                    |
| CALIOP           | Caliop               | Satellite       | CTT(2D),Beta(3D)     | CAL_LID_L2_05kmAPro-Prov-V3-01.*hdf                                                                    |
| AERONET          | Aeronet              | Ground-stations | AOT(2D)              | .*.lev20                                                                                               |
| (internal)       | CisCol               | N/A             | N/A                  | cis-col-.*.nc                                                                                          |
| csv datapoints   | ASCII_Hyperpoints    | N/A             | N/A                  | .*.txt                                                                                                 |
+------------------+----------------------+-----------------+----------------------+--------------------------------------------------------------------------------------------------------+


It can also read the following gridded data types:

+----------------+--------------+-----------+--------------------+----------------------------------------------------+
| Dataset        | Product name | Type      | Scientific Product | File Signature                                     |
+----------------+--------------+-----------+--------------------+----------------------------------------------------+
| ?              | Xglnwa_vprof | Model     | ?                  | .*xglnwa.*vprof.*.nc                               |
| ?              | Xglnwa       | Model     | ?                  | .*xglnwa.*.nc                                      |
| ?              | Xenida       | Model     | ?                  | .*xenida.*.nc                                      |
| MODIS L3 daily | MODIS_L3     | Satellite | AOT(2D)            | .*MYD08_D3.*.hdf,.*MOD08_D3.*.hdf,.*MOD08_E3.*.hdf |
+----------------+--------------+-----------+--------------------+----------------------------------------------------+


The file signature is used to automatically recognise which product definition to use. Note the product can overridden easily by being specified at the command line.

This is of course far from being an exhaustive list of what's out there. To cope with this, a "plugin" architecture has been designed so that the user can readily use their own data product reading routines, without even having to change the code - see Design Maintenance Guide for more information.

.. todo:: [CommunityIntercomparisonSuite/Design Maintenance Guide]

the plugins are always read first, so one can also overwrite default behaviour if the built-in products listed above do not achieve a very specific purpose.

Example plots
=============

.. image:: img/model.png
   :width: 400px
  
.. image:: img/line.png
   :width: 400px
  
.. image:: img/MODIS_L2.png
   :width: 400px
  
.. image:: img/MODIS_L3.png
   :width: 400px
  
.. image:: img/seviri-ctt.png
   :width: 400px
  
.. image:: img/aerosol_cci.png
   :width: 400px
  
.. image:: img/comparative_scatter_Aeronet.jpg
   :width: 400px
  
.. image:: img/comparativehistogram2d.png
   :width: 400px
  
.. image:: img/agoufou_18022013_all_three.gif
   :width: 400px
  
.. image:: img/cloudcci.png
   :width: 400px
  
.. image:: img/cloudsat_RVOD.png
   :width: 400px
  
.. image:: img/caliop_l1b.png
   :width: 400px
  
.. image:: img/aircraft.png
   :width: 400px


Colocation
==========

+-------------------+-----------------+------------------+------------------------+
| **samplegroup**   | **datagroup**   | **outputfile**   |                        |
+-------------------+-----------------+------------------+------------------------+
| gridded           | gridded         | gridded          | ''not implemented''    |
| gridded           | ungridded       | gridded          | ''not implemented(*)'' |
| ungridded         | ungridded       | ungridded        | ''implemented''        |
| ungridded         | gridded         | ungridded        | ''implemented''        |
+-------------------+-----------------+------------------+------------------------+


(*) Note that a ungridded->gridded is mostly equivalent to a gridded->ungridded co-location 
