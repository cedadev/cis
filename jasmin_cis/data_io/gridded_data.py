from time import gmtime, strftime
import logging

import iris
from iris.cube import CubeList
import numpy as np

from jasmin_cis.data_io.common_data import CommonData, CommonDataList
from jasmin_cis.data_io.hyperpoint import HyperPoint
from jasmin_cis.data_io.hyperpoint_view import GriddedHyperPointView

from iris.std_names import STD_NAMES
from jasmin_cis.utils import remove_file_prefix


def load_cube(*args, **kwargs):
    iris_cube = iris.load_cube(*args, **kwargs)
    return make_from_cube(iris_cube)


def make_from_cube(cube):
    gd = None
    if isinstance(cube, iris.cube.Cube):
        gd = cube
        gd.__class__ = GriddedData
    elif isinstance(cube, iris.cube.CubeList):
        gd = cube
        gd.__class__ = GriddedDataList
    return gd


class GriddedData(iris.cube.Cube, CommonData):
    def __init__(self, *args, **kwargs):

        try:
            standard_name = kwargs['standard_name']
            try:
                iris.std_names.STD_NAMES[standard_name]
            except KeyError:
                rejected_name = kwargs.pop('standard_name')
                logging.warning("Standard name '{}' not CF-compliant, this standard name will not be "
                                "used in the output file.".format(rejected_name))
        except KeyError:
            pass

        try:
            super(GriddedData, self).__init__(*args, **kwargs)
        except ValueError:
            rejected_unit = kwargs.pop('units')
            logging.warning("Attempted to set invalid unit '{}'.".format(rejected_unit))
            super(GriddedData, self).__init__(*args, **kwargs)

    def make_new_with_same_coordinates(self, data=None, var_name=None, standard_name=None,
                                       long_name=None, history=None, units=None):
        """
        Create a new, empty GriddedData object with the same coordinates as this one
        :param data: Data to use (if None then defaults to all zeros)
        :param var_name: Variable name
        :param standard_name: Variable CF standard name
        :param long_name: Variable long name
        :param history: Data history string
        :param units: Variable units
        :return: GriddedData instance
        """
        if data is None:
            data = np.zeros(self.shape)
        data = GriddedData(data=data, standard_name=standard_name, long_name=long_name, var_name=var_name,
                           units=units, dim_coords_and_dims=self._dim_coords_and_dims,
                           aux_coords_and_dims=self._aux_coords_and_dims, aux_factories=self._aux_factories)
        # Add history separately as it is not a constructor argument
        data.add_history(history)
        return data

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

    @property
    def history(self):
        """
        Return the history attribute
        :return:
        """
        return self.attributes['history']

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

    def save_data(self, output_file):
        """
        Save this data object to a given output file
        :param output_file: Output file to save to.
        """
        logging.info('Saving data to %s' % output_file)
        iris.save(self, output_file)


class GriddedDataList(iris.cube.CubeList, CommonDataList):
    """
    This class extends iris.cube.CubeList to add functionality needed for CIS to process multiple gridded data.

    It is expected that it will contain jasmin.cis.data_io.gridded_data.GriddedData instances (which extend
    iris.cube.Cube) rather than IRIS cubes themselves, as there is additional functionality required which is
    present in the GriddedData wrapper.
    """

    def __str__(self):
        "<GriddedDataList: %s>" % super(GriddedDataList, self).__str__()

    @property
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        return True

    def append(self, p_object):
        if isinstance(p_object, iris.cube.Cube):
            p_object = make_from_cube(p_object)
        super(GriddedDataList, self).append(p_object)

    def extend(self, iterable):
        if isinstance(iterable, iris.cube.CubeList):
            iterable = make_from_cube(iterable)
        super(GriddedDataList, self).extend(iterable)

    def save_data(self, output_file):
        """
        Save data to a given output file
        :param output_file: File to save to
        """
        logging.info('Saving data to %s' % output_file)
        iris.save(self, output_file)

    def coord(self, *args, **kwargs):
        """
        Call iris.cube.Cube.coord(*args, **kwargs) for the first item of data (assumes all data in list has
        same coordinates)
        :param args:
        :param kwargs:
        :return:
        """
        return self[0].coord(*args, **kwargs)

    def add_aux_coord(self, *args, **kwargs):
        """
        Call iris.cube.Cube.add_aux_coord(*args, **kwargs) for the all items in the data list
        :param args:
        :param kwargs:
        :return:
        """
        for var in self:
            var.add_aux_coord(*args, **kwargs)

    def coord_dims(self, *args, **kwargs):
        """
        Call iris.cube.Cube.coord_dims(*args, **kwargs) for the first item of data (assumes all data in list has
        same coordinates)
        :param args:
        :param kwargs:
        :return:
        """
        return self[0].coord_dims(*args, **kwargs)

    def remove_coord(self, *args, **kwargs):
        """
        Call iris.cube.Cube.remove_coord(*args, **kwargs) for the all items in the data list
        :param args:
        :param kwargs:
        :return:
        """
        for var in self:
            var.remove_coord(*args, **kwargs)

    def add_dim_coord(self, *args, **kwargs):
        """
        Call iris.cube.Cube.add_dim_coord(*args, **kwargs) for the all items in the data list
        :param args:
        :param kwargs:
        :return:
        """
        for var in self:
            var.add_dim_coord(*args, **kwargs)

    def aggregated_by(self, *args, **kwargs):
        """
        Build an aggregated GriddedDataList by calling iris.cube.Cube.aggregated_by(*args, **kwargs)
        for the all items in the data list
        :param args:
        :param kwargs:
        :return: GriddedDataList
        """
        data_list = GriddedDataList()
        for data in self:
            data_list.append(data.aggregated_by(*args, **kwargs))
        return data_list

    def collapsed(self, *args, **kwargs):
        """
        Build a collapsed GriddedDataList by calling iris.cube.Cube.collapsed(*args, **kwargs)
        for the all items in the data list
        :param args:
        :param kwargs:
        :return: GriddedDataList
        """
        data_list = GriddedDataList()
        for data in self:
            collapsed_data = make_from_cube(data.collapsed(*args, **kwargs))
            data_list.append(collapsed_data)
        return data_list

    def interpolate(self, *args, **kwargs):
        """
        Perform an interpolation over the GriddedDataList using the iris.cube.Cube.interpolate() method
        :param args: Arguments for the Iris interpolate method
        :param kwargs: Keyword arguments for the Iris interpolate method
        :return: Interpolated GriddedDataList
        """
        output = GriddedDataList()
        for data in self:
            output.append(data.interpolate(*args, **kwargs))
        return output

    def regrid(self, *args, **kwargs):
        """
        Perform a regrid over the GriddedDataList using the iris.cube.Cube.regrid() method
        :param args: Arguments for the Iris regrid method
        :param kwargs: Keyword arguments for the Iris regrid method
        :return: Regridded GriddedDataList
        """
        output = CubeList()
        for data in self:
            output.append(data.regrid(*args, **kwargs))
        return output

    @property
    def ndim(self):
        """
        The number of dimensions in the data of this list.
        """
        # Use the dimensions of the first item since all items should be the same shape
        return self[0].ndim