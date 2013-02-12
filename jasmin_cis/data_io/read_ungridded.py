'''
Module for reading ungridded data in HDF4 format
'''
import hdf_vd as hdf_vd
import hdf_sd as hdf_sd

def get_file_variables(filename):
    '''
    Get all variables from a file containing ungridded data.
    Concatenate variable from both VD and SD data
    
    args:
        filename: The filename of the file to get the variables from
    
    '''
    SD_vars = hdf_sd.get_hdf_SD_file_variables(filename)
    VD_vars = hdf_vd.get_hdf_VD_file_variables(filename)
    
    return SD_vars, VD_vars


def get_file_coordinates(filename):
    '''
    Read in coordinate variables and pass back tuple of lat, lon,
    each element of tuple being a 2D numpy array
    '''
    lat = hdf_vd.get_data((filename,'Latitude'))
    lon = hdf_vd.get_data((filename,'Longitude'))
    return (lat,lon)


def get_file_coordinates_points(filename):
    '''
    Convert coordinate 2D arrays into a list of points
    useful for co-location sampling
    '''
    from jasmin_cis.data_io.hyperpoint import HyperPoint
    
    latitude, longitude = get_file_coordinates(filename)
    
    points = []    
    
    for i, lat in enumerate(latitude):
        points.append(HyperPoint(lat,longitude[i]))
    
#    for (x,y), lat in np.ndenumerate(latitude):
#        lon = longitude[x,y]
#        points.append(HyperPoint(lat,lon))
        
    return points


def read_data(filenames, variable, product=None):
    '''
    Read ungridded data from a file. Just a wrapper that calls the UngriddedData class method
    
        @param filenames:     A list of files to read
        @param variable:      A variable to read from the files
        
        @return An ungridded data object
        @raise FileIOError: Unable to read a file
        @raise InvalidVariableError: Variable not present in file
    '''
    from data_io.products.AProduct import get_data
    return get_data(filenames, variable, product)


