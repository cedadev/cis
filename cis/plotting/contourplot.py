"""
A contour plot, filled or not.
"""
from .genericplot import Generic2DPlot


class ContourPlot(Generic2DPlot):

    def __init__(self, packed_data, contnlevels=7, vstep=None,
                 contlevels=None, contlabel=False, contwidth=None, cont_label_kwargs=None, *args, **kwargs):
        """

        :param packed_data:
        :param int contnlevels: The number of contour levels to plot (default is 7)
        :param float vstep: The step between contour levels
        :param list contlevels: A list of contour levels to plot
        :param bool contlabel: Plot contour labels (default is False)
        :param int contwidth: The thickness of the contour lines
        :param dict cont_label_kwargs: A dictionary of contour label keywork args (e.g. format)
        :param kwargs: Other keyword args to pass to plot
        """
        super(ContourPlot, self).__init__(packed_data, *args, **kwargs)
        self.filled = False
        if contlevels:
            self.levels = contlevels
        elif self.vstep:
            self.levels = (kwargs.get('vmax', self.data.max()) -
                           kwargs.get('vmin', self.data.min())) / vstep
        else:
            self.levels = contnlevels

        self.contlabel = contlabel
        self.contwidth = contwidth
        self.cont_label_kwargs = cont_label_kwargs if cont_label_kwargs is not None else {}

    def __call__(self, ax):
        from matplotlib import ticker

        # Set the options specific to a datagroup with the contour type
        mplkwargs = self.mplkwargs

        mplkwargs["colors"] = self.color

        mplkwargs["linewidths"] = self.contwidth

        if self.logv:
            mplkwargs['locator'] = ticker.LogLocator()

        contour_type = ax.contourf if self.filled else ax.contour

        self.mappable = contour_type(self.x, self.y, self.data, self.levels, **mplkwargs)

        if self.contlabel:
            ax.clabel(self.mappable, **self.cont_label_kwargs)

        super(ContourPlot, self).__call__(ax)


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data, *args, **kwargs):
        super(ContourfPlot, self).__init__(packed_data, *args, **kwargs)
        self.filled = True
