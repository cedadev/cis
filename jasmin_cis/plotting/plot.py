'''
Class for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''
from sys import maxint
import logging
import matplotlib.pyplot as plt
from contour_plot import Contour_Plot
from contourf_plot import Contourf_Plot
from heatmap import Heatmap
from line_plot import Line_Plot
from scatter_overlay import Scatter_Overlay
from scatter_plot import Scatter_Plot

def format_units(units):
    if units:
        return " ($" + str(units) + "$)"
    else:
        return ""

class Plotter(object):
    plot_options = { 'title' : plt.title,
                  'xlabel' : plt.xlabel, 
                  'ylabel' : plt.ylabel,
                  'fontsize' : plt.rcParams.update,
                  'logx' : None,
                  'logy' : None,
                  'grid' : None }
    
    default_plot_types = { 1 : 'line',
                           2 : 'heatmap'}

    plot_types = {"contour" : Contour_Plot,
                  "contourf" : Contourf_Plot,
                  "heatmap" : Heatmap,
                  "line": Line_Plot,
                  "scatter_overlay" : Scatter_Overlay,
                  "scatter" : Scatter_Plot}

    def __init__(self, data, plot_type = None, out_filename = None, *args, **kwargs):
        '''
        Constructor for the Plotter
        
        @param data             A list of data objects (either Cubes or UngriddedData)
        @param plot_type        The plot type, as a string
        @param out_filename     The filename to save the plot to
        @param *args            args to be passed into matplotlib
        @param **kwargs         kwargs to be passed into matplotlib
        '''
        self.data = data
        if plot_type is None:
            plot_type = self.__set_default_plot_type()
        self.plot_type = self.plot_types[plot_type]()
        self.out_filename = out_filename
        self.args = args
        self.kwargs = kwargs
        self.num_of_preexisting_plots = 0

        self.__calculate_min_and_max_values()

        self.plots = [] # A list where all the plots will be stored
        self.plot() # Call main method

    def __calculate_min_and_max_values(self):
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

        self.unpacked_data = []

        for item in self.data:
            unpacked = unpack_data_object(item)
            self.unpacked_data.append(unpacked)
            if unpacked["data"].min() < self.kwargs["vmin"] and calculate_min_data:
                self.kwargs["vmin"] = unpacked["data"].min()
            if unpacked["data"].max() > self.kwargs["vmax"] and calculate_max_data:
                self.kwargs["vmax"] = unpacked["data"].max()

    def __get_plot_method(self):
        if self.__is_map():
            from mpl_toolkits.basemap import Basemap
            self.basemap = Basemap()
            plot_method = self.basemap
            self.kwargs["latlon"] = True
        else:
            plot_method = plt
        return plot_method
    
    def __set_font_size(self, options):
        if options["fontsize"] is not None:
            options["fontsize"] = { "font.size" : float(options["fontsize"]) }   
        else:
            options.pop("fontsize")
        return options

    def __is_map(self):
        axes = []
        for coord in self.data[0].coords(axis="X"):
            axes.append(coord.name())
        for coord in self.data[0].coords(axis="Y"):
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

        parallels = __create_set_of_grid_lines("y", self.y_range)
        meridians = __create_set_of_grid_lines("x", self.x_range)

        return parallels, meridians

    def __draw_coastlines(self, draw_grid = False):
        if self.__is_map():
            from mpl_toolkits.basemap import Basemap
            self.basemap = Basemap()
            self.basemap.drawcoastlines()

            parallels, meridians = self.__create_map_grid_lines()
            if draw_grid:
                self.basemap.drawparallels(parallels)
                self.basemap.drawmeridians(meridians)

            meridian_labels = self.__format_map_ticks(meridians, "x")
            parallel_labels = self.__format_map_ticks(parallels, "y")

            plt.xticks(meridians, meridian_labels)
            plt.yticks(parallels, parallel_labels)
    
    def __set_log_scale(self, logx, logy):
        ax = plt.gca()
        if logx:
            ax.set_xscale("log", basex = logx)
        if logy:
            ax.set_yscale("log", basey = logy)
                        
    def __format_plot(self, options, datafiles): 
        '''
        Sets the fontsize, xlabel, ylabel, title, legend and color bar
        Tries to assign default value if value not specified
        
        @param data:                    A list of data objects (cubes or ungridded data)
        @param options:                 A dictionary of formatting options constructed using __create_plot_format_options
        @param plot_type:               The plot type (as a string, not a PlotType object)
        @param datafiles:               The list of datafiles from the command line, as a dictionary, containing filename, variable, label etc
        @param colour_bar_orientation:  A string, either 'horizontal' or 'vertical', should have been converted to lowercase by the parser
        '''
        # When should scientific notation be used on the axes?
        #(m, n), pair of integers; scientific notation will be used for numbers outside the range 10^m to 10^n. Use (0,0) to include all numbers          
        try:
            plt.gca().ticklabel_format(style='sci', scilimits=(-3,3), axis='both')
        except AttributeError:
            pass

        if options is not None:  
            logx = options.pop("logx")
            logy = options.pop("logy")
            if logx or logy: self.__set_log_scale(logx, logy)

            draw_grid = options.pop("grid")
            if draw_grid: plt.grid(True, which="both")
            
            options = self.__set_font_size(options)             
            # If any of the options have not been specified, then use the defaults
            options = self.plot_type.set_axis_label("X", options, self.data)
            options = self.plot_type.set_axis_label("Y", options, self.data)
        
            if options["xlabel"] == None: options["xlabel"] = ""
            if options["ylabel"] == None: options["ylabel"] = ""
                
            if not options["title"]: options["title"] = ""
                
            if self.plot_type != "line" and self.plot_type != "scatter2D" and not options["title"]: options["title"] = self.data[0].long_name
            
            for option, value in options.iteritems():
                # Call the method associated with the option        
                self.plot_options[option](value)

        if len(self.plots) > 1 and not (self.plot_type == "scatteroverlay" and len(self.plots) == 2): self.__create_legend(datafiles)

        if not self.no_colour_bar: self.plot_type.add_color_bar(self.logv, self.kwargs["vmin"], self.kwargs["vmax"], self.v_range, self.colour_bar_orientation, self.data[0].units)
        
        self.__draw_coastlines(draw_grid)
        
    def __set_width_and_height(self):
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

    def __do_plot(self):
        '''
        Goes through all the data objects and plots them
        '''
        datafiles = self.kwargs.pop("datafiles", None) 
        for i, item in enumerate(self.data):
            # Plot the data item using the specified plot type
            self.plots.append(self.plot_type.plot(self.unpacked_data[i], datafiles[i], *self.args, **self.kwargs))
        return datafiles

    def __set_default_plot_type(self):
        '''
        Sets the default plot type based on the number of dimensions of the data
        '''
        from jasmin_cis.exceptions import InvalidPlotTypeError
        variable_dim = len(self.data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
        try:
            if len(self.data) > 1 and variable_dim == 2:
                return 'scatteroverlay'
            else:
                return self.default_plot_types[variable_dim]
        except KeyError:
            raise InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")
    
    def __prepare_range(self, axis):
        '''
        If the axis is for the values and the plot type is not a line graph, then adds the min and max value to the kwargs
        otherwise just returns the valrange as a dictionary containing the min and max value
        
        @param axis    The axis to prepare the range for
        '''
        valrange = self.kwargs.pop(axis + "range", None)     
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
                valrange = None
        return valrange
    
    def __output_to_file_or_screen(self):
        '''
        Outputs to screen unless a filename is given
        
        @param out_filename    The filename of the file to save to
        '''
        if self.out_filename is None:
            plt.show()
        else:
            logging.info("saving plot to file: " + self.out_filename);
            plt.savefig(self.out_filename) # Will overwrite if file already exists
    
    def __remove_unassigned_arguments(self):
        '''
        Removes arguments from the kwargs if they are equal to None
        '''
        for key in self.kwargs.keys():
            if self.kwargs[key] is None:
                self.kwargs.pop(key)
    
    def __create_plot_format_options(self):
        '''
        @return A dictionary containing the kwargs where the key is contained in the plot_options dictionary
        '''
        options = {}
        for key in self.plot_options.keys():
            options[key] = self.kwargs.pop(key, None)
        
        return options
    
    def __apply_axis_limits(self, valrange, axis):
        '''
        @param valrange    A dictionary containing xmin, xmax or ymin, ymax
        @param axis        The axis to apply the limits to
        '''
        from iris.exceptions import CoordinateNotFoundError
        from numpy.ma import MaskedArray
        import numpy
        if valrange is None and self.__is_map():
            valrange = {}
            try:
                valrange[axis + "min"] = MaskedArray.min(self.data[0].coord(axis=axis).data)
                valrange[axis + "max"] = MaskedArray.max(self.data[0].coord(axis=axis).data)
                try:
                    self.valrange[axis] = valrange
                except AttributeError:
                    self.valrange = {}
                    self.valrange[axis] = valrange
            except (CoordinateNotFoundError, AttributeError):
                pass
        if valrange is not None:
            if axis == "x":
                step = valrange.pop("xstep", None)
                plt.xlim(**valrange)
                if step is not None: valrange["xstep"] = step
            elif axis == "y":
                step = valrange.pop("ystep", None)
                plt.ylim(**valrange)
                if step is not None: valrange["ystep"] = step
    
    def plot(self):
        '''
        The main plotting method
        '''

        logging.info("Generating plot...")

        self.kwargs["linewidth"] = self.kwargs.pop("itemwidth", None)        
        self.__remove_unassigned_arguments()

        # Checks are currently not smart enough to perform correctly.
        #self.__validate_data(variable_dim)
        
        plot_format_options = self.__create_plot_format_options()
        self.v_range = self.__prepare_range("val")
        self.x_range = self.__prepare_range("x")
        self.y_range = self.__prepare_range("y")
        self.__set_width_and_height()  
        Plotter.colour_bar_orientation = self.kwargs.pop("cbarorient", "horizontal")  
        self.no_colour_bar = self.kwargs.pop("nocolourbar", False)
        self.logv = self.kwargs.pop("logv", False)
        if self.logv:
            from matplotlib import colors
            self.kwargs["norm"] = colors.LogNorm()
        datafiles = self.__do_plot()  
        self.__apply_axis_limits(self.x_range, "x")
        self.__apply_axis_limits(self.y_range, "y")
            
        self.__format_plot(plot_format_options, datafiles) 
        
        self.__output_to_file_or_screen()        