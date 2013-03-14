import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

class Generic_Plot(object):
    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    def __init__(self, packed_data_items, plot_args, calculate_min_and_max_values = True, *mplargs, **mplkwargs):
        '''
        Constructor for Generic_Plot.
        Note: This also calls the plot method
        @param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        @param plot_args: A dictionary of plot args that was created by plot.py
        @param mplargs: Any arguments to be passed directly into matplotlib
        @param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        '''
        from jasmin_cis.utils import unpack_data_object
        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        if plot_args.get("logv", False):
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        self.plot_args = plot_args
        self.packed_data_items = packed_data_items
        self.unpacked_data_items = [unpack_data_object(packed_data_item) for packed_data_item in self.packed_data_items]
        if calculate_min_and_max_values: self.calculate_min_and_max_values()

        self.matplotlib = plt

        if self.is_map():
            self.basemap = Basemap(lon_0=(self.unpacked_data_items[0])["x"].max()-180.0)
            self.plot_method = self.basemap
        else:
            self.plot_method = self.matplotlib

        self.set_width_and_height()
        
        self.plot()

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
        @param axis: The axis of which to set the default label for. Either "x" or "y".
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
        @param axis: The axis for the limits to be calculated
        @return: A dictionary containing the min and max values of an array along a given axis
        '''
        calculated_min, calculated_max = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][axis])
        valrange = {}
        valrange[axis + "min"] = calculated_min if min_val is None else min_val
        valrange[axis + "max"] = calculated_max if max_val is None else max_val
        valrange[axis + "step"] = step

        return valrange

    def apply_axis_limits(self, valrange, axis):
        '''
        Applies the limits to the specified axis if given, or calculates them otherwise
        @param valrange    A dictionary containing xmin, xmax or ymin, ymax
        @param axis        The axis to apply the limits to
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

        cbar = self.matplotlib.colorbar(orientation = self.plot_args["cbarorient"], ticks = ticks)

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

        if self.is_map() and self.plot_args[axis + "range"].get(axis + "step") is None:
            self.plot_args[axis + "range"][axis + "step"] = 30

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

        coords = self.packed_data_items[0].coords(axis='X')
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(axis='T')

        if len(coords) == 1:
            if coords[0].units == str(cis_standard_time_unit):
                self.set_x_axis_as_time()

    def set_default_axis_label_for_comparative_plot(self, axis):
        '''
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        @param axis: The axis to set the default label for
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
            self.plot_args[axislabel] = name + self.format_units(units)

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
        @param axis: The axis to check if a log scale is being used for
        @param array: The array to calculate the min and max values of
        @return: The min and max values of the array
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
            if date_time.hour == 0 and date_time.minute == 0 and date_time.second == 0:
                return date_time.strftime("%Y-%m-%d")
            elif date_time.second == 0:
                return date_time.strftime("%Y-%m-%d %H:%M")
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
        @return: A boolean saying if the first packed data item contains lat and lon coordinates
        '''
        from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
        from jasmin_cis.exceptions import CoordinateNotFoundError as JasminNotFoundError
        axes = {}
        try:
            axes["X"] = self.packed_data_items[0].coord(axis="X")
            axes["Y"] = self.packed_data_items[0].coord(axis="Y")
        except (JasminNotFoundError, irisNotFoundError):
            return False

        if axes["X"].name().lower().startswith("lon") and axes["Y"].name().lower().startswith("lat"):
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
        '''
        Used by both contour and contourf to plot a contour plot
        @param filled: A boolean specifying whether or not the contour plot should be filled
        '''
        from numpy import linspace
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.plot_args["valrange"].get("vstep", None) is None:
            step = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        else:
            step = (vmax - vmin) / self.plot_args["valrange"]["vstep"]

        if filled:
            contour_type = self.plot_method.contourf
        else:
            contour_type = self.plot_method.contour

        if self.is_map(): self.mplkwargs["latlon"] = True

        contour_type(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], linspace(vmin, vmax, step), *self.mplargs, **self.mplkwargs)

        self.mplkwargs.pop("latlon", None)
        
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def set_log_scale(self, logx, logy):
        '''
        Sets a log (base 10) scale (if specified) on the axes
        @param logx: A boolean specifying whether or not to apply a log scale to the x axis
        @param logy: A boolean specifying whether or not to apply a log scale to the y axis
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

    def format_3d_plot(self):
        '''
        Used by 3d subclasses to format the plot
        '''
        from jasmin_cis.plotting.plot import plot_options

        logx = self.plot_args.get("logx", False)
        logy = self.plot_args.get("logy", False)
        if logx or logy:
            self.set_log_scale(logx, logy)

        draw_grid = self.plot_args.get("grid")
        if draw_grid: self.matplotlib.grid(True, which="both")

        if self.is_map():
            colour = self.plot_args["coastlinescolour"] if self.plot_args["coastlinescolour"] is not None else "k"
            self.basemap.drawcoastlines(color = colour)

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

        if len(self.packed_data_items) > 1: self.create_legend()

    def set_3daxis_label(self, axis):
        '''
        Used by 3d plots to calculate the default axis label.
        Uses Latitude or Longitude if a map is being plotted
        @param axis: The axis to calculate the default label for
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
                    name = self.packed_data_items[0].coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                self.plot_args[axislabel] = name + self.format_units(units)

    def format_units(self, units):
        '''
        @param units: The units of a variable, as a string
        @return: The units formatted in LaTeX style with surrounding brackets, or the empty string if no units given
        '''
        if units:
            return " ($" + str(units) + "$)"
        else:
            return ""

