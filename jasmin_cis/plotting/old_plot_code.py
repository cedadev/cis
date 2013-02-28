import logging

def __format_plot(self, options, datagroups):
    '''
    Sets the fontsize, xlabel, ylabel, title, legend and color bar
    Tries to assign default value if value not specified

    @param data:                    A list of data objects (cubes or ungridded data)
    @param options:                 A dictionary of formatting options constructed using __create_plot_format_options
    @param plot_type:               The plot type (as a string, not a PlotType object)
    @param datagroups:               The list of datagroups from the command line, as a dictionary, containing filename, variable, label etc
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

    if len(self.plots) > 1 : self.__create_legend(datagroups)

    if not self.no_colour_bar: self.plot_type.add_color_bar(self.logv, self.mplkwargs["vmin"], self.mplkwargs["vmax"], self.v_range, self.colour_bar_orientation, self.data[0].units)

    self.__draw_coastlines(draw_grid)

class PlotType(object):
    def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
        self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method

def __check_number_of_variables_does_not_exceed_maximum(self):
    from jasmin_cis.exceptions import InvalidPlotTypeError
    if self.plot_types[self.plot_type].maximum_no_of_expected_variables is not None:
        if len(self.data) > self.plot_types[self.plot_type].maximum_no_of_expected_variables:
            raise InvalidPlotTypeError("The plot type is not valid for this number of variables") # else: There are an unlimited number of variables for this plot type

def __warn_if_incorrect_colour_type_used(self):
    '''
    A 'color' should only be specified for a line graph, and 'cmap' should be specified for every other plot type
    '''
    if self.plot_type != "line": # Remove color if specified for plot where type is not line
        arg = self.mplkwargs.pop("color", None)
        if arg is not None:
            logging.warn("Cannot specify a line colour for plot type '" + self.plot_type + "', did you mean to use cmap?")
    else:
        arg = self.mplkwargs.pop("cmap", None)
        if arg is not None:
            logging.warn("Cannot specify a colour map for plot type '" + self.plot_type + "', did you mean to use color?")

def __check_plot_type_is_valid_for_given_variable(self, variable_dim):
    from jasmin_cis.exceptions import InvalidPlotTypeError
    if self.plot_types[self.plot_type].variable_dimensions != variable_dim:
        raise InvalidPlotTypeError("The plot type is not valid for this variable, the dimensions do not match")

def __check_all_data_items_are_of_same_shape(self, variable_dim):
    from jasmin_cis.exceptions import InconsistentDimensionsError
    for item in self.data:
        if len(item.shape) != variable_dim:
            raise InconsistentDimensionsError("Number of dimensions must be consistent across variables")

def __validate_data(self, variable_dim):
    '''
    Used to validate the data before plotting
    
    @param variable_dim:    The number of dimensions of the data being plotted
    '''
    self.__check_all_data_items_are_of_same_shape(variable_dim)
    self.__check_plot_type_is_valid_for_given_variable(variable_dim)
    self.__warn_if_incorrect_colour_type_used()
    self.__check_number_of_variables_does_not_exceed_maximum()

    '''
    Heatmap overlay
    import matplotlib.cm as cm
    #thecm = cm.get_cmap("Accent")
    thecm = cm.get_cmap("Greys")
    thecm._init()

    import numpy as np
    alphas = np.arange(256)/256.0
    thecm._lut[:-3,-1] = alphas

    # Heatmap overlay self.plots.append(plot_method.scatter(data_item["x"], data_item["y"], c = colour_scheme, cmap=thecm, vmin = minval, vmax = maxval, marker = mark, s = scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs))
    # Heatmap overlay self.plots.append(plot_method.scatter(data_item["x"], data_item["data"], c = colour_scheme, cmap=thecm, vmin = minval, vmax = maxval, marker = mark, s = scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs))
    '''