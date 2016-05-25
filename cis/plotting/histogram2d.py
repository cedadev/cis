from cis.plotting.genericplot import Generic2DPlot
import numpy


class Histogram2D(Generic2DPlot):

    def __init__(self, packed_data_items, xbinwidth=None, ybinwidth=None, *args, **kwargs):
        super(Histogram2D, self).__init__(packed_data_items, *args, **kwargs)
        self.xbinwidth = xbinwidth
        self.ybinwidth = ybinwidth

    def plot(self):
        """
        Plots a 3d histogram.
        Requires two data items.
        The first data item is plotted on the x axis, and the second on the y axis
        """
        from cis.utils import apply_intersection_mask_to_two_arrays
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        xbins = self.calculate_bin_edges("x")
        ybins = self.calculate_bin_edges("y")

        # All bins that have count less than cmin will not be displayed
        cmin = vmin
        # All bins that have count more than cmax will not be displayed
        cmax = vmax

        # Add y=x line
        min_val = min(self.x.min(), self.y.min())
        max_val = max(self.x.max(), self.y.max())
        y_equals_x_array = [min_val, max_val]
        self.ax.plot(y_equals_x_array, y_equals_x_array, color="black", linestyle="dashed")

        # Just in case data has different shapes, reshape here
        self.x = numpy.reshape(self.x, self.y.shape)

        first_data_item, second_data_item = apply_intersection_mask_to_two_arrays(
            self.x, self.y)

        first_data_item = first_data_item.compressed()
        second_data_item = second_data_item.compressed()

        # Use Numpy histogram generator instead of hist2d to allow log scales to be properly plotted
        histogram2ddata = numpy.histogram2d(first_data_item, second_data_item, bins=[xbins, ybins])[0]
        histogram2ddata = numpy.ma.masked_equal(histogram2ddata, 0)
        self.ax.pcolor(xbins, ybins, histogram2ddata.T, vmin=cmin, vmax=cmax, *self.mplargs, **self.mplkwargs)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def unpack_data_items(self, packed_data_items, x_wrap_start=None):
        self.x = packed_data_items[0].data
        self.y = packed_data_items[1].data

    def calculate_bin_edges(self, axis):
        """
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        :param axis: The axis to calculate the number of bins for
        :return: The number of bins for the given axis
        """
        from cis.utils import calculate_histogram_bin_edges
        if axis == "x":
            data = self.x
        elif axis == "y":
            data = self.y

        bin_edges = calculate_histogram_bin_edges(data, axis, getattr(self, axis + "min"), getattr(self, axis + "max"),
                                                  getattr(self, axis + "binwidth"), getattr(self, "log" + axis))

        setattr(self, axis + "min", bin_edges.min())
        setattr(self, axis + "max", bin_edges.max())

        return bin_edges

    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        """
        Sets the default axis label for a comparative plot, e.g. a comparative scatter or a 3d histogram
        :param axis: The axis to set the default label for
        """
        from .APlot import format_units
        if axis.lower() == 'x':
            item_index = 0
        elif axis.lower() == 'y':
            item_index = 1

        units = data[item_index].units
        name = data[item_index].name()
        return name + " " + format_units(units)

    @staticmethod
    def add_color_bar(fig, mappable, cbarorient, cbarscale, cbarlabel, logv, vstep):
        """
        Adds a color bar to the plot and labels it as "Frequency"
        """
        super(Histogram2D).add_color_bar(fig, mappable, cbarorient, cbarscale, "Frequency", logv, vstep)

    def set_axis_ticks(self, axis, no_of_dims):
        from numpy import arange

        if axis == "x":
            tick_method = self.ax.xticks
        elif axis == "y":
            tick_method = self.ax.yticks

        if getattr(self, axis + "step") is not None:
            step = getattr(self, axis + "step")

            if getattr(self, axis + "min") is None:
                min_val = getattr(self, axis).min()
            else:
                min_val = getattr(self, axis + "min")

            if getattr(self, axis + "max") is None:
                max_val = getattr(self, axis).max()
            else:
                max_val = getattr(self, axis + "max")

            ticks = arange(min_val, max_val + step, step)

            tick_method(ticks)

    def drawcoastlines(self):
        pass

    @staticmethod
    def valid_number_of_datagroups(number_of_datagroups):
        return number_of_datagroups == 2
