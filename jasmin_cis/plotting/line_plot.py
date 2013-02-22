import matplotlib.pyplot as plt

class PlotType(object):
    def __init__(self, maximum_no_of_expected_variables, variable_dimensions, plot_method):
        self.maximum_no_of_expected_variables = maximum_no_of_expected_variables
        self.variable_dimensions = variable_dimensions
        self.plot_method = plot_method

class Line_Plot(object):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]
    #'line' : PlotType(None, 1, plot_line),
    def add_color_bar(self):
        pass

    def set_axis_label(self, axis, options, data):
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            try:
                name = data[0].coord(axis=axis).name()
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                name = data[0].name()

            try:
                units = data[0].coord(axis=axis).units
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                units = data[0].units

            if len(data) == 1:
                # only 1 data to plot, display
                options[axislabel] = name + format_units(units)
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                options[axislabel] = units

        return options

    def create_legend(self, datafiles):
        legend_titles = []
        for i, item in enumerate(self.data):
            if datafiles is not None and datafiles[i]["label"]:
                legend_titles.append(datafiles[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = plt.legend(legend_titles, loc="best")
        legend.draggable(state = True)

    def plot(self, data_item, datafile, *args, **kwargs):
        '''
        Plots a line graph
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords and data as arrays
        '''

        new_kwargs = kwargs
        new_kwargs.pop("vmin", None)
        new_kwargs.pop("vmax", None)
        if datafile["itemstyle"]:
            if datafile["itemstyle"] not in Line_Plot.line_styles:
                from exceptions import InvalidLineStyleError
                raise InvalidLineStyleError("'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(Plotter.line_styles))
            else:
                self.kwargs["linestyle"] = datafile["itemstyle"]
        if datafile["color"]:
            self.kwargs["color"] = datafile["color"]

        return plt.plot(data_item["x"], data_item["data"], *args, **kwargs )

    def add_color_bar(self, logv, vmin, vmax, v_range, colour_bar_orientation, units):
        pass

