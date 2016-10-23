from cis.plotting.comparativescatter import ComparativeScatter
import numpy


class Histogram2D(ComparativeScatter):

    def __init__(self, packed_data_items, logv=None, vstep=None, xbins=10, ybins=10,
                 cbarscale=None, cbarorient=None, colourbar=True, cbarlabel=None, *args, **kwargs):
        super(Histogram2D, self).__init__(packed_data_items, *args, **kwargs)

        self.logv = logv
        self.xbins = xbins
        self.ybins = ybins
        self.vstep = vstep
        self.cbarscale = cbarscale
        self.cbarorient = cbarorient
        self.colourbar = colourbar
        self.cbarlabel = cbarlabel or "Frequency"

    def __call__(self, ax):
        """
        Plots a 2d histogram.
        """
        from .plot import add_color_bar
        from cis.utils import apply_intersection_mask_to_two_arrays

        first_data_item, second_data_item = apply_intersection_mask_to_two_arrays(self.x, self.y)

        first_data_item = first_data_item.compressed()
        second_data_item = second_data_item.compressed()

        # Use Numpy histogram generator instead of hist2d to allow log scales to be properly plotted
        histogram2ddata, x, y = numpy.histogram2d(first_data_item, second_data_item, bins=[self.xbins, self.ybins])
        histogram2ddata = numpy.ma.masked_equal(histogram2ddata, 0)
        self.map = ax.pcolor(x, y, histogram2ddata.T, *self.mplargs, **self.mplkwargs)

        self._plot_xy_line(ax)

        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        if self.colourbar:
            add_color_bar(self.map, self.vstep, self.logv, self.cbarscale, self.cbarorient, self.cbarlabel)
