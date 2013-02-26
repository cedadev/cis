from generic_plot import Generic_Plot

class Line_Plot(Generic_Plot):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]
    #'line' : PlotType(None, 1, plot_line),

    def plot(self, datafile):
        '''
        Plots a line graph
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords and data as arrays
        '''
        self.mplkwargs["linewidth"] = self.mplkwargs.pop("itemwidth", 1)

        self.mplkwargs.pop("vmax", None)
        self.mplkwargs.pop("vmin", None)

        if datafile["itemstyle"]:
            if datafile["itemstyle"] not in Line_Plot.line_styles:
                from exceptions import InvalidLineStyleError
                raise InvalidLineStyleError("'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(Plotter.line_styles))
            else:
                self.mplkwargs["linestyle"] = datafile["itemstyle"]
        if datafile["color"]:
            self.mplkwargs["color"] = datafile["color"]

        self.matplotlib.plot(self.unpacked_data_item["x"], self.unpacked_data_item["data"], *self.mplargs, **self.mplkwargs ) #TODO append to list


    def format_plot(self, options):
        self.format_2d_plot(options)


    def set_default_axis_label(self, axis, options):
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            try:
                name = self.packed_data_item.coord(axis=axis).name()
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                name = self.packed_data_item.name()

            try:
                units = self.packed_data_item.coord(axis=axis).units
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                units = self.packed_data_item.units

            if self.number_of_data_items == 1:
                # only 1 data to plot, display
                options[axislabel] = name + format_units(units)
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                options[axislabel] = units

        return options

