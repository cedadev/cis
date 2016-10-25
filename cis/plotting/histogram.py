"""
A basic histogram plot
"""
from cis.plotting.genericplot import GenericPlot


class Histogram(GenericPlot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]

    def __init__(self, packed_data, xbins=10, *args, **kwargs):
        """
        :param xbins: The number of bins to use on the xaxis
        """
        super(Histogram, self).__init__(packed_data, *args, **kwargs)
        self.xbins = xbins
        #
        self.xlabel = packed_data.name()
        self.ylabel = "Frequency"

    def __call__(self, ax):
        from numpy.ma import MaskedArray

        self.mplkwargs["bins"] = self.xbins

        if self.itemstyle:
            if self.itemstyle in self.valid_histogram_styles:
                self.mplkwargs["histtype"] = self.itemstyle
            else:
                from cis.exceptions import InvalidHistogramStyleError
                raise InvalidHistogramStyleError(
                    "'" + self.itemstyle + "' is not a valid histogram style, please use one of: " + str(
                        self.valid_histogram_styles))

        if self.color:
            self.mplkwargs["color"] = self.color

        if isinstance(self.data, MaskedArray):
            data = self.data.compressed()
        else:
            data = self.data.flatten()

        ax.hist(data, *self.mplargs, **self.mplkwargs)

        super(Histogram, self).__call__(ax)

    def unpack_data_items(self, packed_data_items):
        self.data = packed_data_items.data
