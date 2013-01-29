'''
Module for finding files
'''
from glob import glob
import numpy as np

def find_satelitte_data(folder,day,year,variable,orbits=None): 
    '''
    Returns a list of filenames from a given folder,
    given a day, year, variable and (optionally) orbits
    for general satellite Level2 data files. 
    '''   
    day = str(day).rjust(3,'0')
    
    if orbits is None:
        filenames = glob(folder + str(year) + '/' + str(day) + '/*')
        filenames = np.sort(filenames)
    else:
        filenames = []
        for orbit in orbits:
            filenames.append(glob(folder + str(year) + '/' + str(day) + '/*_' + str(orbit) + '_*.hdf')[0])
    
    return filenames
