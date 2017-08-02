import logging
import iris


class DataList(iris.cube.CubeList):
    """
    Interface for common list methods implemented for both gridded and ungridded data.

    Note that all objects in a CommonDataList must have the same coordinates and coordinate values.

    This is essentially an xarray Dataset object translated to Iris
    """
    filenames = []

    def __init__(self, iterable=()):
        super(DataList, self).__init__()
        self.extend(iterable)

    def __add__(self, rhs):
        return self.__class__(list.__add__(self, rhs))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            result = self.__class__(result)
        return result

    def __getslice__(self, start, stop):
        result = super(DataList, self).__getslice__(start, stop)
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

        super(DataList, self).append(p_object)
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

    def is_gridded(self, coords):
        """Returns value indicating whether the data/coordinates are gridded.
        """
        from cis.data_io.cube_utils import is_gridded
        return is_gridded(self[0], coords)

    def save_data(self, output_file):
        """
        Save data to a given output file
        :param output_file: File to save to
        """
        logging.info('Saving data to %s' % output_file)
        save_args = {}

        # If we have a time coordinate then use that as the unlimited dimension, otherwise don't have any
        if self.coords('time'):
            save_args['unlimited_dimensions'] = ['time']
        else:
            iris.FUTURE.netcdf_no_unlimited = True

        iris.save(self, output_file, **save_args)

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
        data_list = DataList()
        for data in self:
            data_list.append(data.aggregated_by(*args, **kwargs))
        return data_list

    def collapsed(self, *args, **kwargs):
        """
        Collapse the dataset over one or more coordinates using CIS aggregation (NOT Iris). This allows multidimensional
         coordinates to be aggregated over as well.
        :param list of iris.coords.Coord or str coords: The coords to collapse
        :param str or iris.analysis.Aggregator how: The kernel to use in the aggregation
        :param kwargs: NOT USED - this is only to match the iris interface.
        :return:
        """
        output = DataList()
        for data in self:
            output.extend(data.collapsed(*args, **kwargs))
        return output

    def interpolate(self, *args, **kwargs):
        """
        Perform an interpolation over the GriddedDataList using the iris.cube.Cube.interpolate() method
        :param args: Arguments for the Iris interpolate method
        :param kwargs: Keyword arguments for the Iris interpolate method
        :return: Interpolated GriddedDataList
        """
        output = DataList()
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
        output = DataList()
        for data in self:
            output.append(data.regrid(*args, **kwargs))
        return output

    def intersection(self, *args, **kwargs):
        """
        Call the iris.cube.Cube.intersection() method over all the cubes in a GriddedDataList
        :param args: Arguments for the Iris intersection method
        :param kwargs: Keyword arguments for the Iris intersection method
        :return: Intersected GriddedDataList or None if no data in intersection
        """
        output = DataList()
        for data in self:
            new_data = data.intersection(*args, **kwargs)
            if new_data is None:
                return None
            output.append(data.intersection(*args, **kwargs))
        return output

    def extract(self, *args, **kwargs):
        """
        Call the iris.cube.Cube.extract() method over all the cubes in a GriddedDataList
        :param args: Arguments for the Iris extract method
        :param kwargs: Keyword arguments for the Iris extract method
        :return: Extracted GriddedDataList oR None if all data excluded
        """
        output = DataList()
        for data in self:
            new_data = data.extract(*args, **kwargs)
            if new_data is None:
                return None
            output.append(data.extract(*args, **kwargs))
        return output

    def transpose(self, *args, **kwargs):
        """
        Call the iris.cube.Cube.transpose() method over all the cubes in a GriddedDataList
        :param args: Arguments for the Iris transpose method
        :param kwargs: Keyword arguments for the Iris transpose method
        """
        for data in self:
            data.transpose(*args, **kwargs)

    @property
    def dim_coords(self):
        """
        The dimension coordinates of this data
        """
        # Use the dimensions of the first item since all items should have the same dimensions
        return self[0].dim_coords

    @property
    def aux_coords(self):
        """
        The auxiliary coordinates of this data
        """
        # Use the dimensions of the first item since all items should have the same dimensions
        return self[0].aux_coords

    @property
    def ndim(self):
        """
        The number of dimensions in the data of this list.
        """
        # Use the dimensions of the first item since all items should be the same shape
        return self[0].ndim

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
        from cis.subsetting.subset import subset, GriddedSubsetConstraint
        return subset(self, GriddedSubsetConstraint, **kwargs)
