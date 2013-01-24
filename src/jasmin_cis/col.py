'''
    Colocation routines - to be implemented
'''
import numpy as np

def col(points, data, method):
    pass

def col_nn(points, data):
    pass

def col_li(points, data):
    pass

def col_nn_wc(points, data):
    pass

colocation_methods = { 'nn' : col_nn, 
                       'li' :col_li,
                       'nn_wc' : col_nn_wc }

def is_colocated(data1, data2):
    '''
        Checks wether two datasets share all of the same points, this might be useful
        to determine if colocation is necesary or completed succesfully
    '''
    return np.array_equal(data1.points, data2.points)#
    # Or manually?
#    colocated = True
#    for point1 in data1:
#        colocated = all( point1 == point2 for point2 in data2 )
#        if not colocated:
#            return colocated
#    return colocated