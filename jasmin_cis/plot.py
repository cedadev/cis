'''
Class for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import sys
from utils import unpack_data_object
import logging


class PlotType(object):
        def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
            self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
            self.variable_dimensions = variable_dimensions
            self.plot_method = plot_method

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
    
    line_styles = ["solid", "dashed", "dashdot", "dotted"]
    
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
        self.plot_type = plot_type
        self.out_filename = out_filename
        self.args = args
        self.kwargs = kwargs
        self.num_of_preexisting_plots = 0
        self.min_data = sys.maxint      # To be used for calculating the colour scheme of a scatter plotter overlayed on a heatmap
        self.max_data = -sys.maxint - 1 # To be used for calculating the colour scheme of a scatter plotter overlayed on a heatmap
        self.plots = [] # A list where all the plots will be stored
        self.plot() # Call main method
    
    def __add_color_bar(self):
        plt.colorbar(orientation = Plotter.colour_bar_orientation, format = "%e")
        # format = "%.3f
        # format = "%.3e
        # format = "%.3g
    
    def plot_line(self, data_item):
        '''
        Plots a line graph
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords and data as arrays
        '''
        self.plots.append(plt.plot(data_item["x"], data_item["data"], *self.args, **self.kwargs ))
    
    def plot_heatmap(self, data_item):
        '''
        Plots a heatmap using Basemap
        Stores the min and max values of the data to be used later on for setting the colour scheme of scatter plots
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        #import matplotlib.colors as colors
        self.min_data = data_item["data"].min()
        self.max_data = data_item["data"].max()
        self.basemap = Basemap()    
        #norm = colors.LogNorm,         
        self.plots.append(self.basemap.pcolormesh(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))

    def plot_heatmap_nobasemap(self, data_item):
        '''
        Plots a heatmap without using basemap
        Stores the min and max values of the data to be used later on for setting the colour scheme of scatter plots
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.min_data = data_item["data"].min()
        self.max_data = data_item["data"].max()

        self.plots.append(plt.pcolormesh(data_item["x"], data_item["y"], data_item["data"], *self.args, **self.kwargs))
        
    def plot_contour(self, data_item):
        '''
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.basemap = Basemap()    
        self.plots.append(self.basemap.contour(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))
        
    def plot_contourf(self, data_item):
        '''
        Plots a filled contour
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.basemap = Basemap()    
        self.plots.append(self.basemap.contourf(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))
    
    def plot_scatter(self, data_item):
        '''
        Plots a scatter plot
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        from math import pow  
        colour_scheme = self.kwargs.get("color", None)
        minval = None
        maxval = None   
        mark = self.kwargs.pop("marker", "o")
        if data_item["data"] is not None: # i.e. the scatter plot is 3D
            minval = data_item["data"].min()
            maxval = data_item["data"].max()
            if self.min_data != sys.maxint and self.max_data != (-sys.maxint - 1): # If a heatmap has been already plotted
                minval = self.min_data
                maxval = self.max_data
            if colour_scheme is None:
                colour_scheme = data_item["data"]
        if colour_scheme is None:
            colour_scheme = "b" # Default color scheme used by matplotlib
        if "linewidth" in self.kwargs.keys():
            scatter_size = self.kwargs["linewidth"]
        else:
            scatter_size = 20 # Default scatter size

        # Code review this
        try:
            x = self.basemap
        except AttributeError:
            self.basemap = Basemap()

        self.plots.append(self.basemap.scatter(data_item["x"], data_item["y"], c = colour_scheme, vmin = minval, vmax = maxval, marker = mark, s = scatter_size))
    
    def plot_scatteroverlay(self, data_item):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        Stores the plot in a list to be used for when adding the legend
        
        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        if self.num_of_preexisting_plots == 0:
            self.kwargs.pop("marker", None)
            self.kwargs["label"] = "_nolegend_"
            self.plot_heatmap(data_item)
            self.kwargs.pop("label")
            if not self.no_colour_bar:
                self.__add_color_bar()
        else:
            self.plot_scatter(data_item)    
        self.num_of_preexisting_plots += 1            

    plot_types = {'line' : PlotType(None, 1, plot_line),
                'scatter' : PlotType(None, 2, plot_scatter), 
                'heatmap' : PlotType(1, 2, plot_heatmap),
                'heatmap_nobasemap' : PlotType(1, 2, plot_heatmap_nobasemap),
                'contour' : PlotType(1, 2, plot_contour),
                'contourf' : PlotType(1, 2, plot_contourf),
                'scatteroverlay' : PlotType(None, 2, plot_scatteroverlay)}
    
    def __set_font_size(self, options):
        if options["fontsize"] is not None:
            options["fontsize"] = { "font.size" : float(options["fontsize"]) }   
        else:
            options.pop("fontsize")
        return options
    
    def __set_x_label(self, options):
        if options["xlabel"] is None and self.plot_type != "heatmap" and self.plot_type != "scatteroverlay":
            for dim in xrange(len(self.data[0].shape)):
                for coord in self.data[0].coords(axis="X"):
                    xlabel = coord.name()
            options["xlabel"] = xlabel.capitalize()
        return options
    
    def __set_y_label(self, options):
        if options["ylabel"] is None and self.plot_type != "heatmap" and self.plot_type != "scatteroverlay":
            if len(self.data) == 1:
                options["ylabel"] = self.data[0].long_name.title()
            else:
                options["ylabel"] = str(self.data[0].units)
        return options
    
    def __create_legend(self, datafiles):
        if len(self.plots) > 1:
            legend_titles = []
            for i, item in enumerate(self.data):
                if datafiles is not None and datafiles[i]["label"]:
                    legend_titles.append(datafiles[i]["label"])
                else:
                    if " " in item.long_name:
                        legend_titles.append(" ".join(item.long_name.title().split()[:-1]))
                    else:
                        legend_titles.append(item.long_name.title())
            if self.plot_type == "line":
                legend = plt.legend(legend_titles, loc="best")
            else:                
                handles = self.plots
                if self.plot_type == "scatteroverlay":
                    handles = handles[1:]
                    legend_titles = legend_titles[1:]
                legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
            legend.draggable(state = True)
    
    def __draw_coastlines(self):
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
            self.basemap.drawcoastlines()
    
    def __set_log_scale(self, logx, logy):
        from numpy import e, log
        ax = plt.gca()
        if logx:
            ax.set_xscale("log", basex = logx) 
            if logx == e:
                xticks = [("e^" + "{0:.0f}".format(x)) for x in log(ax.get_xticks())]
                #xticks = [("$\mathrm{e^(" + "{0:.0f}".format(x) + ")}$") for x in log(ax.get_xticks())]
                ax.set_xticklabels(xticks)
        if logy:
            ax.set_yscale("log", basey = logy)
            if logy == e:
                yticks = [("e^" + "{0:.0f}".format(x)) for x in log(ax.get_yticks())]
                #yticks = [("$\mathrm{e^(" + "{0:.0f}".format(x) + ")}$") for x in log(ax.get_yticks())]
                ax.set_yticklabels(yticks)
                        
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
            plt.gca().ticklabel_format(style='sci', scilimits=(0,3), axis='both')
        except AttributeError:
            pass

        if options is not None:  
            logx = options.pop("logx")
            logy = options.pop("logy")
            if logx or logy:
                self.__set_log_scale(logx, logy)
                
            if options.pop("grid") or logx or logy:
                plt.grid(True, which="both")
            
            options = self.__set_font_size(options)             
            # If any of the options have not been specified, then use the defaults
            options = self.__set_x_label(options)
            options = self.__set_y_label(options)
        
            if options["xlabel"] == None:
                options["xlabel"] = ""
            if options["ylabel"] == None:
                options["ylabel"] = ""
                
            if not options["title"]:
                options["title"] = ""
                
            if self.plot_type != "line" and not options["title"]:
                    options["title"] = self.data[0].long_name.title()            
            
            for option, value in options.iteritems():
                # Call the method associated with the option        
                self.plot_options[option](value)      
                 
        if self.plot_type == "line" or "scatter" in self.plot_type:
            self.__create_legend(datafiles)
        else:
            if not self.no_colour_bar:
                self.__add_color_bar()
        
        self.__draw_coastlines()
        
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
    
    def __add_datafile_args_to_kwargs(self, datafile):
        '''
        Add linestyle/marker and color to kwargs just before plotting
        '''
        if self.plot_type == "line" or "scatter" in self.plot_type:
            if datafile["itemstyle"]:
                if self.plot_type == "line":
                    if datafile["itemstyle"] not in Plotter.line_styles:
                        from exceptions import InvalidLineStyleError
                        raise InvalidLineStyleError("'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(Plotter.line_styles))
                    else:
                        self.kwargs["linestyle"] = datafile["itemstyle"]
                elif "scatter" in self.plot_type:
                    self.kwargs["marker"] = datafile["itemstyle"]
            if datafile["color"]:
                self.kwargs["color"] = datafile["color"]
                        
    def __remove_datafile_args_from_kwargs(self, datafile):
        '''
        Removes linestyle/marker and color from kwargs just after plotting
        '''
        if self.plot_type == "line" or "scatter" in self.plot_type:
            if datafile["itemstyle"]:
                if self.plot_type == "line":
                    self.kwargs.pop("linestyle")
                elif "scatter" in self.plot_type:
                    self.kwargs.pop("marker", None)
            if datafile["color"]:
                self.kwargs.pop("color")
    
    def __do_plot(self):
        '''
        Goes through all the data objects and plots them
        '''
        datafiles = self.kwargs.pop("datafiles", None) 
        for i, item in enumerate(self.data):

            # Temporarily add args to kwargs
            if datafiles is not None:
                self.__add_datafile_args_to_kwargs(datafiles[i])
            item_to_plot = unpack_data_object(item)            

            # for heatmaps, we plot the world map (with basemap)
            # if the 'x' axis is longitude AND the 'y' axis is the latitude
            if self.plot_type == "heatmap":
                if item.y.standard_name == "latitude" and item.x.standard_name == "longitude":
                    Plotter.plot_types["heatmap"].plot_method(self, item_to_plot)
                else:
                    Plotter.plot_types["heatmap_nobasemap"].plot_method(self, item_to_plot)
            else:              
                Plotter.plot_types[self.plot_type].plot_method(self, item_to_plot)

            # Remove temp args
            if datafiles is not None:
                self.__remove_datafile_args_from_kwargs(datafiles[i])
        return datafiles
    
    def __warn_if_incorrect_colour_type_used(self):
        '''
        A 'color' should only be specified for a line graph, and 'cmap' should be specified for every other plot type
        '''
        import logging
        if self.plot_type != "line": # Remove color if specified for plot where type is not line
            arg = self.kwargs.pop("color", None)
            if arg is not None:
                logging.warn("Cannot specify a line colour for plot type '" + self.plot_type + "', did you mean to use cmap?")
        else:
            arg = self.kwargs.pop("cmap", None)
            if arg is not None:
                logging.warn("Cannot specify a colour map for plot type '" + self.plot_type + "', did you mean to use color?")
    
    def __set_default_plot_type(self, variable_dim):
        '''
        Sets the default plot type based on the number of dimensions of the data
        '''
        from jasmin_cis.exceptions import InvalidPlotTypeError
        try:
            if len(self.data) > 1 and variable_dim == 2:
                self.plot_type = 'scatteroverlay'
            else:
                self.plot_type = self.default_plot_types[variable_dim]
        except KeyError:
            raise InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")
    
    def __check_plot_type_is_valid_for_given_variable(self, variable_dim):
        from jasmin_cis.exceptions import InvalidPlotTypeError
        if self.plot_types[self.plot_type].variable_dimensions != variable_dim:
            raise InvalidPlotTypeError("The plot type is not valid for this variable, the dimensions do not match")
    
    def __check_all_data_items_are_of_same_shape(self, variable_dim):
        from jasmin_cis.exceptions import InconsistentDimensionsError
        for item in self.data:
            if len(item.shape) != variable_dim:
                raise InconsistentDimensionsError("Number of dimensions must be consistent across variables")
    
    def __check_number_of_variables_does_not_exceed_maximum(self):
        from jasmin_cis.exceptions import InvalidPlotTypeError
        if self.plot_types[self.plot_type].maximum_no_of_expected_variables is not None:
            if len(self.data) > self.plot_types[self.plot_type].maximum_no_of_expected_variables:
                raise InvalidPlotTypeError("The plot type is not valid for this number of variables") # else: There are an unlimited number of variables for this plot type
    
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
    
    def __output_to_file_or_screen(self, out_filename = None):
        '''
        Outputs to screen unless a filename is given
        
        @param out_filename    The filename of the file to save to
        '''
        if out_filename is None:
            plt.show()
        else:
            logging.info("saving plot to file: " + out_filename);
            plt.savefig(out_filename) # Will overwrite if file already exists
    
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
        if valrange is not None:
            if axis == "x":
                plt.xlim(**valrange)
            elif axis == "y":
                plt.ylim(**valrange)
    
    def __validate_data(self, variable_dim):
        '''
        Used to validate the data before plotting
        
        @param variable_dim:    The number of dimensions of the data being plotted
        '''
        self.__check_all_data_items_are_of_same_shape(variable_dim)
        self.__check_plot_type_is_valid_for_given_variable(variable_dim)
        self.__warn_if_incorrect_colour_type_used()
        self.__check_number_of_variables_does_not_exceed_maximum()
    
    def plot(self):
        '''
        The main plotting method
        '''

        logging.info("Generating plot... This may take some time")

        self.kwargs["linewidth"] = self.kwargs.pop("itemwidth", None)        
        self.__remove_unassigned_arguments()   

        variable_dim = len(self.data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
        
        if self.plot_type is None:
            self.__set_default_plot_type(variable_dim)

        # Checks are currently not smart enough to perform correctly.
        #self.__validate_data(variable_dim)
        
        plot_format_options = self.__create_plot_format_options()
        self.__prepare_range("val")
        x_range = self.__prepare_range("x")  
        y_range = self.__prepare_range("y")
        self.__set_width_and_height()  
        Plotter.colour_bar_orientation = self.kwargs.pop("cbarorient", "horizontal")  
        self.no_colour_bar = self.kwargs.pop("nocolourbar", False)
        datafiles = self.__do_plot()  
        self.__apply_axis_limits(x_range, "x")
        self.__apply_axis_limits(y_range, "y")
            
        self.__format_plot(plot_format_options, datafiles) 
        
        self.__output_to_file_or_screen()        