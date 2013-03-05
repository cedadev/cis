from jasmin_cis.plotting.generic_plot import Generic_Plot

class Histogram_3D(Generic_Plot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]
    def plot(self):
        '''
        Plots a 3d histogram.
        Requires two data items.
        The first data item is plotted on the x axis, and the second on the y axis
        '''
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        xbins = self.calculate_number_of_bins("x")
        ybins = self.calculate_number_of_bins("y")

        # All bins that have count less than cmin will not be displayed
        cmin = self.plot_args["valrange"].get("vmin", None)
        # All bins that has count more than cmax will not be displayed
        cmax = self.plot_args["valrange"].get("vmax", None)


        # Add y=x line
        min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
        max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
        y_equals_x_array = [min_val, max_val]
        self.matplotlib.plot(y_equals_x_array, y_equals_x_array, color = "black", linestyle = "dashed")

        self.matplotlib.hist2d(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], bins = [xbins, ybins], cmin = cmin, cmax = cmax, *self.mplargs, **self.mplkwargs)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def calculate_number_of_bins(self, axis):
        '''
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        @param axis: The axis to calculate the number of bins for
        @return: The number of bins for the given axis
        '''
        if axis == "x":
            axis_index = 0
        elif axis == "y":
            axis_index = 1

        if self.plot_args[axis + "range"] is not None:
            step = self.plot_args[axis + "range"].get(axis + "step", None)
        else:
            step = None

        if step is None:
            number_of_bins = 10
        else:
            number_of_bins = int((self.unpacked_data_items[axis_index]["data"].max() - self.unpacked_data_items[axis_index]["data"].min())/step)

        return number_of_bins

    def format_plot(self):
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_default_axis_label_for_comparative_plot(axis)

    def calculate_axis_limits(self, axis):
        '''
        Calculates the limits for a given axis.
        If the axis is "x" then looks at the data of the first data item
        If the axis is "y" then looks at the data of the second data item
        @param axis: The axis to calculate the limits for
        @return: A dictionary containing the min and max values for the given axis
        '''
        valrange = {}
        if axis == "x":
            coord_axis = 0
        elif axis == "y":
            coord_axis = 1
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[coord_axis]["data"])
        return valrange

    def apply_axis_limits(self, valrange, axis):
        if valrange is not None:
            if axis == "x":
                step = valrange.pop("xstep", None)
                self.matplotlib.xlim(**valrange)
                if step is not None: valrange["xstep"] = step
            elif axis == "y":
                step = valrange.pop("ystep", None)
                self.matplotlib.ylim(**valrange)
                if step is not None: valrange["ystep"] = step

    def create_legend(self):
        '''
        Overides the create legend method of the Generic Plot as a 3d histogram doesn't need a legend
        '''
        pass

    def add_color_bar(self):
        '''
        Adds a color bar to the plot and labels it as "Frequency"
        '''
        step = self.plot_args["valrange"].get("vstep", None)
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)
        cbar = self.matplotlib.colorbar(orientation = self.plot_args["cbarorient"], ticks = ticks)

        if self.plot_args["cbarlabel"] is None:
            label = "Frequency"
        else:
            label = self.plot_args["cbarlabel"]

        cbar.set_label(label)



