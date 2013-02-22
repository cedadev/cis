import logging

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
        arg = self.kwargs.pop("color", None)
        if arg is not None:
            logging.warn("Cannot specify a line colour for plot type '" + self.plot_type + "', did you mean to use cmap?")
    else:
        arg = self.kwargs.pop("cmap", None)
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

    # Heatmap overlay self.plots.append(plot_method.scatter(data_item["x"], data_item["y"], c = colour_scheme, cmap=thecm, vmin = minval, vmax = maxval, marker = mark, s = scatter_size, edgecolors = "none", *self.args, **self.kwargs))
    # Heatmap overlay self.plots.append(plot_method.scatter(data_item["x"], data_item["data"], c = colour_scheme, cmap=thecm, vmin = minval, vmax = maxval, marker = mark, s = scatter_size, edgecolors = "none", *self.args, **self.kwargs))
    '''