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

    def set_font_size(self, options):
        if options.get("fontsize", None) is not None:
            options["fontsize"] = { "font.size" : float(options["fontsize"]) }
        else:
            options.pop("fontsize", None)
        return options

    def __init__(self, packed_data_item, v_range, number_of_data_items, plot_args, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.plot_args = plot_args
        self.number_of_data_items = number_of_data_items
        self.packed_data_item = packed_data_item
        self.calculate_min_and_max_values()
        self.basemap = Basemap()
        self.matplotlib = plt
        self.v_range = v_range

        if is_map(packed_data_item):
            self.plot_method = self.basemap
            self.kwargs["latlon"] = True
        else:
            self.plot_method = self.matplotlib

    def plot(self, data_item, datafile, *args, **kwargs):
        raise NotImplementedError()


    def calculate_min_and_max_values(self):
        from sys import maxint
        from utils import unpack_data_object
        self.kwargs["vmin"] = self.kwargs.get("vmin", maxint)
        self.kwargs["vmax"] = self.kwargs.get("vmax", -maxint - 1)

        if self.kwargs["vmin"] == maxint:
            calculate_min_data = True
        else:
            calculate_min_data = False
        if self.kwargs["vmax"] == -maxint - 1:
            calculate_max_data = True
        else:
            calculate_max_data = False

        self.unpacked_data_item = unpack_data_object(self.packed_data_item)
        if self.unpacked_data_item["data"].min() < self.kwargs["vmin"] and calculate_min_data:
            self.kwargs["vmin"] = self.unpacked_data_item["data"].min()
        if self.unpacked_data_item["data"].max() > self.kwargs["vmax"] and calculate_max_data:
            self.kwargs["vmax"] = self.unpacked_data_item["data"].max()


    def add_color_bar(self, logv, vmin, vmax, v_range, orientation, units):
        from plot import format_units
        # nformat = "%e"
        # nformat = "%.3f"
        # nformat = "%.3e"
        nformat = "%.3g"

        if not logv:
            try:
                step = v_range.get("vstep", (vmax-vmin) / 5)
            except AttributeError:
                step = (vmax-vmin) / 5
            ticks = []
            tick = vmin
            while tick <= vmax:
                ticks.append(tick)
                tick = tick + step
        else:
            ticks = None

        cbar = plt.colorbar(orientation = orientation, ticks = ticks, format = nformat)

        cbar.set_label(format_units(units))

    def set_axis_label(self, axis, options, data):
        raise NotImplementedError()

    def create_legend(self, data, datagroups):
        raise NotImplementedError()















    def draw_coastlines(self, draw_grid = False):
        if is_map(self.packed_data_item):
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
                        lines = arange(-180, 181, grid_spacing)

            if lines is None:
                if step is None: step = (max_val-min_val)/24
                lines = arange(min_val, max_val+1, step)
                if min_val < 0 and max_val > 0: lines = append(lines, 0)
                lines.sort()

            return lines

        parallels = __create_set_of_grid_lines("y", self.plot_args["y_range"])
        meridians = __create_set_of_grid_lines("x", self.plot_args["x_range"])

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
        ax = plt.gca()
        if logx:
            ax.set_xscale("log", basex = logx)
        if logy:
            ax.set_yscale("log", basey = logy)

    def format_2d_plot(self, plot_format_options):
        from jasmin_cis.plotting.plot import plot_options
        #BEGIN FORMAT PLOT
        self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3,3), axis='both')
        logx = plot_format_options.pop("logx", False)
        logy = plot_format_options.pop("logy", False)
        if logx or logy: self.set_log_scale(logx, logy)

        draw_grid = plot_format_options.pop("grid", False)
        if draw_grid: self.matplotlib.grid(True, which="both")

        plot_format_options = self.set_font_size(plot_format_options)


        # If any of the options have not been specified, then use the defaults
        plot_format_options = self.set_default_axis_label("X", plot_format_options)
        plot_format_options = self.set_default_axis_label("Y", plot_format_options)

        if plot_format_options["xlabel"] == None: plot_format_options["xlabel"] = ""
        if plot_format_options["ylabel"] == None: plot_format_options["ylabel"] = ""

        if not plot_format_options["title"]: plot_format_options["title"] = ""

        for key in plot_options.keys():
            # Call the method associated with the option
            if key in plot_format_options.keys():
                plot_options[key](plot_format_options[key])

        #END FORMAT PLOT

    def format_3d_plot(self, options):
        from jasmin_cis.plotting.plot import plot_options
        '''
        Sets the fontsize, xlabel, ylabel, title, legend and color bar
        Tries to assign default value if value not specified

        @param data:                    A list of data objects (cubes or ungridded data)
        @param options:                 A dictionary of formatting options constructed using __create_plot_format_options
        @param plot_type:               The plot type (as a string, not a PlotType object)
        @param datagroups:               The list of datagroups from the command line, as a dictionary, containing filename, variable, label etc
        @param colour_bar_orientation:  A string, either 'horizontal' or 'vertical', should have been converted to lowercase by the parser
        '''

        if options is not None:
            logx = options.pop("logx")
            logy = options.pop("logy")
            draw_grid = options.pop("grid")

            options = self.set_font_size(options)
            # If any of the options have not been specified, then use the defaults
            options = self.set_axis_label("X", options)
            options = self.set_axis_label("Y", options)

            if options["xlabel"] == None: options["xlabel"] = ""
            if options["ylabel"] == None: options["ylabel"] = ""

            if not options["title"]: options["title"] = ""

            if not options["title"]: options["title"] = self.packed_data_item.long_name

            for option, value in options.iteritems():
                # Call the method associated with the option
                plot_options[option](value)

        if not self.plot_args["nocolourbar"]: self.add_color_bar(self.plot_args["logv"], self.kwargs["vmin"], self.kwargs["vmax"], self.v_range, self.plot_args["cbarorient"], self.packed_data_item.units)

        self.draw_coastlines(draw_grid)

    def set_3daxis_label(self, axis, options):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if is_map(self.packed_data_item):
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_item.coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_item.name()

                try:
                    units = self.packed_data_item.coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_item.units

                # in general, display both name and units in brackets
                options[axislabel] = name + self.__format_units(units)

        return options
