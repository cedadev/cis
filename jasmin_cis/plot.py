'''
Class for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''

import matplotlib.pyplot as plt
from data_io.netcdf import unpack_data_object
from mpl_toolkits.basemap import Basemap
import sys

class PlotType(object):
        def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
            self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
            self.variable_dimensions = variable_dimensions
            self.plot_method = plot_method

class Plotter(object):
    plot_options = { 'title' : plt.title,
                  'xlabel' : plt.xlabel, 
                  'ylabel' : plt.ylabel,
                  'fontsize' : plt.rcParams.update }
    
    default_plot_types = { 1 : 'line',
                           2 : 'heatmap'}
    
    line_styles = ["solid", "dashed", "dashdot", "dotted"]
    
    def __init__(self, data, plot_type = None, out_filename = None, *args, **kwargs):
        self.data = data
        self.plot_type = plot_type
        self.out_filename = out_filename
        self.args = args
        self.kwargs = kwargs
        self.num_of_preexisting_plots = 0
        self.min_data = sys.maxint
        self.max_data = -sys.maxint - 1
        self.plots = []
        self.plot() # Call main method
    
    def plot_line(self, data_item):
        '''
        Plots a line graoh
        
        @param data:    A dictionary containing the x coords and data as arrays
        '''
        self.plots.append(plt.plot(data_item["x"], data_item["data"], *self.args, **self.kwargs ))
    
    def plot_heatmap(self, data_item):
        '''
        Plots a heatmap
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        import numpy as np    
        self.min_data = np.min(data_item["data"])
        self.max_data = np.max(data_item["data"])
        self.basemap = Basemap()    
        self.plots.append(self.basemap.pcolormesh(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))

    def plot_heatmap_nobasemap(self, data_item):
        '''
        Plots a heatmap
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        import numpy as np    
        self.min_data = np.min(data_item["data"])
        self.max_data = np.max(data_item["data"])
        self.plots.append(plt.pcolormesh(data_item["x"], data_item["y"], data_item["data"], *self.args, **self.kwargs))
        
    def plot_contour(self, data_item):
        '''
        Plots a contour plot
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.basemap = Basemap()    
        self.plots.append(self.basemap.contour(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))
        
    def plot_contourf(self, data_item):
        '''
        Plots a filled contour
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.basemap = Basemap()    
        self.plots.append(self.basemap.contourf(data_item["x"], data_item["y"], data_item["data"], latlon = True, *self.args, **self.kwargs))
    
    def plot_scatter(self, data_item):
        '''
        Plots a scatter plot
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        from math import pow  
        colour_scheme = self.kwargs.get("color", None)
        minval = None
        maxval = None   
        mark = self.kwargs.pop("marker", "o") 
        if data_item["data"] is not None:
            import numpy as np
            minval = np.min(data_item["data"])
            maxval = np.max(data_item["data"])
            if self.min_data != sys.maxint and self.max_data != (-sys.maxint - 1):
                minval = self.min_data
                maxval = self.max_data
            if colour_scheme is None:
                colour_scheme = data_item["data"]
        if colour_scheme is None:
            colour_scheme = "b"
        self.plots.append(plt.scatter(data_item["x"], data_item["y"], s = pow(self.kwargs["linewidth"], 2), c = colour_scheme, vmin = minval, vmax = maxval, marker = mark))
    
    def plot_scatteroverlay(self, data_item):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        
        @param data:    A dictionary containing the x coords, y coords and data as arrays
        '''
        if self.num_of_preexisting_plots == 0:
            self.kwargs.pop("marker", None)
            self.kwargs["label"] = "_nolegend_"
            self.plot_heatmap(data_item)
            self.kwargs.pop("label")
            plt.colorbar(orientation = Plotter.colour_bar_orientation)
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
        if options["xlabel"] is None:
            for dim in xrange(len(self.data[0].shape)):
                for coord in self.data[0].coords(contains_dimension=dim, dim_coords=True):
                    xlabel = coord.name()
            options["xlabel"] = xlabel.capitalize()
        return options
    
    def __set_y_label(self, options):
        if options["ylabel"] is None:
            if len(self.data) == 1:
                options["ylabel"] = self.data[0].long_name.title()
            else:
                options["ylabel"] = str(self.data[0].units)
        return options
    
    def __create_legend(self, datafiles):
        legend_titles = []
        for i, item in enumerate(self.data):
            if datafiles is not None and datafiles[i]["label"]:
                legend_titles.append(datafiles[i]["label"])
            else:
                legend_titles.append(" ".join(item.long_name.title().split()[:-1]))
        handles = self.plots
        if self.plot_type == "scatteroverlay":
            handles = handles[1:]
            legend_titles = legend_titles[1:]
        legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)
    
    def __draw_coastlines(self):
        axes = []
        for dim in xrange(len(self.data[0].shape)):
            for coord in self.data[0].coords(contains_dimension=dim, dim_coords=True):
                axes.append(coord.name())
        
        if "latitude" in axes and "longitude" in axes:
            self.basemap.drawcoastlines()
                        
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
        if options is not None:  
            options = self.__set_font_size(options)             
            # If any of the options have not been specified, then use the defaults
            if self.plot_type == "line":
                options = self.__set_x_label(options)
                options = self.__set_y_label(options)
            else:
                options["xlabel"] = ""
                options["ylabel"] = ""
                
            if not options["title"]:
                options["title"] = ""
                
            if self.plot_type != "line" and not options["title"]:
                    options["title"] = self.data[0].long_name.title()            
            
            for option, value in options.iteritems():        
                self.plot_options[option](value)      
                 
        if self.plot_type == "line" or "scatter" in self.plot_type:
            self.__create_legend(datafiles)
        else:
            plt.colorbar(orientation = Plotter.colour_bar_orientation)
        
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
        @param data:        A list of data objects (cubes or ungridded data)
        @param plot_type:   The plot type, as a string, not a PlotType object
        '''
        datafiles = self.kwargs.pop("datafiles", None) 
        for i, item in enumerate(self.data):
            # Temporarily add args to kwargs
            if datafiles is not None:
                self.__add_datafile_args_to_kwargs(datafiles[i])
            item_to_plot = unpack_data_object(item)            
            if self.plot_type == "heatmap":
                names = []
                for dim in xrange(len(item.shape)):
                    for coord in item.coords(contains_dimension=dim, dim_coords=True):
                        names.append(coord.name().lower())
                if "latitude" in names and "longitude" in names:
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
    
    def __prepare_val_range(self):
        valrange = self.kwargs.pop("valrange", None)
        
        if self.plot_type != "line" and valrange is not None:
            try:
                self.kwargs["vmin"] = valrange.pop("ymin")
            except KeyError:
                pass
            
            try:
                self.kwargs["vmax"] = valrange.pop("ymax")
            except KeyError:
                pass
            
        return valrange
    
    def __output_to_file_or_screen(self, out_filename = None):
        '''
        Outputs to screen unless a filename is given
        '''
        if out_filename is None:
            plt.show()
        else:
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
    
    def __apply_line_graph_value_limits(self, valrange):
        if self.plot_type == "line" and valrange is not None:
            plt.ylim(**valrange)
    
    def __validate_data(self, variable_dim):
        '''
        Used to validate the data before plotting
        
        @param data:             A list of data objects
        @param plot_type:        The plot type, as a string, not as a PlotType object
        @param varaiable_dim:    The number of dimensions of the data being plotted
        '''
        self.__check_all_data_items_are_of_same_shape(variable_dim)
        self.__check_plot_type_is_valid_for_given_variable(variable_dim)
        self.__warn_if_incorrect_colour_type_used()
        self.__check_number_of_variables_does_not_exceed_maximum()
    
    def plot(self):
        '''
        The main plotting method
        
        @param data:         A list of data objects (cubes or ungridded data objects)
        @param plot_type:    The type of the plot to be plotted. A default will be chosen if omitted
        @param out_filename: The filename of the file to save the plot to
        '''
        self.kwargs["linewidth"] = self.kwargs.pop("itemwidth", None)        
        self.__remove_unassigned_arguments()   
           
        variable_dim = len(self.data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
        
        if self.plot_type is None:
            self.__set_default_plot_type(variable_dim)
        
        self.__validate_data(variable_dim)
        
        plot_format_options = self.__create_plot_format_options()
        valrange = self.__prepare_val_range()  
        self.__set_width_and_height()  
        Plotter.colour_bar_orientation = self.kwargs.pop("cbarorient", "horizontal")  
        datafiles = self.__do_plot()  
        self.__apply_line_graph_value_limits(valrange)
            
        self.__format_plot(plot_format_options, datafiles) 
        
        self.__output_to_file_or_screen()        