import logging

import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
import matplotlib.pyplot as plt

from jasmin_cis.exceptions import CISError
from jasmin_cis.utils import find_longitude_wrap_start
from jasmin_cis.plotting.formatter import LogFormatterMathtextSpecial


class Generic_Plot(object):
    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    def __init__(self, packed_data_items, plot_args, x_wrap_start=None, calculate_min_and_max_values=True, datagroup=0,
                 *mplargs, **mplkwargs):
        '''
        Constructor for Generic_Plot.
        Note: This also calls the plot method
        :param calculate_min_and_max_values: If true calculates min and max for the data values
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        '''
        self.mplargs = mplargs
        self.mplkwargs = mplkwargs
        self.datagroup = datagroup

        if plot_args.get("logv", False):
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        self.plot_args = plot_args
        self.packed_data_items = packed_data_items

        self.assign_variables_to_x_and_y_axis()

        logging.debug("Unpacking the data items")
        self.x_wrap_start = self.set_x_wrap_start(x_wrap_start)
        self.unpacked_data_items = self.unpack_data_items()

        if calculate_min_and_max_values:
            self.calculate_min_and_max_values()

        self.matplotlib = plt

        self.plotting_library = self.set_plotting_library()

        self.set_width_and_height()

        if self.is_map():
            self.check_data_is_2d()
            self.sort_by_lons_and_lats()

        self.plot()

    def check_data_is_2d(self):
        if len(self.packed_data_items[0].shape) > 2:
            raise CISError("Data is not 1D or 2D - can't plot it on a map.")

    def sort_by_lons_and_lats(self):
        """
        Sort the data by longitude as the Basemap plotting routines requires the data to be montonically increasing by
        longitude. Also sorts in latitude (this won't cause Basemap to fail but contour plotting etc will be wrong).
        :return:
        """
        lons = self.unpacked_data_items[0]['x']
        lats = self.unpacked_data_items[0]['y']
        if lons is not None and lats is not None:
            shape = lons.shape
            lons = lons.flatten()
            lats = lats.flatten()
            sort_order = np.lexsort((lons, -lats))
            for var_name, variable in self.unpacked_data_items[0].iteritems():
                if variable is not None:
                    reordered_points = variable.flatten()[sort_order]
                    self.unpacked_data_items[0][var_name] = np.reshape(reordered_points, shape)

    def set_x_wrap_start(self, x_wrap_start):
        if x_wrap_start is None:
            x_wrap_start = find_longitude_wrap_start(self.plot_args["x_variable"], self.plot_args.get('xrange'),
                                                          self.packed_data_items)
        return x_wrap_start

    def set_plotting_library(self):
        if self.is_map():
            max_found = 180
            x_range_dict = self.plot_args.get('xrange')
            x_max_requested = x_range_dict.get('xmax')
            max_found = max([max_found, x_max_requested])
            data_max = self.get_data_items_max()
            max_found = max(data_max, max_found)
            self.basemap = Basemap(lon_0=(max_found-180.0))
            return self.basemap
        else:
            return self.matplotlib

    def get_data_items_max(self):
        data_max = self.unpacked_data_items[0]['x'].max()
        for i in self.unpacked_data_items:
            data_max = max([i["x"].max(), data_max])
        return data_max

    def unpack_data_items(self):
        def __get_data(axis):
            variable = self.plot_args[axis + "_variable"]
            if variable == "default" or variable == self.packed_data_items[0].name() or \
               variable == self.packed_data_items[0].standard_name or variable == self.packed_data_items[0].long_name:
                return self.packed_data_items[0].data
            else:
                if variable.startswith("search"):
                    number_of_points = float(variable.split(":")[1])
                    for coord in self.packed_data_items[0].coords():
                        if coord.shape[0] == number_of_points: break
                else:
                    coord = self.packed_data_items[0].coord(variable)
                return coord.points if isinstance(self.packed_data_items[0], Cube) else coord.data

        def __set_variable_as_data(axis):
            old_variable = self.plot_args[axis + "_variable"]
            self.plot_args[axis + "_variable"] = self.packed_data_items[0].name()
            logging.info("Plotting " + self.plot_args[axis + "_variable"] + " on the " + axis + " axis as " + old_variable + " has length 1")

        def __swap_x_and_y_variables():
            temp =  self.plot_args["x_variable"]
            self.plot_args["x_variable"] = self.plot_args["y_variable"]
            self.plot_args["y_variable"] = temp


        from jasmin_cis.utils import unpack_data_object
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
        return [{"data" : packed_data_item.data} for packed_data_item in self.packed_data_items]

    def plot(self):
        '''
        The method that will do the plotting. To be implemented by each subclass of Generic_Plot.
        '''
        raise NotImplementedError()

    def format_plot(self):
        '''
        The method that will format the plot. To be implemented by each subclass of Generic_Plot.
        '''
        raise NotImplementedError()

    def set_default_axis_label(self, axis):
        '''
        The method that will set the default axis label. To be implemented by each subclass of Generic_Plot.
        :param axis: The axis of which to set the default label for. Either "x" or "y".
        '''
        raise NotImplementedError()

    def create_legend(self):
        '''
        Creates a draggable legend in the "best" location for the plot.
        Works out legend labels unless explicitly given to the parser in the datagroups argument.
        '''
        legend_titles = []
        datagroups = self.plot_args["datagroups"]
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = self.matplotlib.legend(legend_titles, loc="best")
        legend.draggable(state = True)

    def calculate_axis_limits(self, axis, min_val, max_val, step):
        '''
        Calculates the axis limits for a given axis
        :param axis: The axis for the limits to be calculated
        :return: A dictionary containing the min and max values of an array along a given axis
        '''
        calculated_min, calculated_max = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][axis])
        valrange = {}
        valrange[axis + "min"] = calculated_min if min_val is None else min_val
        valrange[axis + "max"] = calculated_max if max_val is None else max_val
        valrange[axis + "step"] = step

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.plot_args["y_variable"] == "air_pressure" and min_val is None and max_val is None:
            valrange[axis + "min"], valrange[axis + "max"] = valrange[axis + "max"], valrange[axis + "min"]

        return valrange

    def apply_axis_limits(self, valrange, axis):
        '''
        Applies the limits to the specified axis if given, or calculates them otherwise
        :param valrange    A dictionary containing xmin, xmax or ymin, ymax
        :param axis        The axis to apply the limits to
        '''
        valrange = self.calculate_axis_limits(axis, valrange.get(axis + "min", None), valrange.get(axis + "max", None), valrange.get(axis + "step", None))

        if axis == "x":
            step = valrange.pop("xstep", None)
            self.matplotlib.xlim(**valrange)
            if step is not None: valrange["xstep"] = step
        elif axis == "y":
            step = valrange.pop("ystep", None)
            self.matplotlib.ylim(**valrange)
            if step is not None: valrange["ystep"] = step

    def add_color_bar(self):
        '''
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        '''

        step = self.plot_args["valrange"].get("vstep", None)
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)

        if self.plot_args.get("logv", False):
            formatter = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
        else:
            formatter = None

        cbar = self.matplotlib.colorbar(orientation = self.plot_args["cbarorient"], ticks = ticks,
                                        shrink=float(self.plot_args["cbarscale"]), format=formatter)

        if not self.plot_args["logv"]:
            cbar.formatter.set_scientific(True)
            cbar.formatter.set_powerlimits((-3,3))
            cbar.update_ticks()

        if self.plot_args["cbarlabel"] is None:
            label = self.format_units(self.packed_data_items[0].units)
        else:
            label = self.plot_args["cbarlabel"]

        cbar.set_label(label)

    def set_axis_ticks(self, axis, no_of_dims):
        from numpy import arange

        if axis == "x":
            coord_axis = "x"
            tick_method = self.matplotlib.xticks
        elif axis == "y":
            coord_axis = "data" if no_of_dims == 2 else "y"
            tick_method = self.matplotlib.yticks

        if self.plot_args.get(axis + "tickangle", None) is None:
            angle = None
            ha = "center" if axis == "x" else "right"
        else:
            angle = self.plot_args[axis + "tickangle"]
            ha = "right"

        if self.plot_args[axis + "range"].get(axis + "step") is not None:
            step = self.plot_args[axis + "range"][axis + "step"]

            if self.plot_args[axis + "range"].get(axis + "min") is None:
                min_val = min(unpacked_data_item[coord_axis].min() for unpacked_data_item in self.unpacked_data_items)
            else:
                min_val = self.plot_args[axis + "range"][axis + "min"]

            if self.plot_args[axis + "range"].get(axis + "max") is None:
                max_val = max(unpacked_data_item[coord_axis].max() for unpacked_data_item in self.unpacked_data_items)
            else:
                max_val = self.plot_args[axis + "range"][axis + "max"]

            ticks = arange(min_val, max_val+step, step)

            tick_method(ticks, rotation=angle, ha=ha)
        else:
            tick_method(rotation=angle, ha=ha)

    def format_time_axis(self):
        from jasmin_cis.time_util import cis_standard_time_unit

        coords = self.packed_data_items[0].coords(standard_name=self.plot_args["x_variable"])
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(name=self.plot_args["x_variable"])
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(long_name=self.plot_args["x_variable"])

        if len(coords) == 1:
            if coords[0].units == str(cis_standard_time_unit):
                self.set_x_axis_as_time()

    def set_default_axis_label_for_comparative_plot(self, axis):
        '''
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        :param axis: The axis to set the default label for
        '''
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

    def set_width_and_height(self):
        '''
        Sets the width and height of the plot
        Uses an aspect ratio of 4:3 if only one of width and height are specified
        '''
        height = self.mplkwargs.pop("height", None)
        width = self.mplkwargs.pop("width", None)

        if height is not None:
            if width is None:
                width = height * (4.0 / 3.0)
        elif width is not None:
            height = width * (3.0 / 4.0)

        if height is not None and width is not None:
            self.matplotlib.figure(figsize = (width, height))

    def calculate_min_and_max_values_of_array_including_case_of_log(self, axis, array):
        '''
        Calculates the min and max values of a given array.
        If a log scale is being used on the given axis, only positive values are taken into account
        :param axis: The axis to check if a log scale is being used for
        :param array: The array to calculate the min and max values of
        :return: The min and max values of the array
        '''
        log_axis = self.plot_args.get("log" + axis, False)

        if log_axis:
            import numpy.ma as ma
            positive_array = ma.array(array, mask=array<=0)
            min_val = positive_array.min()
            max_val = positive_array.max()
        else:
            min_val =  array.min()
            max_val =  array.max()
        return min_val, max_val

    def set_x_axis_as_time(self):
        from matplotlib import ticker
        from jasmin_cis.time_util import convert_std_time_to_datetime

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
        tick_angle = self.plot_args.get("xtickangle", None)
        if tick_angle is None:
            self.plot_args["xtickangle"] = 45
        self.matplotlib.xticks(rotation=self.plot_args["xtickangle"], ha="right")
        # Give extra spacing at bottom of plot due to rotated labels
        self.matplotlib.gcf().subplots_adjust(bottom=0.3)

        #ax.xaxis.set_minor_formatter(ticker.FuncFormatter(format_time))

    def set_font_size(self):
        '''
        Converts the fontsize argument (if specified) from a float into a dictionary that matplotlib can recognise.
        Could be further extended to allow specifying bold, and other font formatting
        '''
        if self.plot_args.get("fontsize", None) is not None:
            if not isinstance(self.plot_args.get("fontsize", None), dict):
                self.plot_args["fontsize"] = { "font.size" : float(self.plot_args["fontsize"]) }
        else:
            self.plot_args.pop("fontsize", None)

    def is_map(self):
        '''
        :return: A boolean saying if the first packed data item contains lat and lon coordinates
        '''
        from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
        from jasmin_cis.exceptions import CoordinateNotFoundError as JasminNotFoundError
        try:
            x = self.packed_data_items[0].coord(name=self.plot_args["x_variable"])
            y = self.packed_data_items[0].coord(name=self.plot_args["y_variable"])
        except (JasminNotFoundError, irisNotFoundError):
            return False

        if x.name().lower().startswith("lon") and y.name().lower().startswith("lat"):
            return True
        else:
            return False

    def calculate_min_and_max_values(self):
        '''
        Calculates the min and max values of all the data given
        Stores the values in the matplotlib keyword args to be directly passed into the plot methods.
        '''
        from sys import maxint
        from numpy import ma

        if self.plot_args.get('logv', False):
            mask_val = 0.0
        else:
            mask_val = -maxint - 1

        vmin = self.plot_args["valrange"].get("vmin", maxint)
        vmax = self.plot_args["valrange"].get("vmax", -maxint - 1)

        if vmin == maxint:
            vmin = min(ma.array(unpacked_data_item["data"], mask=unpacked_data_item["data"]<=mask_val).min() for unpacked_data_item in self.unpacked_data_items)

        if vmax == -maxint - 1:
            vmax = max(ma.array(unpacked_data_item["data"], mask=unpacked_data_item["data"]<=mask_val).max() for unpacked_data_item in self.unpacked_data_items)

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
            self.plot_args["valrange"]["vmin"] = self.plot_args['datagroups'][self.datagroup]['cmin']
        if self.plot_args['datagroups'][self.datagroup]['cmax'] is not None:
            self.plot_args["valrange"]["vmax"] = self.plot_args['datagroups'][self.datagroup]['cmax']

        self.calculate_min_and_max_values()

        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.plot_args["valrange"].get("vstep", None) is None and \
                self.plot_args['datagroups'][self.datagroup]['contnlevels'] is None:
            nconts = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        elif self.plot_args["valrange"].get("vstep", None) is None:
            nconts = self.plot_args['datagroups'][self.datagroup]['contnlevels']
        else:
            nconts = (vmax - vmin) / self.plot_args["valrange"]["vstep"]

        if self.plot_args['datagroups'][self.datagroup]['contlevels'] is None:
            if self.plot_args.get('logv') is None:
                contour_level_list = np.linspace(vmin, vmax, nconts)
            else:
                contour_level_list = np.logspace(np.log10(vmin), np.log10(vmax), nconts)
        else:
            contour_level_list = self.plot_args['datagroups'][self.datagroup]['contlevels']

        if filled:
            contour_type = self.plotting_library.contourf
        else:
            contour_type = self.plotting_library.contour

        if self.is_map() and self.unpacked_data_items[0]["data"].ndim == 2:
            # This fails for an unknown reason on one dimensional data
            self.mplkwargs["latlon"] = True

        # If data (and x, y) is one dimensional, "tri" is set to true to tell Basemap the data is unstructured
        if self.unpacked_data_items[0]["data"].ndim == 1:
            self.mplkwargs["tri"] = True

        cs = contour_type(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"],
                          self.unpacked_data_items[0]["data"], contour_level_list, *self.mplargs, **self.mplkwargs)
        if self.mplkwargs["contlabel"] and not filled:
            plt.clabel(cs, fontsize=self.mplkwargs["cfontsize"], inline=1, fmt='%.3g')
        elif self.mplkwargs["contlabel"] and filled:
            plt.clabel(cs, fontsize=self.mplkwargs["cfontsize"], inline=0, fmt='%.3g')

        self.mplkwargs.pop("latlon", None)
        self.mplkwargs.pop("tri", None)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def set_log_scale(self, logx, logy):
        '''
        Sets a log (base 10) scale (if specified) on the axes
        :param logx: A boolean specifying whether or not to apply a log scale to the x axis
        :param logy: A boolean specifying whether or not to apply a log scale to the y axis
        '''
        if logx: self.matplotlib.xscale("log")
        if logy: self.matplotlib.yscale("log")

    def set_axes_ticks(self, no_of_dims):
        self.set_axis_ticks("x", no_of_dims)
        self.set_axis_ticks("y", no_of_dims)

    def format_2d_plot(self):
        '''
        Used by 2d subclasses to format the plot
        '''
        import logging
        from jasmin_cis.plotting.plot import plot_options

        logx = self.plot_args.get("logx", False)
        logy = self.plot_args.get("logy", False)
        if logx or logy:
            self.set_log_scale(logx, logy)
        else:
            try:
                self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3,3), axis='both')
            except AttributeError:
                logging.warning("Couldn't apply scientific notation to axes")

        draw_grid = self.plot_args.pop("grid", False)
        if draw_grid: self.matplotlib.grid(True, which="both")

        self.set_axes_ticks(2)

        self.set_font_size()

        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        if self.plot_args["xlabel"] is None: self.plot_args["xlabel"] = ""
        if self.plot_args["ylabel"] is None: self.plot_args["ylabel"] = ""
        if self.plot_args["title"] is None: self.plot_args["title"] = ""

        for key in plot_options.keys():
            # Call the method associated with the option
            if key in self.plot_args.keys():
                plot_options[key](self.plot_args[key])

        if len(self.packed_data_items) > 1: self.create_legend()

    def drawcoastlines(self):
        if self.plot_args["nasabluemarble"] is not False:
            self.basemap.bluemarble()
        else:
            colour = self.plot_args["coastlinescolour"] if self.plot_args["coastlinescolour"] is not None else "k"
            self.basemap.drawcoastlines(color = colour)

    def format_3d_plot(self):
        '''
        Used by 3d subclasses to format the plot
        '''
        from jasmin_cis.plotting.plot import plot_options
        import jasmin_cis.plotting.overlay

        logx = self.plot_args.get("logx", False)
        logy = self.plot_args.get("logy", False)
        if logx or logy:
            self.set_log_scale(logx, logy)

        draw_grid = self.plot_args.get("grid")
        if draw_grid: self.matplotlib.grid(True, which="both")

        if self.is_map(): self.drawcoastlines()

        self.set_axes_ticks(3)

        self.set_font_size()
        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        if self.plot_args["xlabel"] is None: self.plot_args["xlabel"] = ""
        if self.plot_args["ylabel"] is None: self.plot_args["ylabel"] = ""
        if self.plot_args["title"] is None: self.plot_args["title"] = self.packed_data_items[0].long_name

        for key in plot_options.keys():
        # Call the method associated with the option
            if key in self.plot_args.keys():
                plot_options[key](self.plot_args[key])

        if not self.plot_args["nocolourbar"]: self.add_color_bar()

        if len(self.packed_data_items) > 1 and not isinstance(self, jasmin_cis.plotting.overlay.Overlay):
            self.create_legend()

    def set_3daxis_label(self, axis):
        '''
        Used by 3d plots to calculate the default axis label.
        Uses Latitude or Longitude if a map is being plotted
        :param axis: The axis to calculate the default label for
        '''
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if self.is_map():
                self.plot_args[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                self.plot_args[axislabel] = name + " " + self.format_units(units)

    def format_units(self, units):
        '''
        :param units: The units of a variable, as a string
        :return: The units surrounding brackets, or the empty string if no units given
        '''
        if "since" in str(units):
            # Assume we are on a time if the units contain since.
            return ""
        elif units:
            return "(" + str(units) + ")"
        else:
            return ""

    def assign_variables_to_x_and_y_axis(self):
        '''
        Overwrites which variable to used for the x and y axis
        Does not work for Iris Cubes
        :param main_arguments: The arguments received from the parser
        :param data: A list of packed data objects
        '''
        import logging
        from jasmin_cis.exceptions import NotEnoughAxesSpecifiedError

        x_variable = self.get_variable_name("x")
        y_variable = self.get_variable_name("y")

        if x_variable == y_variable:
            specified_axis = "x" if self.plot_args["x_variable"] is not None else "y"
            not_specified_axis = "y" if specified_axis == "x" else "y"
            raise NotEnoughAxesSpecifiedError("--" + not_specified_axis + "axis must also be specified if assigning the current " + not_specified_axis + " axis coordinate to the " + specified_axis + " axis")

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
        import jasmin_cis.exceptions as jasmin_ex

        # If the user has explicitly specified what variable they want plotting on the axis
        if self.plot_args[axis + '_variable'] is None:
            try:
                return self.name_preferring_standard(self.packed_data_items[0].coord(axis=axis.upper()))
            except (iris_ex.CoordinateNotFoundError, jasmin_ex.CoordinateNotFoundError):
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

        y_variable = self.plot_args['y_variable'].lower()
        x_variable = self.plot_args['x_variable'].lower()

        ymin, ymax = self.matplotlib.ylim()
        xmin, xmax = self.matplotlib.xlim()

        max_x_bins = 9
        max_y_bins = 9

        xsteps = self.plot_args['xrange'].get('xstep', None)
        ysteps = self.plot_args['yrange'].get('ystep', None)

        lon_steps = [1, 3, 6, 9, 10]
        lat_steps = [1, 3, 6, 9, 10]
        variable_step = [1, 2, 4, 5, 10]

        if (xmax - xmin) < 5:
            lon_steps = variable_step
        if (ymax - ymin) < 5:
            lat_steps = variable_step

        # We need to make a special exception for paritcularly narrow and wide plots, which will be lat vs lon
        # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
        # the maximum number of bins.
        if x_variable.startswith('lon') and y_variable.startswith('lat'):
            max_y_bins = 7  # as plots are wider rather than taller
            if (ymax - ymin) > 2.2 * (xmax-xmin):
                max_x_bins = 4
                max_y_bins = 11
            elif (xmax - xmin) > 2.2 * (ymax - ymin):
                max_x_bins = 14
                max_y_bins = 4

        lat_or_lon = 'lat', 'lon'

        if xsteps is None and self.plot_args['logx'] is None:
            if self.plot_args['x_variable'].lower().startswith(lat_or_lon):
                self.matplotlib.axes().xaxis.set_major_locator(MaxNLocator(nbins=max_x_bins, steps=lon_steps))
            else:
                self.matplotlib.axes().xaxis.set_major_locator(MaxNLocator(nbins=max_x_bins, steps=variable_step))

            self.matplotlib.axes().xaxis.set_minor_locator(AutoMinorLocator())
            self.matplotlib.axes().xaxis.grid(False, which='minor')

        if ysteps is None and self.plot_args['logy'] is None:
            if y_variable.startswith(lat_or_lon):
                self.matplotlib.axes().yaxis.set_major_locator(MaxNLocator(nbins=max_y_bins, steps=lat_steps))
            else:
                self.matplotlib.axes().yaxis.set_major_locator(MaxNLocator(nbins=max_y_bins, steps=variable_step))

            self.matplotlib.axes().yaxis.set_minor_locator(AutoMinorLocator())
            self.matplotlib.axes().yaxis.grid(False, which='minor')
