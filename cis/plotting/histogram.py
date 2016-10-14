from cis.plotting.genericplot import GenericPlot


class Histogram(GenericPlot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]

    def __init__(self, packed_data_items, *args, xbinwidth=None, **kwargs):
        super(Histogram, self).__init__(packed_data_items, *args, **kwargs)
        self.xbinwidth = xbinwidth
        #
        self.xlabel = packed_data_items.name()
        self.ylabel = "Frequency"


    def __call__(self):
        """
        Plots a 2D histogram
        """
        from numpy.ma import MaskedArray
        # TODO: What is going on here..?
        # vmin = self.mplkwargs.pop("vmin")
        # vmax = self.mplkwargs.pop("vmax")

        # TODO: Delete this routine - it's trying to be too clever by half
        # self.mplkwargs["bins"] = self.calculate_bin_edges()

        if self.itemstyle:
            if self.itemstyle in self.valid_histogram_styles:
                self.mplkwargs["histtype"] = self.itemstyle
            else:
                from cis.exceptions import InvalidHistogramStyleError
                raise InvalidHistogramStyleError(
                    "'" + self.itemstyle + "' is not a valid histogram style, please use one of: " + str(
                        self.valid_histogram_styles))
        # TODO: Why are we popping this off - maybe someone put it on there deliberately?
        else:
            self.mplkwargs.pop("histtype", None)

        if self.color:
            self.mplkwargs["color"] = self.color
        # TODO: As above
        else:
            self.mplkwargs.pop("color", None)

        if isinstance(self.data, MaskedArray):
            data = self.data.compressed()
        else:
            data = self.data.flatten()

        self.ax.hist(data, *self.mplargs, **self.mplkwargs)

        # self.mplkwargs["vmin"] = vmin
        # self.mplkwargs["vmax"] = vmax

        super(Histogram, self).__call__()

    def unpack_data_items(self, packed_data_items, x_wrap_start=None):
        self.data = packed_data_items.data

    def calculate_bin_edges(self):
        """
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        :param axis: The axis to calculate the number of bins for
        :return: The number of bins for the given axis
        """
        from cis.utils import calculate_histogram_bin_edges
        from numpy import array
        data = array([self.data.min(), self.data.max()])
        bin_edges = calculate_histogram_bin_edges(data, "x", self.xmin, self.xmax, self.xbinwidth, self.logx)

        # TODO: Why are these being changed?
        self.xmin = bin_edges.min()
        self.xmax = bin_edges.max()

        return bin_edges

    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        """
        Sets the default axis label for the given axis.
        If the axis is "y", then labels it "Frequency", else works it out based on the name and units of the data
        :param axis: The axis to calculate the default axis label for
        """
        from .APlot import format_units

        if axis.lower() == "x":
            units = data[0].units

            if len(data) == 1:
                name = data[0].name()
                # only 1 data to plot, display
                label = name + " " + format_units(units)
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                label = format_units(units)
        elif axis.lower() == "y":
            label = "Frequency"

        return label

    def apply_axis_limits(self):
        """
        Applies the limits (if given) to the specified axis.
        Sets the "y" axis as having a minimum value of 0 as can never have a negative frequency
        :param valrange: A dictionary containing the min and/or max values for the axis
        :param axis: The axis to apply the limits to
        """
        # Need to ensure that frequency starts from 0
        self.ymin = 0 if self.ymin < 0 else self.ymin

        super(Histogram, self).apply_axis_limits()