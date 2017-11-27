"""
A '2D' Histogram plot - e.g. one that has data on both the x and y axis. This is generated using numpy.histogram2d and
a call to pcolormesh. Although strictly a 2D plot it inherits from ComparativeScatter rather than Generic2D because
the unpacking has more in common with that.
"""
from cis.plotting.comparativescatter import ComparativeScatter
import numpy


class Histogram2D(ComparativeScatter):

    def __init__(self, packed_data, logv=None, vstep=None, xbins=10, ybins=10,
                 cbarscale=None, cbarorient=None, colourbar=True, cbarlabel=None, *args, **kwargs):
        """
        Note that the packed_data argument is ignored for this plot type - only xaxis and yaxis are plotted.

        :param CommonData packed_data: IGNORED
        :param bool logv: Log the v (colour bar) axis?
        :param float vstep: The step to use for the v axis (colour bar)
        :param int xbins: The number of histogram bins to use on the xaxis
        :param int ybins: The number of histogram bins to use on the yaxis
        :param bool colourbar: Include colour bar? Default True
        :param float cbarscale: A scale factor for the colorbar
        :param string cbarorient: The colour bar orientation ('vertical' or 'horizontal')
        :param string cbarlabel: A label for the colour bar
        """
        super(Histogram2D, self).__init__(packed_data, *args, **kwargs)

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

        # Numpy histogram2D doesn't like masked arrays, so create the unmased intersection of the two datasets
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
            add_color_bar(ax, self.map, self.vstep, self.logv, self.cbarscale, self.cbarorient, self.cbarlabel)
