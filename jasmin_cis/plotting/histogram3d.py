from jasmin_cis.plotting.generic_plot import Generic_Plot
import numpy

class Histogram_3D(Generic_Plot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]

    def plot(self):
        '''
        Plots a 3d histogram.
        Requires two data items.
        The first data item is plotted on the x axis, and the second on the y axis
        '''
        from numpy.ma import MaskedArray
        from jasmin_cis.utils import apply_intersection_mask_to_two_arrays
        from jasmin_cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) == 2:
            vmin = self.mplkwargs.pop("vmin")
            vmax = self.mplkwargs.pop("vmax")

            xbins = self.calculate_bin_edges("x")
            ybins = self.calculate_bin_edges("y")

            # All bins that have count less than cmin will not be displayed
            cmin = self.plot_args["valrange"].get("vmin", None)
            # All bins that have count more than cmax will not be displayed
            cmax = self.plot_args["valrange"].get("vmax", None)


            # Add y=x line
            min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
            max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
            y_equals_x_array = [min_val, max_val]
            self.matplotlib.plot(y_equals_x_array, y_equals_x_array, color = "black", linestyle = "dashed")

            # Just in case data has different shapes, reshape here
            self.unpacked_data_items[0]["data"] = numpy.reshape(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"].shape)

            first_data_item, second_data_item = apply_intersection_mask_to_two_arrays(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"])

            first_data_item = first_data_item.compressed()
            second_data_item = second_data_item.compressed()

            # Use Numpy histogram generator instead of hist2d to allow log scales to be properly plotted
            histogram2ddata = numpy.histogram2d(first_data_item, second_data_item, bins=[xbins, ybins])[0]
            histogram2ddata = numpy.ma.masked_equal(histogram2ddata, 0)
            self.matplotlib.pcolor(xbins, ybins, histogram2ddata.T, vmin=cmin, vmax=cmax,
                                   *self.mplargs, **self.mplkwargs)

            self.mplkwargs["vmin"] = vmin
            self.mplkwargs["vmax"] = vmax
        else:
            raise InvalidNumberOfDatagroupsSpecifiedError("Histogram 3D requires two datagroups")

    def unpack_data_items(self):
        return self.unpack_comparative_data()

    def set_plotting_library(self):
        pass

    def calculate_bin_edges(self, axis):
        '''
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        :param axis: The axis to calculate the number of bins for
        :return: The number of bins for the given axis
        '''
        from jasmin_cis.utils import calculate_histogram_bin_edges
        if axis == "x":
            data = self.unpacked_data_items[0]["data"]
        elif axis == "y":
            data = self.unpacked_data_items[1]["data"]

        bin_edges = calculate_histogram_bin_edges(data, axis, self.plot_args[axis + "range"], self.plot_args[axis + "binwidth"], self.plot_args["log" + axis])

        self.plot_args[axis + "range"][axis + "min"] = bin_edges.min()
        self.plot_args[axis + "range"][axis + "max"] = bin_edges.max()

        return bin_edges

    def format_plot(self):
        # We don't format the time axis here as we're only plotting data against data
        self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3,3), axis='both')
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_default_axis_label_for_comparative_plot(axis)

    def calculate_axis_limits(self, axis, min_val, max_val, step):
        '''
        Calculates the limits for a given axis.
        If the axis is "x" then looks at the data of the first data item
        If the axis is "y" then looks at the data of the second data item
        :param axis: The axis to calculate the limits for
        :return: A dictionary containing the min and max values for the given axis
        '''
        if axis == "x":
            coord_axis = 0
        elif axis == "y":
            coord_axis = 1
        calculated_min, calculated_max = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[coord_axis]["data"])

        valrange = {}
        valrange[axis + "min"] = calculated_min if min_val is None else min_val
        valrange[axis + "max"] = calculated_max if max_val is None else max_val
        valrange[axis + "step"] = step

        return valrange

    def apply_axis_limits(self, valrange, axis):
        if len(valrange) != 0:
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

    def set_axis_ticks(self, axis, no_of_dims):
        from numpy import arange

        if axis == "x":
            tick_method = self.matplotlib.xticks
            item_index = 0
        elif axis == "y":
            tick_method = self.matplotlib.yticks
            item_index = 1

        if self.plot_args.get(axis + "tickangle", None) is None:
            angle = None
        else:
            angle = self.plot_args[axis + "tickangle"]

        if self.plot_args[axis + "range"].get(axis + "step") is not None:
            step = self.plot_args[axis + "range"][axis + "step"]

            if self.plot_args[axis + "range"].get(axis + "min") is None:
                min_val = self.unpacked_data_items[item_index]["data"].min()
            else:
                min_val = self.plot_args[axis + "range"][axis + "min"]

            if self.plot_args[axis + "range"].get(axis + "max") is None:
                max_val = self.unpacked_data_items[item_index]["data"].max()
            else:
                max_val = self.plot_args[axis + "range"][axis + "max"]

            ticks = arange(min_val, max_val+step, step)

            tick_method(ticks, rotation=angle)
        else:
            tick_method(rotation=angle)

    def drawcoastlines(self):
        pass
