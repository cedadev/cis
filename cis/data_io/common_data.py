from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class CommonData(object):
    """
    Interface of common methods implemented for gridded and ungridded data.
    """
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

        :return: The variable name
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

    @abstractmethod
    def subset(self, **kwargs):
        """
        Subset the CommonData object based on the specified constraints. Constraints on arbitrary coordinates are
        specified using keyword arguments. Each constraint must have two entries (a maximum and a minimum) although
        one of these can be None. Datetime objects can be used to specify upper and lower datetime limits, or a
        single PartialDateTime object can be used to specify a datetime range.

        The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
        axis and var_name.

        For example:
            data.subset(time=[datetime.datetime(1984, 8, 28), datetime.datetime(1984, 8, 29)],
                             altitude=[45.0, 75.0])

        Will subset the data from the start of the 28th of August 1984, to the end of the 29th, and between altitudes of
        45 and 75 (in whatever units ares used for that Coordinate).

        And:
            data.subset(time=[PartialDateTime(1984, 9)])

        Will subset the data to all of September 1984.

        :param kwargs: The constraint arguments
        :return CommonData: The subset of the data
        """
        pass

    @abstractmethod
    def sampled_from(self, data, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                     var_name='', var_long_name='', var_units='', **kwargs):
        """
        Collocate the CommonData object with another CommonData object using the specified collocator and kernel

        :param CommonData or CommonDataList data: The data to resample
        :param str how: Collocation method (e.g. lin, nn, bin or box)
        :param str or cis.collocation.col_framework.Kernel kernel:
        :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
        :param float fill_value: Value to use for missing data
        :param str var_name: The output variable name
        :param str var_long_name: The output variable's long name
        :param str var_units: The output variable's units
        :param kwargs: Constraint arguments such as h_sep, a_sep, etc.
        :return CommonData: The collocated dataset
        """
        pass

    def collocated_onto(self, sample, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                        var_name='', var_long_name='', var_units='', **kwargs):
        """
        Collocate the CommonData object with another CommonData object using the specified collocator and kernel.

        :param CommonData sample: The sample data to collocate onto
        :param str how: Collocation method (e.g. lin, nn, bin or box)
        :param str or cis.collocation.col_framework.Kernel kernel:
        :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
        :param float fill_value: Value to use for missing data
        :param str var_name: The output variable name
        :param str var_long_name: The output variable's long name
        :param str var_units: The output variable's units
        :param kwargs: Constraint arguments such as h_sep, a_sep, etc.
        :return CommonData: The collocated dataset
        """
        return sample.sampled_from(self, how=how, kernel=kernel,
                                   missing_data_for_missing_sample=missing_data_for_missing_sample,
                                   fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                   var_units=var_units, **kwargs)

    def plot(self, *args, **kwargs):
        """
        Plot the data. A matplotlib Axes is created if none is provided.

        The default method for series data is 'line', otherwise (for e.g. a map plot) is 'scatter2d' for UngriddedData
        and 'heatmap' for GriddedData.

        :param string how: The method to use, one of:  "contour", "contourf", "heatmap", "line", "scatter", "scatter2d",
        "comparativescatter", "histogram", "histogram2d" or "taylor"
        :param Axes ax: A matplotlib axes on which to draw the plot
        :param Coord or CommonData xaxis: The data to plot on the x axis
        :param Coord or CommonData yaxis: The data to plot on the y axis
        :param string or cartopy.crs.Projection projection: The projection to use for map plots (default is PlateCaree)
        :param float central_longitude: The central longitude to use for PlateCaree (if no other projection specified)
        :param string label: A label for the data. This is used for the title, colorbar or legend depending on plot type
        :param args: Other plot-specific args
        :param kwargs: Other plot-specific kwargs
        :return Axes: The matplotlib Axes on which the plot was drawn
        """
        from cis.plotting.plot import basic_plot
        _, ax = basic_plot(self, *args, **kwargs)
        return ax

    @abstractmethod
    def _get_default_plot_type(self, lat_lon=False):
        pass

    def _get_coord(self, name):
        from cis.utils import standard_axes
        def _try_coord(data, coord_dict):
            import cis.exceptions as cis_ex
            import iris.exceptions as iris_ex
            try:
                coord = data.coord(**coord_dict)
            except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
                coord = None
            return coord

        coord = _try_coord(self, dict(name_or_coord=name)) or _try_coord(self, dict(standard_name=name)) \
            or _try_coord(self, dict(standard_name=standard_axes.get(name.upper(), None))) or \
                _try_coord(self, dict(var_name=name)) or _try_coord(self, dict(axis=name))

        return coord


