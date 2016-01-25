import logging

import numpy as np
from matplotlib.ticker import MaxNLocator, AutoMinorLocator

from cis.exceptions import CISError
from cis.utils import find_longitude_wrap_start
from cis.plotting.formatter import LogFormatterMathtextSpecial


class Generic_Plot(object):
    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    # TODO: Remove the plot_args argument let python figure out which kwargs are named here, and which end up in
    # mplkwargs
    # TODO: Reorder these into roughly the order they are most commonly used
    def __init__(self, ax, packed_data_items, plot_args, calculate_min_and_max_values=True, datagroup=0,
                 datagroups=None, nocolourbar=False, logx=False, logy=False, logv=False, xmin=None,
                 xmax=None, xstep=None, ymin=None, ymax=None, ystep=None, vmin=None, vmax=None, vstep=None,
                 cbarorient='horizontal', grid=False, xlabel=None, ylabel=None, cbarlabel=None, title=None, fontsize=None,
                 itemwidth=1, xtikangle=None, ytickangle=None, xbinwidth=None, ybinwidth=None, coastlinecolour='k',
                 nasabluemarble=False, xaxis=None, yaxis=None, plotwidth=None, plotheight=None, cbarscale=None,
                 *mplargs, **mplkwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param calculate_min_and_max_values: If true calculates min and max for the data values
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """

        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        # TODO: The nocolorbar defaults to False, but wouldn't it be simpler to have a colorbar property?

        # Why does this need to know this - it should only get one datagroup surely?
        self.datagroup = datagroup

        self.color_axis = []

        if plot_args["logv"]:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        self.plot_args = plot_args
        self.packed_data_items = packed_data_items

        self.assign_variables_to_x_and_y_axis()

        logging.debug("Unpacking the data items")
        user_x_min = self.plot_args['xmin']
        self.set_x_wrap_start(user_x_min)
        self.offset_longitude = user_x_min != self.x_wrap_start
        self.unpacked_data_items = self.unpack_data_items()

        if calculate_min_and_max_values:
            self.calculate_min_and_max_values()

        self.matplotlib = ax

        if self.is_map():
            self.setup_map()
            self.check_data_is_2d()

        self.plot()

    def check_data_is_2d(self):
        if len(self.packed_data_items[0].shape) > 2:
            raise CISError("Data is not 1D or 2D - can't plot it on a map.")

    def set_x_wrap_start(self, user_xmin):

        # FIND THE WRAP START OF THE DATA
        data_wrap_start = find_longitude_wrap_start(self.plot_args["x_variable"], self.packed_data_items)

        # NOW find the wrap start of the user specified range
        if user_xmin is not None:
            self.x_wrap_start = -180 if user_xmin < 0 else 0
        else:
            self.x_wrap_start = data_wrap_start

    def setup_map(self):
        import cartopy.crs as ccrs

        # The projection of the data gets offset
        self.projection = ccrs.PlateCarree(central_longitude=(self.x_wrap_start + 180.0))
        # But not the transform...
        self.transform = ccrs.PlateCarree()
        self.cartopy_axis = self.matplotlib.axes(projection=self.projection)
        self.mplkwargs['transform'] = self.transform

    def get_data_items_max(self):
        import numpy as np
        data_max = np.nanmax(self.unpacked_data_items[0]['x'])
        for i in self.unpacked_data_items:
            data_max = max([np.nanmax(i["x"]), data_max])
        return data_max

    def unpack_data_items(self):
        def __get_data(axis):
            variable = self.plot_args[axis + "_variable"]
            if variable == "default" or variable == self.packed_data_items[0].name() \
                    or variable == self.packed_data_items[0].standard_name \
                    or variable == self.packed_data_items[0].long_name:
                return self.packed_data_items[0].data
            else:
                if variable.startswith("search"):
                    number_of_points = float(variable.split(":")[1])
                    for coord in self.packed_data_items[0].coords():
                        if coord.shape[0] == number_of_points:
                            break
                else:
                    coord = self.packed_data_items[0].coord(variable)
                return coord.points if isinstance(self.packed_data_items[0], Cube) else coord.data

        def __set_variable_as_data(axis):
            old_variable = self.plot_args[axis + "_variable"]
            self.plot_args[axis + "_variable"] = self.packed_data_items[0].name()
            logging.info("Plotting " + self.plot_args[
                axis + "_variable"] + " on the " + axis + " axis as " + old_variable + " has length 1")

        def __swap_x_and_y_variables():
            temp = self.plot_args["x_variable"]
            self.plot_args["x_variable"] = self.plot_args["y_variable"]
            self.plot_args["y_variable"] = temp

        from cis.utils import unpack_data_object
        from iris.cube import Cube
        import logging
        if len(self.packed_data_items[0].shape) == 1:
            x_data = __get_data("x")
            y_data = __get_data("y")

            if len(x_data) == 1 and len(y_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("x")
            elif len(y_data) == 1 and len(x_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("y")
            else:
                try:
                    if (x_data == y_data).all():
                        __swap_x_and_y_variables()
                except AttributeError:
                    if x_data == y_data:
                        __swap_x_and_y_variables()

        return [unpack_data_object(packed_data_item, self.plot_args["x_variable"], self.plot_args["y_variable"],
                                   self.x_wrap_start) for packed_data_item in self.packed_data_items]

    def unpack_comparative_data(self):
        return [{"data": packed_data_item.data} for packed_data_item in self.packed_data_items]

    def plot(self):
        """
        The method that will do the plotting. To be implemented by each subclass of Generic_Plot.
        """
        raise NotImplementedError()

    def format_plot(self):
        """
        The method that will format the plot. To be implemented by each subclass of Generic_Plot.
        """
        raise NotImplementedError()

    def set_default_axis_label(self, axis):
        """
        The method that will set the default axis label. To be implemented by each subclass of Generic_Plot.
        :param axis: The axis of which to set the default label for. Either "x" or "y".
        """
        raise NotImplementedError()

    def create_legend(self):
        """
        Creates a draggable legend in the "best" location for the plot.
        Works out legend labels unless explicitly given to the parser in the datagroups argument.
        """
        legend_titles = []
        datagroups = self.plot_args["datagroups"]
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = self.matplotlib.legend(legend_titles, loc="best")
        legend.draggable(state=True)

    def calculate_axis_limits(self, axis, min_val, max_val):
        """
        Calculates the axis limits for a given axis
        :param axis: The axis for the limits to be calculated
        :return: A dictionary containing the min and max values of an array along a given axis
        """
        c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis,
                                                                    self.unpacked_data_items[
                                                                        0][axis])

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.plot_args["y_variable"] == "air_pressure" and min_val is None and max_val is None:
            new_min, new_max = new_max, new_min

        return new_min, new_max

    def apply_axis_limits(self):
        """
        Applies the limits to the specified axis if given, or calculates them otherwise
        """

        self.xmin, self.xmax = self.calculate_axis_limits('x', self.plot_args['xmin'], self.plot_args['xmax'])
        ymin, ymax = self.calculate_axis_limits('y', self.plot_args['ymin'], self.plot_args['ymax'])

        if self.is_map():
            try:
                self.cartopy_axis.set_extent([self.xmin, self.xmax, ymin, ymax], crs=self.transform)
            except ValueError:
                self.cartopy_axis.set_extent([self.xmin, self.xmax, ymin, ymax], crs=self.projection)
        else:
            self.matplotlib.set_xlim(xmin=self.xmin, xmax=self.xmax)
            self.matplotlib.set_ylim(ymin=ymin, ymax=ymax)

    def add_color_bar(self):
        """
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        """

        step = self.plot_args["vstep"]
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)

        if self.plot_args["logv"]:
            formatter = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
        else:
            formatter = None
        #
        scale = self.plot_args["cbarscale"]
        orientation = self.plot_args["cbarorient"]
        if scale is None:
            default_scales = {"horizontal": 1.0, "vertical": 0.55}
            scale = default_scales.get(orientation, 1.0)
        else:
            scale = float(scale)

        cbar = self.matplotlib.colorbar(self.color_axis[0], orientation=orientation, ticks=ticks,
                                        shrink=scale, format=formatter)

        if not self.plot_args["logv"]:
            cbar.formatter.set_scientific(True)
            cbar.formatter.set_powerlimits((-3, 3))
            cbar.update_ticks()

        if self.plot_args["cbarlabel"] is None:
            label = self.format_units(self.packed_data_items[0].units)
        else:
            label = self.plot_args["cbarlabel"]

        cbar.set_label(label)

    def set_axis_ticks(self, axis, no_of_dims):
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
        from numpy import arange

        tick_kwargs = {}

        if self.is_map():
            if axis == "x":
                coord_axis = "x"
                tick_method = self.cartopy_axis.set_xticks
                self.cartopy_axis.xaxis.set_major_formatter(LongitudeFormatter())
            elif axis == "y":
                coord_axis = "data" if no_of_dims == 2 else "y"
                tick_method = self.cartopy_axis.set_yticks
                self.cartopy_axis.yaxis.set_major_formatter(LatitudeFormatter())

            tick_kwargs['crs'] = self.transform
        else:
            if axis == "x":
                coord_axis = "x"
                tick_method = self.matplotlib.set_xticks
            elif axis == "y":
                coord_axis = "data" if no_of_dims == 2 else "y"
                tick_method = self.matplotlib.set_yticks

            #TODO: These other kwargs are going to be broken, I think I'll need to ask for the labels using get_labels, then use l.update(kwarg).

            # if self.plot_args.get(axis + "tickangle", None) is None:
            #     angle = None
                # tick_kwargs['ha'] = "center" if axis == "x" else "right"
            # else:
                # tick_kwargs['rotation'] = self.plot_args[axis + "tickangle"]
                # tick_kwargs['ha'] = "right"

        if self.plot_args[axis + "step"] is not None:
            step = self.plot_args[axis + "step"]

            if self.plot_args[axis + "min"] is None:
                min_val = min(unpacked_data_item[coord_axis].min() for unpacked_data_item in self.unpacked_data_items)
            else:
                min_val = self.plot_args[axis + "min"]

            if self.plot_args[axis + "max"] is None:
                max_val = max(unpacked_data_item[coord_axis].max() for unpacked_data_item in self.unpacked_data_items)
            else:
                max_val = self.plot_args[axis + "max"]

            ticks = arange(min_val, max_val + step, step)

            tick_method(ticks, **tick_kwargs)
        elif not self.is_map() and tick_kwargs:
            tick_method(**tick_kwargs)

    def format_time_axis(self):
        from cis.time_util import cis_standard_time_unit

        coords = self.packed_data_items[0].coords(standard_name=self.plot_args["x_variable"])
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(name_or_coord=self.plot_args["x_variable"])
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(long_name=self.plot_args["x_variable"])

        if len(coords) == 1:
            if coords[0].units == str(cis_standard_time_unit):
                self.matplotlib.xaxis_date()
                # self.set_x_axis_as_time()

    def set_default_axis_label_for_comparative_plot(self, axis):
        """
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        :param axis: The axis to set the default label for
        """
        axis = axis.lower()
        axislabel = axis + "label"
        if axis == 'x':
            item_index = 0
        elif axis == 'y':
            item_index = 1

        if self.plot_args[axislabel] is None:
            units = self.packed_data_items[item_index].units
            name = self.packed_data_items[item_index].name()
            self.plot_args[axislabel] = name + " " + self.format_units(units)

    def calc_min_and_max_vals_of_array_incl_log(self, axis, array):
        """
        Calculates the min and max values of a given array.
        If a log scale is being used on the given axis, only positive values are taken into account
        :param axis: The axis to check if a log scale is being used for
        :param array: The array to calculate the min and max values of
        :return: The min and max values of the array
        """
        log_axis = self.plot_args["log" + axis]

        if log_axis:
            import numpy.ma as ma
            positive_array = ma.array(array, mask=array <= 0)
            min_val = positive_array.min()
            max_val = positive_array.max()
        else:
            min_val = array.min()
            max_val = array.max()
        return min_val, max_val

    def set_x_axis_as_time(self):
        from matplotlib import ticker
        from cis.time_util import convert_std_time_to_datetime

        ax = self.matplotlib.gca()

        def format_date(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%Y-%m-%d')

        def format_datetime(x, pos=None):
            # use iosformat rather than strftime as strftime can't handle dates before 1900 - the output is the same
            date_time = convert_std_time_to_datetime(x)
            day_range = self.matplotlib.gcf().axes[0].viewLim.x1 - self.matplotlib.gcf().axes[0].viewLim.x0
            if day_range < 1 and date_time.second == 0:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute
            elif day_range < 1:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute + ':' + "%02d" % date_time.second
            elif day_range > 5:
                return str(date_time.date())
            else:
                return date_time.isoformat(' ')

        def format_time(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%H:%M:%S')

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_datetime))
        tick_angle = self.plot_args["xtickangle"]
        if tick_angle is None:
            self.plot_args["xtickangle"] = 45
        self.matplotlib.xticks(rotation=self.plot_args["xtickangle"], ha="right")
        # Give extra spacing at bottom of plot due to rotated labels
        self.matplotlib.gcf().subplots_adjust(bottom=0.3)

        # ax.xaxis.set_minor_formatter(ticker.FuncFormatter(format_time))

    def set_font_size(self):
        """
        Converts the fontsize argument (if specified) from a float into a dictionary that matplotlib can recognise.
        Could be further extended to allow specifying bold, and other font formatting
        """
        if self.plot_args["fontsize"] is not None:
                self.mplkwargs["fontsize"] = {"font.size": float(self.plot_args["fontsize"])}

    def is_map(self):
        """
        :return: A boolean saying if the first packed data item contains lat and lon coordinates
        """
        from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
        from cis.exceptions import CoordinateNotFoundError as cisNotFoundError
        try:
            x = self.packed_data_items[0].coord(self.plot_args["x_variable"])
            y = self.packed_data_items[0].coord(self.plot_args["y_variable"])
        except (cisNotFoundError, irisNotFoundError):
            return False

        if x.name().lower().startswith("lon") and y.name().lower().startswith("lat"):
            return True
        else:
            return False

    def calculate_min_and_max_values(self):
        """
        Calculates the min and max values of all the data given
        Stores the values in the matplotlib keyword args to be directly passed into the plot methods.
        """
        from sys import maxint
        from numpy import ma

        if self.plot_args['logv']:
            mask_val = 0.0
        else:
            mask_val = -maxint - 1

        vmin = self.plot_args["vmin"] or maxint
        vmax = self.plot_args["vmax"] or -maxint - 1

        if vmin == maxint:
            vmin = min(ma.array(unpacked_data_item["data"], mask=unpacked_data_item["data"] <= mask_val).min() for
                       unpacked_data_item in self.unpacked_data_items)

        if vmax == -maxint - 1:
            vmax = max(ma.array(unpacked_data_item["data"], mask=unpacked_data_item["data"] <= mask_val).max() for
                       unpacked_data_item in self.unpacked_data_items)

        # TODO: This should really just return the values, and let the calling function put them where they want.
        self.mplkwargs["vmin"] = float(vmin)
        self.mplkwargs["vmax"] = float(vmax)

    def contour_plot(self, filled):
        """
        Used by both contour and contourf to plot a contour plot
        :param filled: A boolean specifying whether or not the contour plot should be filled
        """

        # Set the options specific to a datagroup with the contour type
        self.mplkwargs['cmap'] = self.plot_args['datagroups'][self.datagroup]['cmap']
        self.mplkwargs["contlabel"] = self.plot_args['datagroups'][self.datagroup]['contlabel']
        self.mplkwargs["cfontsize"] = self.plot_args['datagroups'][self.datagroup]['contfontsize']
        self.mplkwargs["colors"] = self.plot_args['datagroups'][self.datagroup]['color']

        self.mplkwargs["linewidths"] = self.plot_args['datagroups'][self.datagroup]['contwidth']
        if self.plot_args['datagroups'][self.datagroup]['cmin'] is not None:
            self.plot_args["vmin"] = self.plot_args['datagroups'][self.datagroup]['cmin']
        if self.plot_args['datagroups'][self.datagroup]['cmax'] is not None:
            self.plot_args["vmax"] = self.plot_args['datagroups'][self.datagroup]['cmax']

        self.calculate_min_and_max_values()

        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.plot_args["vstep"] is None and \
                        self.plot_args['datagroups'][self.datagroup]['contnlevels'] is None:
            nconts = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        elif self.plot_args["vstep"] is None:
            nconts = self.plot_args['datagroups'][self.datagroup]['contnlevels']
        else:
            nconts = (vmax - vmin) / self.plot_args["vstep"]

        if self.plot_args['datagroups'][self.datagroup]['contlevels'] is None:
            if self.plot_args['logv'] is None:
                contour_level_list = np.linspace(vmin, vmax, nconts)
            else:
                contour_level_list = np.logspace(np.log10(vmin), np.log10(vmax), nconts)
        else:
            contour_level_list = self.plot_args['datagroups'][self.datagroup]['contlevels']

        if filled:
            contour_type = self.matplotlib.contourf
        else:
            contour_type = self.matplotlib.contour

        if self.is_map() and self.unpacked_data_items[0]["data"].ndim == 2:
            # This fails for an unknown reason on one dimensional data
            self.mplkwargs["latlon"] = True

        self.color_axis.append(contour_type(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"],
                                       self.unpacked_data_items[0]["data"], contour_level_list, *self.mplargs, **self.mplkwargs))
        if self.mplkwargs["contlabel"] and not filled:
            self.matplotlib.clabel(self.color_axis[0], fontsize=self.mplkwargs["cfontsize"], inline=1, fmt='%.3g')
        elif self.mplkwargs["contlabel"] and filled:
            self.matplotlib.clabel(self.color_axis[0], fontsize=self.mplkwargs["cfontsize"], inline=0, fmt='%.3g')

        self.mplkwargs.pop("latlon", None)
        self.mplkwargs.pop("tri", None)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def set_log_scale(self, logx, logy):
        """
        Sets a log (base 10) scale (if specified) on the axes
        :param logx: A boolean specifying whether or not to apply a log scale to the x axis
        :param logy: A boolean specifying whether or not to apply a log scale to the y axis
        """
        if logx:
            self.matplotlib.set_xscale("log")
        if logy:
            self.matplotlib.set_yscale("log")

    def set_axes_ticks(self, no_of_dims):
        self.set_axis_ticks("x", no_of_dims)
        self.set_axis_ticks("y", no_of_dims)

    def format_2d_plot(self):
        """
        Used by 2d subclasses to format the plot
        """
        import logging
        from cis.plotting.plot import plot_options

        logx = self.plot_args["logx"]
        logy = self.plot_args["logy"]
        if logx or logy:
            self.set_log_scale(logx, logy)
        else:
            try:
                self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3, 3), axis='both')
            except AttributeError:
                logging.warning("Couldn't apply scientific notation to axes")

        if self.plot_args["grid"]:
            self.matplotlib.grid(True, which="both")

        self.set_axes_ticks(2)

        self.set_font_size()

        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        for key in plot_options.keys():
            # Call the method associated with the option
            if key in self.plot_args.keys() and self.plot_args[key] is not None:
                plot_options[key](self.plot_args[key])

        if len(self.packed_data_items) > 1:
            self.create_legend()

    def _get_extent(self):
        """
         Calculates the diagonal extent of plot area in Km
        :return: The diagonal size of the plot in Km
        """
        from cis.utils import haversine
        x0, x1, y0, y1 = self.cartopy_axis.get_extent()
        return haversine(y0, x0, y1, x1)

    def _test_natural_earth_available(self):
        """
        Test whether we can download the natural earth cartographies.
        :return: Can we access natural earth?
        """
        from cartopy.io.shapereader import natural_earth
        from urllib2 import HTTPError
        try:
            natural_earth_available = natural_earth()
        except HTTPError:
            natural_earth_available = False
        return natural_earth_available

    def drawcoastlines(self):
        """
        Adds coastlines or nasa blue marble back ground to a plot (no coastlines are plotted over nasa blue marble).
        There are three levels of resolution used based on the spatial scale of the plot. These are determined using
        values determined by eye for bluemarble and the coastlines independently.
        """
        from matplotlib.image import imread
        import os.path as path
        bluemarble_scales =[(0, 'raster/world.topo.bathy.200407.3x1350x675.png'),
                            (5000, 'raster/world.topo.bathy.200407.3x2700x1350.png'),
                            (2500, 'raster/world.topo.bathy.200407.3x5400x2700.png')]

        coastline_scales = [(0, '110m'), (500, '50m'), (100, '10m')]

        ext = self._get_extent()

        if self.plot_args["nasabluemarble"] is not False:
            bluemarble_res = bluemarble_scales[0][1]
            for scale, res in bluemarble_scales[1:]:
                if scale > ext:
                    bluemarble_res = res

            img = imread(path.join(path.dirname(path.realpath(__file__)), bluemarble_res))
            self.cartopy_axis.imshow(img, origin='upper', transform=self.transform, extent=[-180, 180, -90, 90])
        else:
            if self._test_natural_earth_available():
                coastline_res = coastline_scales[0][1]
                for scale, res in coastline_scales[1:]:
                    if scale > ext:
                        coastline_res = res

                colour = self.plot_args["coastlinescolour"] if self.plot_args["coastlinescolour"] is not None else "black"
                self.cartopy_axis.coastlines(color=colour, resolution=coastline_res)
            else:
                logging.warning('Unable to access the natural earth topographies required for plotting coastlines. '
                                'Check internet connectivity and try again')

    def format_3d_plot(self):
        """
        Used by 3d subclasses to format the plot
        """
        from cis.plotting.plot import plot_options
        import cis.plotting.overlay

        logx = self.plot_args["logx"]
        logy = self.plot_args["logy"]
        if logx or logy:
            self.set_log_scale(logx, logy)

        if self.plot_args["grid"]:
            self.matplotlib.grid(True, which="both")

        if self.is_map():
            self.drawcoastlines()

        self.set_axes_ticks(3)

        self.set_font_size()
        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        if self.plot_args["xlabel"] is None:
            self.plot_args["xlabel"] = ""
        if self.plot_args["ylabel"] is None:
            self.plot_args["ylabel"] = ""
        if self.plot_args["title"] is None:
            self.plot_args["title"] = self.packed_data_items[0].long_name

        for key in plot_options.keys():
            # Call the method associated with the option
            if key in self.plot_args.keys():
                plot_options[key](self.plot_args[key])

        if not self.plot_args["nocolourbar"]:
            self.add_color_bar()

        if len(self.packed_data_items) > 1 and not isinstance(self, cis.plotting.overlay.Overlay):
            self.create_legend()

    def set_3daxis_label(self, axis):
        """
        Used by 3d plots to calculate the default axis label.
        Uses Latitude or Longitude if a map is being plotted
        :param axis: The axis to calculate the default label for
        """
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if self.is_map():
                self.plot_args[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_items[0].coord(self.plot_args[axis + "_variable"]).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(self.plot_args[axis + "_variable"]).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                self.plot_args[axislabel] = name + " " + self.format_units(units)

    def format_units(self, units):
        """
        :param units: The units of a variable, as a string
        :return: The units surrounding brackets, or the empty string if no units given
        """
        if "since" in str(units):
            # Assume we are on a time if the units contain since.
            return ""
        elif units:
            return "(" + str(units) + ")"
        else:
            return ""

    def assign_variables_to_x_and_y_axis(self):
        """
        Overwrites which variable to used for the x and y axis
        Does not work for Iris Cubes
        :param main_arguments: The arguments received from the parser
        :param data: A list of packed data objects
        """
        import logging
        from cis.exceptions import NotEnoughAxesSpecifiedError

        x_variable = self.get_variable_name("x")

        if x_variable.lower().endswith('time') and len(self.packed_data_items) > 1:
            y_variable = 'default'
        else:
            y_variable = self.get_variable_name("y")

        if x_variable == y_variable:
            specified_axis = "x" if self.plot_args["x_variable"] is not None else "y"
            not_specified_axis = "y" if specified_axis == "x" else "y"
            raise NotEnoughAxesSpecifiedError("-- {0} axis must also be specified if assigning the current {0} axis "
                                              "coordinate to the {1} axis".format(not_specified_axis, specified_axis))

        if "search" in x_variable:
            logging.info("Plotting unknown on the x axis")
        else:
            logging.info("Plotting " + x_variable + " on the x axis")

        if "search" in y_variable:
            logging.info("Plotting unknown on the y axis")
        else:
            logging.info("Plotting " + y_variable + " on the y axis")

        self.plot_args["x_variable"] = x_variable
        self.plot_args["y_variable"] = y_variable

    @staticmethod
    def name_preferring_standard(coord_item):
        for name in [coord_item.standard_name, coord_item.var_name, coord_item.long_name]:
            if name:
                return name
        return ''

    def get_variable_name(self, axis):
        import iris.exceptions as iris_ex
        import cis.exceptions as cis_ex

        # If the user has explicitly specified what variable they want plotting on the axis
        if self.plot_args[axis + '_variable'] is None:
            try:
                return self.name_preferring_standard(self.packed_data_items[0].coord(axis=axis.upper()))
            except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
                if axis == "x":
                    number_of_points_in_dimension = self.packed_data_items[0].shape[0]
                elif axis == "y":
                    if len(self.packed_data_items[0].shape) > 1:
                        number_of_points_in_dimension = self.packed_data_items[0].shape[1]
                    else:
                        return "default"

                for coord in self.packed_data_items[0].coords():
                    if coord.shape[0] == number_of_points_in_dimension:
                        return "search:" + str(number_of_points_in_dimension)
                return "default"
        else:
            return self.plot_args[axis + "_variable"]

    def auto_set_ticks(self):
        """
        Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
        Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
        vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
        """
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

        y_variable = self.plot_args['y_variable'].lower()
        x_variable = self.plot_args['x_variable'].lower()

        ymin, ymax = self.matplotlib.get_ylim()

        # Matplotlib xlim doesn't work with cartopy plots
        xmin, xmax = self.xmin, self.xmax
        # xmin, xmax = self.matplotlib.xlim()

        max_x_bins = 9
        max_y_bins = 9

        xsteps = self.plot_args['xstep']
        ysteps = self.plot_args['ystep']

        lon_steps = [1, 3, 6, 9, 10]
        lat_steps = [1, 3, 6, 9, 10]
        variable_step = [1, 2, 4, 5, 10]

        if (xmax - xmin) < 5:
            lon_steps = variable_step
        if (ymax - ymin) < 5:
            lat_steps = variable_step

        # We need to make a special exception for particularly narrow and wide plots, which will be lat vs lon
        # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
        # the maximum number of bins.
        if x_variable.startswith('lon') and y_variable.startswith('lat'):
            max_y_bins = 7  # as plots are wider rather than taller
            if (ymax - ymin) > 2.2 * (xmax - xmin):
                max_x_bins = 4
                max_y_bins = 11
            elif (xmax - xmin) > 2.2 * (ymax - ymin):
                max_x_bins = 14
                max_y_bins = 4

        lat_or_lon = 'lat', 'lon'

        if xsteps is None and not self.plot_args['logx']:
            if self.plot_args['x_variable'].lower().startswith(lat_or_lon):
                lon_locator = MaxNLocator(nbins=max_x_bins, steps=lon_steps)
                if self.is_map():
                    self.cartopy_axis.set_xticks(lon_locator.tick_values(xmin, xmax), crs=self.transform)
                    self.cartopy_axis.xaxis.set_major_formatter(LongitudeFormatter())
                else:
                    self.matplotlib.axes().xaxis.set_major_locator(lon_locator)
            else:
                self.matplotlib.axes().xaxis.set_major_locator(MaxNLocator(nbins=max_x_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().xaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().xaxis.grid(False, which='minor')

        if ysteps is None and not self.plot_args['logy']:
            if y_variable.startswith(lat_or_lon):
                lat_locator = MaxNLocator(nbins=max_y_bins, steps=lat_steps)
                if self.is_map():
                    self.cartopy_axis.set_yticks(lat_locator.tick_values(ymin, ymax), crs=self.transform)
                    self.cartopy_axis.yaxis.set_major_formatter(LatitudeFormatter())
                else:
                    self.matplotlib.axes().yaxis.set_major_locator(lat_locator)
            else:
                self.matplotlib.axes().yaxis.set_major_locator(MaxNLocator(nbins=max_y_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().yaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().yaxis.grid(False, which='minor')
