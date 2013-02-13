__author__ = 'duncan'
import re

print re.match(r'.*xenida.*\.nc','/home/duncan/xenida.pah9450.nc')
print re.match(r'.*2B.CWC.RVOD*','2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')

print re.match(r'.*2B.CWC.RVOD*','/home/duncan/2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')
print re.match(r'.*\.nc','/home/duncan/2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')

print re.match(r'.*ESACCI.*', "/home/daniel/CCI_Files/20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc")

