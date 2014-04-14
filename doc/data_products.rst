====================================
What kind of data can CIS deal with?
====================================

Writing
=======

When creating files (from co-located data) CIS uses the NetCDF 4 classic format. Ungridded output files are always prefixed with ``cis-``, and both ungridded and gridded output are always suffixed with ``.nc``.

.. _data-products-reading:

Reading
=======

CIS has built-in support for NetCDF and HDF4 file formats. That said, most data requires some sort of pre-processing before being ready to be plotted or analysed (this could be scale factors or offsets needing to applied, or even just knowing what the dependencies between variables are). For that reason, the way CIS deals with reading in data files is via the concept of "data products". Each product has its own very specific way of reading and massaging the data in order for it to be ready to be plotted, analysed, etc.

So far, CIS can read the following ungridded data files:

  ================ ====================== ================= ======================================================================================================== 
  Dataset          Product name           Type              File Signature                                                                                          
  ================ ====================== ================= ======================================================================================================== 
  AERONET          Aeronet                Ground-stations   \*.lev20                                                                                                
  Aerosol CCI      Aerosol_CCI            Satellite         \*ESACCI*AEROSOL*          
  CALIOP L1        Caliop_L1              Satellite         CAL_LID_L1-ValStage1-V3*.hdf                                                                                                                                                
  CALIOP L2        Caliop_L2              Satellite         CAL_LID_L2_05kmAPro-Prov-V3*.hdf                                                                     
  CloudSAT         Cloudsat_2B_CWC_RVOD   Satellite         \*2B.CWC.RVOD*.hdf                                                                                     
  Flight campaigns NCAR_NetCDF_RAF        Aircraft          RF*.nc                                                                                                
  MODIS L2         MODIS_L2               Satellite         \*MYD06_L2*.hdf, \*MOD06_L2*.hdf, \*MYD04_L2*.hdf, \*MOD04_L2*.hdf, \*MYDATML2.*.hdf, \*MODATML2*.hdf
  Cloud CCI        Cloud_CCI              Satellite         \*ESACCI*CLOUD*                                                                                       
  CSV datapoints   ASCII_Hyperpoints      N/A               \*.txt                                                                                                  
  CIS ungridded    cis                    CIS output        cis-\*.nc       
  ================ ====================== ================= ======================================================================================================== 


It can also read the following gridded data types:

  ==================== =========================== ================== =================================================================================
  Dataset              Product name                Type               File Signature                                      
  ==================== =========================== ================== =================================================================================
  MODIS L3 daily       MODIS_L3                    Satellite          \*MYD08_D3*.hdf, \*MOD08_D3*.hdf, \*MOD08_E3*.hdf  
  Net_CDF Gridded Data NetCDFGridded               Gridded Model Data \*.nc (this is the default for NetCDF Files that do not match any other signature)
  ==================== =========================== ================== =================================================================================


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

 =================== ================= ================== ======================== 
  **samplegroup**     **datagroup**     **outputfile**                             
 =================== ================= ================== ======================== 
  gridded             gridded           gridded            ''implemented''     
  gridded             ungridded         gridded            ''implemented''  
  ungridded           ungridded         ungridded          ''implemented''         
  ungridded           gridded           ungridded          ''implemented''         
 =================== ================= ================== ======================== 

