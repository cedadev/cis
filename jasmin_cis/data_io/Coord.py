from ungridded_data import LazyData

class Coord(LazyData):

    def __init__(self, data, metadata, axis=''):
        """

        @param data:
        @param metadata:
        @param axis: A string label for the axis, e.g. 'X', 'Y', 'Z', or 'T'
        @return:
        """
        super(Coord, self).__init__(data, metadata)
        self.axis = axis.upper()

    def __eq__(self, other):
        return other.standard_name == self.standard_name and self.standard_name != ''

class CoordList(list):
    """All the functionality of a standard `list` with added "Coord" context."""

    def __new__(cls, list_of_coords=None):
        """
        Given a `list` of Coords, return a CoordList instance.

        """
        coord_list = list.__new__(cls, list_of_coords)

        # Check that all items in the incoming list are coords. Note that this checking
        # does not guarantee that a CoordList instance *always* has just cubes in its list as
        # the append & __getitem__ methods have not been overridden.
        if not all([isinstance(coord, Coord) for coord in coord_list]):
            raise ValueError('All items in list_of_coords must be Coord instances.')
        return coord_list

    def append(self, other):
        """
            Safely add a new coordinate object to the list, this checks for a unique axis and standard_name
        @param other: Other coord to add
        @raise: DuplicateCoordinateError
        @return:
        """
        from jasmin_cis.exceptions import DuplicateCoordinateError
        if any([ other == item for item in self ]):
            raise DuplicateCoordinateError()
        super(CoordList, self).append(other)

    def get_coords(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a list of coordinates in this UngriddedData object fitting the given criteria. This is deliberately very
         similar to Cube.coords() to maintain a similar interface and because the functionality is similar. There
          is no distrinction between dimension coordinates and auxilliary coordinates here though.

        @param name:  The standard name or long name or default name of the desired coordinate.
            If None, does not check for name. Also see, :attr:`Cube.name`.
        @param standard_name: The CF standard name of the desired coordinate. If None, does not check for standard name.
        @param long_name: An unconstrained description of the coordinate. If None, does not check for long_name.
        @param attributes: A dictionary of attributes desired on the coordinates. If None, does not check for attributes.
        @param axis: The desired coordinate axis, see :func:`iris.util.guess_coord_axis`. If None, does not check for axis.
            Accepts the values 'X', 'Y', 'Z' and 'T' (case-insensitive).

        @return: A list of coordinates in this UngriddedData object fitting the given criteria
        """
        from collections import Mapping
        coords = self

        if name is not None:
            coords = filter(lambda coord_: coord_.name() == name, coords)

        if standard_name is not None:
            coords = filter(lambda coord_: coord_.standard_name == standard_name, coords)

        if long_name is not None:
            coords = filter(lambda coord_: coord_.long_name == long_name, coords)

        if axis is not None:
            axis = axis.upper()
            coords = filter(lambda coord_: coord_.axis == axis, coords)

        if attributes is not None:
            if not isinstance(attributes, Mapping):
                raise ValueError('The attributes keyword was expecting a dictionary type, but got a %s instead.' % type(attributes))
            filter_func = lambda coord_: all(k in coord_.attributes and coord_.attributes[k] == v for k, v in attributes.iteritems())
            coords = filter(filter_func, coords)

        return coords

    def get_coord(self, name=None, standard_name=None, long_name=None, attributes=None, axis=None):
        """
        Return a single coord given the same arguments as L(coords). If the arguments given do not result in precisely
         1 coordinate being matched, a CoordinateNotFoundError is raised.

        @raise: CoordinateNotFoundError
        @return: A single coord given the same arguments as L(coords).

        """
        from jasmin_cis.exceptions import CoordinateNotFoundError
        coords = self.get_coords(name=name, standard_name=standard_name, long_name=long_name, attributes=attributes, axis=axis)

        if len(coords) > 1:
            msg = 'Expected to find exactly 1 coordinate, but found %s. They were: %s.'\
                  % (len(coords), ', '.join(coord.name() for coord in coords))
            raise CoordinateNotFoundError(msg)
        elif len(coords) == 0:
            bad_name = name or standard_name or long_name or ''
            msg = 'Expected to find exactly 1 %s coordinate, but found none.' % bad_name
            raise CoordinateNotFoundError(msg)

        return coords[0]

