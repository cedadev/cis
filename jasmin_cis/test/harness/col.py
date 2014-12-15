__author__ = 'duncan'
# import re
#
# print re.match(r'.*xenida.*\.nc','/home/duncan/xenida.pah9450.nc')
# print re.match(r'.*2B.CWC.RVOD*','2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')
#
# print re.match(r'.*2B.CWC.RVOD*','/home/duncan/2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')
# print re.match(r'.*\.nc','/home/duncan/2007180125457_06221_CS_2B-CWC-RVOD_GRANULE_P_R04_E02.hdf')
#
# print re.match(r'.*ESACCI.*', "/home/daniel/CCI_Files/20080612093821-ESACCI-L2P_AEROSOL-ALL-AATSR_ENVISAT-ORAC_32855-fv02.02.nc")
#
# import iris
# variable = 'mass_fraction_of_cloud_liquid_water_in_air'
# filename = '/home/duncan/xenida.pah9470.nc'
#
# var_constraint = iris.AttributeConstraint(name=variable)
# # Create an Attribute constraint on the name Attribute for the variable given
#
# cubes = iris.load(filename, variable)
# for cube in cubes:
#     print cube
#
# print cubes.extract(var_constraint)

#cube = iris.load_cube(filename, var_constraint)
#print cube
#
# try:
#     cube = iris.load_cube(filename, var_constraint)
# except iris.exceptions.ConstraintMismatchError:
#     raise InvalidVariableError("Variable not found: " + variable +
#                                "\nTo see a list of variables run: cis info " + filenames[0] + " -h")

import timeit

from jasmin_cis.test.unit.colocate.test_kernel import TestNNGridded


tc = TestNNGridded()

t = timeit.Timer(tc.test_basic_col_gridded_to_ungridded_in_2d_with_time)

print t.timeit(100)