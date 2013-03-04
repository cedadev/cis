from jasmin_cis.plotting.generic_plot import Generic_Plot

class Histogram_2D(Generic_Plot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]
    def plot(self):
        '''
        Plots a 2D histogram
        '''
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.plot_args["xrange"] is not None:
            step = self.plot_args["xrange"].get("xstep", None)
        else:
            step = None

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            if step is None:
                number_of_bins = 10
            else:
                number_of_bins = int((unpacked_data_item["data"].max() - unpacked_data_item["data"].min())/step)

            datafile = self.plot_args["datagroups"][i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in self.valid_histogram_styles:
                    self.mplkwargs["histtype"] = datafile["itemstyle"]
                else:
                    from jasmin_cis.exceptions import InvalidHistogramStyleError
                    raise InvalidHistogramStyleError("'" + datafile["itemstyle"] + "' is not a valid histogram style, please use one of: " + str(self.valid_histogram_styles))

            else:
                self.mplkwargs["histtype"] = "bar"

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs["color"] = None

            self.matplotlib.hist(unpacked_data_item["data"].compressed(), bins = number_of_bins, *self.mplargs, **self.mplkwargs)
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        '''
        Sets the default axis label for the given axis.
        If the axis is "y", then labels it "Frequency", else works it out based on the name and units of the data
        @param axis: The axis to calculate the default axis label for
        '''
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if axis == "x":
                units = self.packed_data_items[0].units


                if len(self.packed_data_items) == 1:
                    name = self.packed_data_items[0].name()
                    # only 1 data to plot, display
                    self.plot_args[axislabel] = name + self.format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = self.format_units(units)
            elif axis == "y":
                self.plot_args[axislabel] = "Frequency"

    def calculate_axis_limits(self, axis):
        '''
        Calculates the limits for a given axis.
        If the axis is "y" then looks at the "data" as this is where the values are stored
        @param axis: The axis to calculate the limits for
        @return: A dictionary containing the min and max values for the given axis
        '''
        valrange = {}
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            coord_axis = "data"
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][coord_axis])
        return valrange

    def apply_axis_limits(self, valrange, axis):
        '''
        Applies the limits (if given) to the specified axis.
        Sets the "y" axis as having a minimum value of 0 as can never have a negative frequency
        @param valrange: A dictionary containing the min and/or max values for the axis
        @param axis: The axis to apply the limits to
        '''
        if valrange is not None:
            if axis == "x":
                step = valrange.pop("xstep", None)
                self.matplotlib.xlim(**valrange)
                if step is not None: valrange["xstep"] = step
            elif axis == "y":
                step = valrange.pop("ystep", None)
                self.matplotlib.ylim(**valrange)
                if step is not None: valrange["ystep"] = step
        elif axis == "y":
            # Need to ensure that frequency starts from 0
            self.matplotlib.ylim(ymin = 0)


