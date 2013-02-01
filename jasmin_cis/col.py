'''
    Colocation routines - to be implemented
'''
from collections import namedtuple

class Colocator(object):

    def __init__(self, points, data, col_method='nn', constraints=None):
        from jasmin_cis.exceptions import InvalidColocationMethodError
        from iris import cube
        
        self.points = points
        self.data = data
        self.constraints = constraints        
        
        if isinstance(data, cube.Cube):  
            methods = Colocator.gridded_colocation_methods._asdict()
        else:
            methods = Colocator.ungridded_colocation_methods._asdict()
            
        self.method = methods[col_method]
               
        if self.method is None:
            raise InvalidColocationMethodError('This co-location method is invalid for this data type')
                
    def _update_data(self):
        from iris import cube
        from jasmin_cis.data_io.ungridded_data import UngriddedData
        if isinstance(self.points, cube.Cube):
            # Return a cube with those points - TODO
            pass
        else:
            return UngriddedData.from_points_array(self.points)
                
    def colocate(self):
        import numpy as np
        for point in self.points:
            point.val.append(self.method(self, point))
        new_data = self._update_data() 
        new_data.missing_value = np.Infinity
        return new_data
        
    def find_nn_value(self, point):
        '''
            Colocation using nearest neighbours without any constraints where both points and 
              data are a list of HyperPoints
        '''
        nearest_point = point.furthest_point_from()
        for data_point in self.data:
            if point.compdist(nearest_point, data_point): nearest_point = data_point
        return nearest_point.val
    
    def find_nn_value_ungridded(self, point, constraint_fn=None):
        '''
            Co-location routine using nearest neighbour algorithm optimized for ungridded data
        '''
        from jasmin_cis.data_io.hyperpoint import HyperPoint
        import numpy as np
        nearest_point = point.furthest_point_from()
        for (x,y), value in np.ndenumerate(self.data.vals):
            ug_point = HyperPoint(self.data.lat[x,y],self.data.lon[x,y],val=value)
            if point.compdist(nearest_point, ug_point): nearest_point = ug_point
            
        if constraint_fn is not None:
            return constraint_fn(point, nearest_point)
        else:
            return nearest_point.val
    
    def find_nn_value_gridded(self, point):
        '''
            Co-location routine using nearest neighbour algorithm optimized for gridded data.
             This calls out to iris to do the work.
        '''
        from iris.analysis.interpolate import nearest_neighbour_data_value
        return nearest_neighbour_data_value(self.data, point.get_coord_tuple())
    
    def find_value_by_li(self, point):
        pass
    
    ColocationTechniques = namedtuple('Techniques',['nn', 'li'])
    gridded_colocation_methods = ColocationTechniques(find_nn_value_gridded, find_value_by_li)
    ungridded_colocation_methods = ColocationTechniques(find_nn_value_ungridded, None)

