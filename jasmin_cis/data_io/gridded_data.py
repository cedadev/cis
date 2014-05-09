from time import gmtime, strftime
import logging

import iris
import numpy as np

from jasmin_cis.data_io.common_data import CommonData
from jasmin_cis.data_io.hyperpoint import HyperPoint
from jasmin_cis.data_io.hyperpoint_view import GriddedHyperPointView

from iris.std_names import STD_NAMES
from jasmin_cis.utils import remove_file_prefix


def load_cube(*args, **kwargs):
    iris_cube = iris.load_cube(*args, **kwargs)
    return make_from_cube(iris_cube)


def make_from_cube(cube):
    if cube is None:
        gd = None
    else:
        gd = cube
        gd.__class__ = GriddedData
    return gd


class GriddedData(iris.cube.Cube, CommonData):
    def __init__(self, *args, **kwargs):

        try:
            standard_name = kwargs['standard_name']
            try:
                iris.std_names.STD_NAMES[standard_name]
            except KeyError:
                rejected_name = kwargs.pop('standard_name')
                logging.warning("Attempted to set invalid standard_name '{}'.".format(rejected_name))
        except KeyError:
            pass

        try:
            super(GriddedData, self).__init__(*args, **kwargs)
        except ValueError:
            rejected_unit = kwargs.pop('units')
            logging.warning("Attempted to set invalid unit '{}'.".format(rejected_unit))
            super(GriddedData, self).__init__(*args, **kwargs)

    @staticmethod
    def _wrap_cube_iterator(itr):
        """Makes a generator that returns a GriddedData object from each Cube returned by an iterator.
        :param itr: iterator over Cubes
        :return: yields GriddedData objects created from Cubes
        """
        for c in itr:
            yield make_from_cube(c)

    def slices(self, *args, **kwargs):
        return self._wrap_cube_iterator(super(GriddedData, self).slices(*args, **kwargs))

    def get_coordinates_points(self):
        """Returns a HyperPointView of the points.
        :return: HyperPointView of all the data points
        """
        all_coords = [((c[0].points, c[1]) if c is not None else None) for c in self.find_standard_coords()]
        return GriddedHyperPointView(all_coords, self.data)

    def get_all_points(self):
        """Returns a HyperPointView of the points.
        :return: HyperPointView of all the data points
        """
        all_coords = [((c[0].points, c[1]) if c is not None else None) for c in self.find_standard_coords()]
        return GriddedHyperPointView(all_coords, self.data)

    def get_non_masked_points(self):
        """Returns a HyperPointView of the points.
        :return: HyperPointView of all the data points
        """
        all_coords = [((c[0].points, c[1]) if c is not None else None) for c in self.find_standard_coords()]
        return GriddedHyperPointView(all_coords, self.data, non_masked_iteration=True)

    def find_standard_coords(self):
        """Constructs a list of the standard coordinates.
        The standard coordinates are latitude, longitude, altitude, air_pressure and time; they occur in the return
        list in this order.
        :return: list of coordinates or None if coordinate not present
        """
        ret_list = []

        coords = self.coords(dim_coords=True)
        for name in HyperPoint.standard_names:
            coord_and_dim = None
            for idx, coord in enumerate(coords):
                if coord.standard_name == name:
                    coord_and_dim = (coord, idx)
                    break
            ret_list.append(coord_and_dim)

        return ret_list

    def add_history(self, new_history):
        """Appends to, or creates, the history attribute using the supplied history string.

        The new entry is prefixed with a timestamp.
        :param new_history: history string
        """
        timestamp = strftime("%Y-%m-%dT%H:%M:%SZ ", gmtime())
        if 'history' not in self.attributes:
            self.attributes['history'] = timestamp + new_history
        else:
            self.attributes['history'] += '\n' + timestamp + new_history

    def name(self):
        return self.var_name

    @property
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        return True

    def set_longitude_range(self, range_start):
        """Rotates the longitude coordinate array and changes its values by
        360 as necessary to force the values to be within a 360 range starting
        at the specified value, i.e.,
        range_start <= longitude < range_start + 360

        The data array is rotated correspondingly around the dimension
        corresponding to the longitude coordinate.

        :param range_start: starting value of required longitude range
        """
        lon_coord = self.coords(standard_name="longitude")
        if len(lon_coord) == 0:
            return
        lon_coord = lon_coord[0]
        lon_idx = self.dim_coords.index(lon_coord)
        idx1 = np.searchsorted(lon_coord.points, range_start)
        idx2 = np.searchsorted(lon_coord.points, range_start + 360.)
        shift = 0
        new_lon_points = None
        if 0 < idx1 < len(lon_coord.points):
            shift = -idx1
            lon_min = lon_coord.points[idx1]
            new_lon_points = np.roll(lon_coord.points, shift, 0)
            new_lon_points[new_lon_points < lon_min] += 360.0
        elif 0 < idx2 < len(lon_coord.points):
            shift = len(lon_coord.points) - idx2
            lon_max = lon_coord.points[idx2]
            new_lon_points = np.roll(lon_coord.points, shift, 0)
            new_lon_points[new_lon_points >= lon_max] -= 360.0
        if shift != 0:
            new_data = np.roll(self.data, shift, lon_idx)
            self.data = new_data
            self.dim_coords[lon_idx].points = new_lon_points

    def save_data(self, output_file, _sample_points=None, _coords_to_be_written=False):
        output_file = remove_file_prefix('cis-', output_file)
        logging.info('Saving data to %s' % output_file)
        iris.save(self, output_file)
