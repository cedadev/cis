import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def is_map(data_item):
    axes = []
    for coord in data_item.coords(axis="X"):
        axes.append(coord.name())
    for coord in data_item.coords(axis="Y"):
        axes.append(coord.name())

    # Code review this
    lat = False
    lon = False
    for axis in axes:
        if axis.lower().startswith("lat"): lat = True
        if axis.lower().startswith("lon"): lon = True

    if lat and lon:
        return True
    else:
        return False

class Generic_Plot(object):
    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    def __init__(self, packed_data_items, v_range, plot_args, out_filename = None, *mplargs, **mplkwargs):
        from utils import unpack_data_object
        self.out_filename = out_filename
        self.mplargs = mplargs
        self.mplkwargs = mplkwargs
        self.plot_args = plot_args
        self.packed_data_items = packed_data_items
        self.unpacked_data_items = [unpack_data_object(packed_data_item) for packed_data_item in self.packed_data_items]
        self.v_range = v_range
        self.calculate_min_and_max_values()
        self.matplotlib = plt

        if is_map(packed_data_items[0]):
            self.basemap = Basemap(lon_0=(self.unpacked_data_items[0])["x"].max()-180.0)
            self.plot_method = self.basemap
            self.mplkwargs["latlon"] = True
        else:
            self.plot_method = self.matplotlib

        self.set_width_and_height()

        self.plot()
        self.format_plot()

        self.apply_axis_limits(plot_args["xrange"], "x")
        self.apply_axis_limits(plot_args["yrange"], "y")

        self.output_to_file_or_screen()

    def plot(self):
        raise NotImplementedError()

    def format_plot(self):
        raise NotImplementedError()

    def set_default_axis_label(self, axis):
        raise NotImplementedError()

    def create_legend(self):
        legend_titles = []
        datagroups = self.plot_args["datagroups"]
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = self.matplotlib.legend(legend_titles, loc="best")
        legend.draggable(state = True)

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

    def calculate_axis_limits(self, axis):
        valrange = {}
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][axis])
        return valrange

    def apply_axis_limits(self, valrange, axis):
        '''
        @param valrange    A dictionary containing xmin, xmax or ymin, ymax
        @param axis        The axis to apply the limits to
        '''
        if valrange is None: valrange = self.calculate_axis_limits(axis)

        if axis == "x":
            step = valrange.pop("xstep", None)
            self.matplotlib.xlim(**valrange)
            if step is not None: valrange["xstep"] = step
        elif axis == "y":
            step = valrange.pop("ystep", None)
            self.matplotlib.ylim(**valrange)
            if step is not None: valrange["ystep"] = step

    def set_font_size(self):
        if self.plot_args.get("fontsize", None) is not None:
            if not isinstance(self.plot_args.get("fontsize", None), dict):
                self.plot_args["fontsize"] = { "font.size" : float(self.plot_args["fontsize"]) }
        else:
            self.plot_args.pop("fontsize", None)

    def output_to_file_or_screen(self):
        '''
        Outputs to screen unless a filename is given

        @param out_filename    The filename of the file to save to
        '''
        import logging

        if self.out_filename is None:
            self.matplotlib.show()
        else:
            logging.info("saving plot to file: " + self.out_filename);
            self.matplotlib.savefig(self.out_filename) # Will overwrite if file already exists

    def calculate_min_and_max_values(self):
        from sys import maxint

        vmin = self.v_range.get("vmin", maxint)
        vmax = self.v_range.get("vmax", -maxint - 1)

        if vmin == maxint:
            vmin = min(unpacked_data_item["data"].min() for unpacked_data_item in self.unpacked_data_items)

        if vmax == -maxint - 1:
            vmax = max(unpacked_data_item["data"].max() for unpacked_data_item in self.unpacked_data_items)

        self.mplkwargs["vmin"] = float(vmin)
        self.mplkwargs["vmax"] = float(vmax)

    def add_color_bar(self, logv, vmin, vmax, v_range, orientation, units):
        from plot import format_units
        # nformat = "%e"
        # nformat = "%.3f"
        # nformat = "%.3e"
        nformat = "%.3g"

        if not logv:
            try:
                step = v_range.get("vstep", (vmax-vmin) / self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS)
            except AttributeError:
                step = (vmax-vmin) / self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS
            ticks = []
            tick = vmin
            while tick <= vmax:
                ticks.append(tick)
                tick = tick + step
        else:
            ticks = None

        #ticks = None

        cbar = plt.colorbar(orientation = orientation, ticks = ticks, format = nformat)

        cbar.set_label(format_units(units))

    def contour_plot(self, filled):
        from numpy import linspace
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.v_range.get("vstep", None) is None:
            step = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        else:
            step = (vmax - vmin) / self.v_range["vstep"]

        if filled:
            contour_type = self.plot_method.contourf
        else:
            contour_type = self.plot_method.contour

        contour_type(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], linspace(vmin, vmax, step), *self.mplargs, **self.mplkwargs)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def draw_coastlines(self, draw_grid = False):
        if is_map(self.packed_data_items[0]):
            self.basemap.drawcoastlines()

            parallels, meridians = self.__create_map_grid_lines()
            if draw_grid:
                self.basemap.drawparallels(parallels)
                self.basemap.drawmeridians(meridians)

            meridian_labels = self.__format_map_ticks(meridians, "x")
            parallel_labels = self.__format_map_ticks(parallels, "y")

            plt.xticks(meridians, meridian_labels)
            plt.yticks(parallels, parallel_labels)

    def __create_map_grid_lines(self):
        def __create_set_of_grid_lines(axis, range_dict):
            from numpy import arange, append
            lines = None
            grid_spacing = 15 # in degrees
            if range_dict is not None: #If the user has specified range
                min_val = range_dict[axis + "min"]
                max_val = range_dict[axis + "max"]
                step = range_dict.get(axis + "step", None)
            else:
                try:
                    min_val = self.valrange[axis][axis + "min"]
                    max_val = self.valrange[axis][axis + "max"]
                    step = None
                except AttributeError:
                    if axis == "y":
                        lines = arange(-90, 91, grid_spacing)
                    elif axis == "x":
                        lines = arange(0, 361, grid_spacing)

            if lines is None:
                if step is None: step = (max_val-min_val)/24
                lines = arange(min_val, max_val+1, step)
                if min_val < 0 and max_val > 0: lines = append(lines, 0)
                lines.sort()

            return lines

        parallels = __create_set_of_grid_lines("y", self.plot_args["yrange"])
        meridians = __create_set_of_grid_lines("x", self.plot_args["xrange"])

        return parallels, meridians

    def __format_map_ticks(self, tick_array, axis):
        label_format = "{0:.0f}"
        labels = []
        i = 0
        label_every_nth_tick = 4
        for tick in tick_array:
            # Label every nth tick, the 0 tick, and the last tick
            if i % label_every_nth_tick == 0 or tick == 0 or i == len(tick_array) - 1:
                if tick == 0:
                    labels.append(0)
                else:
                    labels.append(label_format.format(tick))
            else:
                labels.append("")
            i += 1
        return labels

    def set_log_scale(self, logx, logy):
        if logx: self.matplotlib.xscale("log")
        if logy: self.matplotlib.yscale("log")

    def format_2d_plot(self):
        from jasmin_cis.plotting.plot import plot_options

        logx = self.plot_args.get("logx", False)
        logy = self.plot_args.get("logy", False)
        if logx or logy:
            self.set_log_scale(logx, logy)
        else:
            self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3,3), axis='both')

        draw_grid = self.plot_args.pop("grid", False)
        if draw_grid: self.matplotlib.grid(True, which="both")

        self.set_font_size()

        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        if self.plot_args["xlabel"] == None: self.plot_args["xlabel"] = ""
        if self.plot_args["ylabel"] == None: self.plot_args["ylabel"] = ""

        if not self.plot_args["title"]: self.plot_args["title"] = ""

        for key in plot_options.keys():
            # Call the method associated with the option
            if key in self.plot_args.keys():
                plot_options[key](self.plot_args[key])

        if len(self.packed_data_items) > 1: self.create_legend()

    def format_3d_plot(self):
        '''
        Sets the fontsize, xlabel, ylabel, title, legend and color bar
        Tries to assign default value if value not specified

        @param data:                    A list of data objects (cubes or ungridded data)
        @param options:                 A dictionary of formatting options constructed using __create_plot_format_options
        @param plot_type:               The plot type (as a string, not a PlotType object)
        @param datagroups:               The list of datagroups from the command line, as a dictionary, containing filename, variable, label etc
        @param colour_bar_orientation:  A string, either 'horizontal' or 'vertical', should have been converted to lowercase by the parser
        '''
        from jasmin_cis.plotting.plot import plot_options

        if self.plot_args is not None:
            logx = self.plot_args.get("logx", False)
            logy = self.plot_args.get("logy", False)
            if logx or logy:
                self.set_log_scale(logx, logy)

            draw_grid = self.plot_args.get("grid")
            if draw_grid: self.matplotlib.grid(True, which="both")

            self.set_font_size()
            # If any of the options have not been specified, then use the defaults
            self.set_default_axis_label("X")
            self.set_default_axis_label("Y")

            if self.plot_args["xlabel"] == None: self.plot_args["xlabel"] = ""
            if self.plot_args["ylabel"] == None: self.plot_args["ylabel"] = ""

            if not self.plot_args["title"]: self.plot_args["title"] = ""

            if not self.plot_args["title"]: self.plot_args["title"] = self.packed_data_items[0].long_name

            for key in plot_options.keys():
            # Call the method associated with the option
                if key in self.plot_args.keys():
                    plot_options[key](self.plot_args[key])

        if not self.plot_args["nocolourbar"]: self.add_color_bar(self.plot_args["logv"], self.mplkwargs["vmin"], self.mplkwargs["vmax"], self.v_range, self.plot_args["cbarorient"], self.packed_data_items[0].units)

        self.draw_coastlines(draw_grid)

        if len(self.packed_data_items) > 1: self.create_legend()

    def set_3daxis_label(self, axis):
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if is_map(self.packed_data_items[0]):
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
                self.plot_args[axislabel] = name + format_units(units)
