'''
Class for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''
import logging
from contour_plot import Contour_Plot
from contourf_plot import Contourf_Plot
from heatmap import Heatmap
from line_plot import Line_Plot
from scatter_overlay import Scatter_Overlay
from scatter_plot import Scatter_Plot
from generic_plot import is_map
import matplotlib.pyplot as mpl

def format_units(units):
    if units:
        return " ($" + str(units) + "$)"
    else:
        return ""

plot_options = { 'title' : mpl.title,
                 'xlabel' : mpl.xlabel,
                 'ylabel' : mpl.ylabel,
                 'fontsize' : mpl.rcParams.update }

class Plotter(object):

    
    default_plot_types = { 1 : 'line',
                           2 : 'heatmap'}

    plot_types = {"contour" : Contour_Plot,
                  "contourf" : Contourf_Plot,
                  "heatmap" : Heatmap,
                  "line": Line_Plot,
                  "scatter_overlay" : Scatter_Overlay,
                  "scatter" : Scatter_Plot}

    def __init__(self, packed_data_items, plot_args, plot_type = None, out_filename = None, *args, **kwargs):
        '''
        Constructor for the Plotter
        
        @param data             A list of data objects (either Cubes or UngriddedData)
        @param plot_type        The plot type, as a string
        @param out_filename     The filename to save the plot to
        @param *args            args to be passed into matplotlib
        @param **kwargs         kwargs to be passed into matplotlib
        '''
        self.kwargs = kwargs
        self.remove_unassigned_arguments()

        self.packed_data_items = packed_data_items
        v_range = self.prepare_range("val")
        self.out_filename = out_filename

        if plot_args.pop("logv", False):
            from matplotlib.colors import LogNorm
            self.kwargs["norm"] = LogNorm()

        if plot_type is None: plot_type = self.__set_default_plot_type(packed_data_items)

        self.set_width_and_height()

        plots = [] # A list where all the plots will be stored
        for i, item in enumerate(self.packed_data_items):
            # Plot the data item using the specified plot type
            plot = self.plot_types[plot_type](item, v_range, len(self.packed_data_items), plot_args, *args, **kwargs)
            plots.append(plot.plot(plot_args["datafiles"][i]))
            plot.format_plot(plot_args)

        self.apply_axis_limits(plot_args["x_range"], "x")
        self.apply_axis_limits(plot_args["y_range"], "y")

        #self.format_plot(self.plot_format_options)
        if len(plots) > 1:  self.create_legend(plot_args["datafiles"])

        self.output_to_file_or_screen()

    def create_legend(self, datafiles):
        legend_titles = []
        for i, item in enumerate(self.packed_data_items):
            if datafiles is not None and datafiles[i]["label"]:
                legend_titles.append(datafiles[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = mpl.legend(legend_titles, loc="best")
        legend.draggable(state = True)

    def output_to_file_or_screen(self):
        '''
        Outputs to screen unless a filename is given

        @param out_filename    The filename of the file to save to
        '''
        import logging

        if self.out_filename is None:
            mpl.show()
        else:
            logging.info("saving plot to file: " + self.out_filename);
            mpl.savefig(self.out_filename) # Will overwrite if file already exists

    def zoom_in_on_heatmap(self, axis):
        from iris.exceptions import CoordinateNotFoundError
        valrange = {}
        try:
            valrange[axis + "min"] = self.packed_data_items[0].coord(axis=axis).data.min()
            valrange[axis + "max"] = self.packed_data_items[0].coord(axis=axis).data.max()
            try:
                self.valrange[axis] = valrange
            except AttributeError:
                self.valrange = {}
                self.valrange[axis] = valrange
        except (CoordinateNotFoundError, AttributeError):
            pass

    def apply_user_specified_axis_limits(self, axis, valrange):
        if axis == "x":
            step = valrange.pop("xstep", None)
            mpl.xlim(**valrange)
            if step is not None: valrange["xstep"] = step
        elif axis == "y":
            step = valrange.pop("ystep", None)
            mpl.ylim(**valrange)
            if step is not None: valrange["ystep"] = step

    def apply_axis_limits(self, valrange, axis):
        '''
        @param valrange    A dictionary containing xmin, xmax or ymin, ymax
        @param axis        The axis to apply the limits to
        '''
        if valrange is None and is_map(self.packed_data_items[0]): #Zoom in on heatmap
            self.zoom_in_on_heatmap(axis)

        if valrange is not None: # apply user specified range
            self.apply_user_specified_axis_limits(axis, valrange)

    def set_width_and_height(self):
        '''
        Sets the width and height of the plot
        Uses an aspect ratio of 4:3 if only one of width and height are specified
        '''
        height = self.kwargs.pop("height", None)
        width = self.kwargs.pop("width", None)

        if height is not None:
            if width is None:
                width = height * (4.0 / 3.0)
        elif width is not None:
            height = width * (3.0 / 4.0)

        if height is not None and width is not None:
            plt.figure(figsize = (width, height))

    def remove_unassigned_arguments(self):
        '''
        Removes arguments from the kwargs if they are equal to None
        '''
        for key in self.kwargs.keys():
            if self.kwargs[key] is None:
                self.kwargs.pop(key)

    def prepare_range(self, axis):
        '''
        If the axis is for the values and the plot type is not a line graph, then adds the min and max value to the kwargs
        otherwise just returns the valrange as a dictionary containing the min and max value

        @param axis    The axis to prepare the range for
        '''
        valrange = self.kwargs.pop(axis + "range", None)
        '''
        if axis == "val" and self.plot_type != "line" and valrange is not None:
            try:
                self.kwargs["vmin"] = valrange.pop("vmin")
            except KeyError:
                pass

            try:
                self.kwargs["vmax"] = valrange.pop("vmax")
            except KeyError:
                pass
            if valrange == {}:
                valrange = None'''
        return valrange

    def __set_default_plot_type(self, data):
        '''
        Sets the default plot type based on the number of dimensions of the data
        '''
        from jasmin_cis.exceptions import InvalidPlotTypeError
        variable_dim = len(data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
        try:
            if len(data) > 1 and variable_dim == 2:
                return 'scatteroverlay'
            else:
                return self.default_plot_types[variable_dim]
        except KeyError:
            raise InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")