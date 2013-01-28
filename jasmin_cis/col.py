'''
    Colocation routines - to be implemented
'''
import numpy as np
from collections import namedtuple
R_E = 6378

HyperPointT = namedtuple('HyperPoint',['lat','lon','alt','t','val'])

def HyperPoint(lat=None, lon=None, alt=None, t=None, val=None):
    '''
        Small constructor for the HyperPoint named tuple to allow optional arguments
    '''
    return HyperPointT(lat,lon,alt,t,val)

def compdist(ref_p,p1,p2):
    '''Compares the distance from reference point ref_p to p1 and p2. Returns True if p2 is closer to ref_p than p1'''
    #print (haversine(latp,lonp,lat1,lon1), haversine(latp,lonp,lat2,lon2))
    #if not np.isfinite(haversine(latp,lonp,lat1,lon1)):
    #    return True
    return (haversine(ref_p.lat,ref_p.lon,p1.lat,p1.lon) > haversine(ref_p.lat,ref_p.lon,p2.lat,p2.lon))

def haversine(lat1,lon1,lat2,lon2):
    import math
    '''Computes the Haversine distance between two points'''
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon1 = lon1 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    arclen = 2*math.asin(math.sqrt((math.sin((lat2-lat1)/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin((lon2-lon1)/2))**2))
    return arclen*R_E

def col_nn(points, data):
    '''
        Colocation using nearest neighbours without any constraints.
         This is just a skeleton at the moment - we need to define hoe
         the data will come in
    '''
    pass
    # This doesn't quite work yet - I think we need to create a set of points with the same coordinates
    #  as the sample points but without any values - these are what we're trying to fill in...
#    new_data = np.array(points, np.zeros(points.shape,2))
#    for point in new_data:
#        nearest_point = LatLonPoint(0,0)
#        for data_point in data:
#            if compdist(data_point,nearest_point,point): nearest_point = point
#        point.val = nearest_point.val
    
        
def col_li(points, data):
    pass

def col_nn_wc(points, data):
    pass

colocation_methods = { 'nn' : col_nn, 
                       'li' :col_li,
                       'nn_wc' : col_nn_wc }

def col(points, data, method='nn'):
    from jasmin_cis.exceptions import InvalidColocationMethodError
    try:
        return colocation_methods[method](points,data)
    except KeyError:
        raise InvalidColocationMethodError

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