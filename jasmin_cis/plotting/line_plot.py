from generic_plot import Generic_Plot

class Line_Plot(Generic_Plot):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]
    #'line' : PlotType(None, 1, plot_line),

    def plot(self):
        '''
        Plots a line graph
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords and data as arrays
        '''
        self.mplkwargs["linewidth"] = self.plot_args.get("itemwidth", 1)

        self.mplkwargs.pop("vmax", None)
        self.mplkwargs.pop("vmin", None)

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.plot_args["datagroups"][i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in Line_Plot.line_styles:
                    self.mplkwargs["linestyle"] = datafile["itemstyle"]
                else:
                    from jasmin_cis.exceptions import InvalidLineStyleError
                    raise InvalidLineStyleError("'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(Plotter.line_styles))
            else:
                self.mplkwargs["linestyle"] = "-"

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs["color"] = "b"

            self.matplotlib.plot(unpacked_data_item["x"], unpacked_data_item["data"], *self.mplargs, **self.mplkwargs ) #TODO append to list


    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            try:
                units = self.packed_data_items[0].coord(axis=axis).units
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                units = self.packed_data_items[0].units

            if len(self.packed_data_items) == 1:
                try:
                    name = self.packed_data_items[0].coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()
                # only 1 data to plot, display
                self.plot_args[axislabel] = name + format_units(units)
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                self.plot_args[axislabel] = format_units(units)

