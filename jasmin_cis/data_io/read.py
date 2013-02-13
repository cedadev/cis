'''
Module for reading data. This is just an abstract layer for making the choice between gridded and ungridded - the actual reading is done elsewhere
'''

def read_data(filenames, variable, product=None):
    '''
    Read a specific variable from a list of files
    Files can be either gridded or ungridded but not a mix of both.
    First tries to read data as gridded, if that fails, tries as ungridded.
    
    @param filenames:   The filenames of the files to read
    @param variable:    The variable to read from the files
        
    @return:  The specified data with unnecessary dimensions removed
    '''
    from data_io.products.AProduct import get_data
    return get_data(filenames, variable, product)


def read_file_coordinates(filenames, product=None):
    '''
    Read the coordinates from a file

    @param filenames:   The filename of the files to read
        
    @return: A CoordList object
    '''
    from data_io.products.AProduct import get_coordinates
    return get_coordinates(filenames, product)

