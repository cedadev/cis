from abc import ABCMeta, abstractmethod


class CommonData(object):
    """
    Interface of common methods implemented for gridded and ungridded data.
    """
    __metaclass__ = ABCMeta

    filenames = []

    _alias = None

    @property
    @abstractmethod
    def history(self):
        """
        Return the associated history of the object

        :return: The history
        :rtype: str
        """
        return None

    @property
    def alias(self):
        """
        Return an alias for the variable name. This is an alternative name by which this data object may be identified
        if, for example, the actual variable name is not valid for some use (such as performing a python evaluation).

        :return: The alias
        :rtype: str
        """
        if self._alias is not None:
            return self._alias
        else:
            return self.var_name

    @alias.setter
    def alias(self, alias):
        """
        Set this data objects alias - this is an alternative name by which this data object may be identified
        if, for example, the actual variable name is not valid for some use (such as performing a python evaluation).

        :param str alias: The alias to use
        """
        self._alias = alias

    @property
    @abstractmethod
    def var_name(self):
        """
        Return the variable name associated with this data object

        :return: The ariable name
        """
        return None

    @abstractmethod
    def get_coordinates_points(self):
        """Returns a list-like object allowing access to the coordinates of all points as HyperPoints.
        The object should allow iteration over points and access to individual points.

        :return: list-like object of data points
        """
        pass

    @abstractmethod
    def get_all_points(self):
        """Returns a list-like object allowing access to all points as HyperPoints.
        The object should allow iteration over points and access to individual points.

        :return: list-like object of data points
        """
        pass

    @abstractmethod
    def get_non_masked_points(self):
        """Returns a list-like object allowing access to all points as HyperPoints.
        The object should allow iteration over non-masked points and access to individual points.

        :return: list-like object of data points
        """
        pass

    @abstractmethod
    def is_gridded(self):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        pass

    @abstractmethod
    def as_data_frame(self, copy):
        """
        Convert a CommonData object to a Pandas DataFrame.

        :param copy: Create a copy of the data for the new DataFrame? Default is True.
        :return: A Pandas DataFrame representing the data and coordinates. Note that this won't include any metadata.
        """
        pass

    @abstractmethod
    def set_longitude_range(self, range_start):
        """
        Rotates the longitude coordinate array and changes its values by
        360 as necessary to force the values to be within a 360 range starting
        at the specified value.
        :param range_start: starting value of required longitude range
        """
        pass


class CommonDataList(list):
    """
    Interface for common list methods implemented for both gridded and ungridded data.

    Note that all objects in a CommonDataList must have the same coordinates and coordinate values.
    """
    __metaclass__ = ABCMeta

    filenames = []

    def __init__(self, iterable=()):
        super(CommonDataList, self).__init__()
        self.extend(iterable)

    @property
    @abstractmethod
    def is_gridded(self):
        """
        Returns value indicating whether the data/coordinates are gridded.
        """
        raise NotImplementedError

    def append(self, p_object):
        """
        Append a compatible object to this list

        :param UngriddedData or GriddedData p_object:
        :return: None
        :raises TypeError: If the objects being added are of the wrong type (i.e. Gridded versus Ungridded).
        :raises ValueError: If the coordinates aren't compatible with each other.
        """
        this_class = self.__class__.__name__
        that_class = p_object.__class__.__name__
        other_gridded = getattr(p_object, 'is_gridded', None)

        if other_gridded is None or other_gridded != self.is_gridded:
            raise TypeError("Appending {that_class} to {this_class} is not allowed".format(
                that_class=that_class, this_class=this_class))

        if len(self) > 0:
            if len(self.coords()) != len(p_object.coords()):
                raise ValueError("Incompatible data: {} must have the same number of coordinates as the first element "
                                 "in this list.".format(that_class))
            for this_coord, that_coord in zip(self.coords(), p_object.coords()):
                if any([(a != b) for a, b in zip(this_coord.points.shape, that_coord.points.shape)]):
                    raise ValueError("Given coordinate {} has shape {} which is "
                                     "incompatible with {}.".format(that_coord.name,
                                                                    that_coord.shape,
                                                                    this_coord.shape))

        super(CommonDataList, self).append(p_object)
        return

    def extend(self, iterable):
        # This will raise a TypeError if the objects being added are of the wrong type (i.e. Gridded versus Ungridded).
        for x in iterable:
            self.append(x)

    def append_or_extend(self, item_to_add):
        """
        Append or extend an item to an existing list, depending on whether the item to add is itself a list or not.
        :param item_to_add: Item to add (may be list or not).
        """
        if isinstance(item_to_add, list):
            self.extend(item_to_add)
        else:
            self.append(item_to_add)

    @property
    def var_name(self):
        """
        Get the variable names in this list
        """
        var_names = []
        for data in self:
            var_names.append(data.var_name)
        return var_names

    @property
    def filenames(self):
        """
        Get the filenames in this data list
        """
        filenames = []
        for data in self:
            filenames.extend(data.filenames)
        return filenames

    def add_history(self, new_history):
        """
        Appends to, or creates, the metadata history attribute using the supplied history string.
        The new entry is prefixed with a timestamp.
        :param new_history: history string
        """
        for data in self:
            data.add_history(new_history)

    def coords(self, *args, **kwargs):
        """
        Returns all coordinates used in all the data object
        :return: A list of coordinates in this data list object fitting the given criteria
        """
        return self[0].coords(*args, **kwargs)

    def set_longitude_range(self, range_start):
        """
        Rotates the longitude coordinate array and changes its values by
        360 as necessary to force the values to be within a 360 range starting
        at the specified value.
        :param range_start: starting value of required longitude range
        """
        for data in self:
            data.set_longitude_range(range_start)
