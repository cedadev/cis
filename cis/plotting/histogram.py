from cis.plotting.genericplot import GenericPlot


class Histogram(GenericPlot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]

    def __init__(self, packed_data_items, xbinwidth=None, *args, **kwargs):
        super().__init__(packed_data_items, *args, **kwargs)
        self.xbinwidth = xbinwidth

    def plot(self):
        """
        Plots a 2D histogram
        """
        from numpy.ma import MaskedArray
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        self.mplkwargs["bins"] = self.calculate_bin_edges()

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.datagroups[i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in self.valid_histogram_styles:
                    self.mplkwargs["histtype"] = datafile["itemstyle"]
                else:
                    from cis.exceptions import InvalidHistogramStyleError
                    raise InvalidHistogramStyleError(
                        "'" + datafile["itemstyle"] + "' is not a valid histogram style, please use one of: " + str(
                            self.valid_histogram_styles))

            else:
                self.mplkwargs.pop("histtype", None)

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs.pop("color", None)

            if isinstance(unpacked_data_item["data"], MaskedArray):
                data = unpacked_data_item["data"].compressed()
            else:
                data = unpacked_data_item["data"].flatten()

            self.matplotlib.hist(data, *self.mplargs, **self.mplkwargs)
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def unpack_data_items(self):
        return self.unpack_comparative_data()

    def calculate_bin_edges(self):
        """
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        :param axis: The axis to calculate the number of bins for
        :return: The number of bins for the given axis
        """
        from cis.utils import calculate_histogram_bin_edges
        from numpy import array
        min_val = min(unpacked_data_item["data"].min() for unpacked_data_item in self.unpacked_data_items)
        max_val = max(unpacked_data_item["data"].max() for unpacked_data_item in self.unpacked_data_items)
        data = array([min_val, max_val])
        bin_edges = calculate_histogram_bin_edges(data, "x", self.xmin, self.xmax,
                                                  self.xbinwidth, self.logx)

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

    def set_axis_ticks(self, axis, no_of_dims):

        if axis == "x":
            tick_method = self.matplotlib.xticks
        elif axis == "y":
            tick_method = self.matplotlib.yticks

        if getattr(self, axis + "tickangle") is None:
            angle = None
        else:
            angle = getattr(self, axis + "tickangle")

        tick_method(rotation=angle)

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