@six.add_metaclass(ABCMeta)
class CommonDataList(list):
    """
    Interface for common list methods implemented for both gridded and ungridded data.

    Note that all objects in a CommonDataList must have the same coordinates and coordinate values.
    """

    def __init__(self, iterable=()):
        super(CommonDataList, self).__init__()
        self.extend(iterable)

    def __add__(self, rhs):
        return self.__class__(list.__add__(self, rhs))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            result = self.__class__(result)
        return result

    def __getslice__(self, start, stop):
        result = super(CommonDataList, self).__getslice__(start, stop)
        result = self.__class__(result)
        return result

    def __str__(self):
        """Runs short :meth:`CommonData.summary` on every item and the coords"""
        result = ['%s: %s' % (i, item.summary(shorten=True)) for i, item in enumerate(self)]
        if result:
            result = ''.join(result)
            result += 'Coordinates: \n'
            for c in self.coords():
                result += '{pad:{width}}{name}\n'.format(pad=' ', width=2, name=c.name())
        else:
            result = '< Empty list >'
        return result

    def __repr__(self):
        """Runs repr on every cube."""
        return '[%s]' % ',\n'.join([repr(item) for item in self])

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
                                     "incompatible with {}.".format(that_coord.name(),
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

    @filenames.setter
    def filenames(self, names):
        """
        Add these filenames to this data list
        """
        for data in self:
            data.filenames.extend(names)

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

    @abstractmethod
    def subset(self, **kwargs):
        """
        Subset the CommonDataList object based on the specified constraints. Constraints on arbitrary coordinates are
        specified using keyword arguments. Each constraint must have two entries (a maximum and a minimum) although
        one of these can be None. Datetime objects can be used to specify upper and lower datetime limits, or a
        single PartialDateTime object can be used to specify a datetime range.

        The keyword keys are used to find the relevant coordinate, they are looked for in order of name, standard_name,
        axis and var_name.

        For example:
            data.subset(time=[datetime.datetime(1984, 8, 28), datetime.datetime(1984, 8, 29)],
                             altitude=[45.0, 75.0])

        Will subset the data from the start of the 28th of August 1984, to the end of the 29th, and between altitudes of
        45 and 75 (in whatever units ares used for that Coordinate).

        And:
            data.subset(time=[PartialDateTime(1984, 9)])

        Will subset the data to all of September 1984.

        :param kwargs: The constraint arguments
        :return CommonDataList: The subset of each of the data
        """
        pass

    def collocated_onto(self, sample, how='', kernel=None, missing_data_for_missing_sample=True, fill_value=None,
                        var_name='', var_long_name='', var_units='', **kwargs):
        """
        Collocate the CommonData object with another CommonData object using the specified collocator and kernel.

        :param CommonData sample: The sample data to collocate onto
        :param str how: Collocation method (e.g. lin, nn, bin or box)
        :param str or cis.collocation.col_framework.Kernel kernel:
        :param bool missing_data_for_missing_sample: Should missing values in sample data be ignored for collocation?
        :param float fill_value: Value to use for missing data
        :param str var_name: The output variable name
        :param str var_long_name: The output variable's long name
        :param str var_units: The output variable's units
        :param kwargs: Constraint arguments such as h_sep, a_sep, etc.
        :return CommonData: The collocated dataset
        """
        return sample.sampled_from(self, how=how, kernel=kernel,
                                   missing_data_for_missing_sample=missing_data_for_missing_sample,
                                   fill_value=fill_value, var_name=var_name, var_long_name=var_long_name,
                                   var_units=var_units, **kwargs)

    def plot(self, *args, **kwargs):
        """
        Plot the data. A matplotlib Axes is created if none is provided.

        The default method for series data is 'line', otherwise (for e.g. a map plot) is 'scatter2d' for UngriddedData
        and 'heatmap' for GriddedData.

        :param string how: The method to use, one of:  "contour", "contourf", "heatmap", "line", "scatter", "scatter2d",
        "comparativescatter", "histogram", "histogram2d" or "taylor"
        :param Axes ax: A matplotlib axes on which to draw the plot
        :param Coord or CommonData xaxis: The data to plot on the x axis
        :param Coord or CommonData yaxis: The data to plot on the y axis
        :param list layer_opts: A list of keyword dictionaries to pass to each layer of the plot.
        :param args: Other plot-specific args to pass to all plots
        :param kwargs: Other plot-specific kwargs to pass to all plots
        :return Axes: The matplotlib Axes on which the plot was drawn
        """
        from cis.plotting.plot import multilayer_plot
        _, ax = multilayer_plot(self, *args, **kwargs)
        return ax

    def _get_coord(self, *args):
        return self[0]._get_coord(*args)
