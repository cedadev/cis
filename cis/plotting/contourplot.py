from .genericplot import Generic2DPlot


class ContourPlot(Generic2DPlot):

    def __init__(self, packed_data_items, ax, contnlevels=None,
                 contlevels=None, contlabel=None, contwidth=None, cont_label_kwargs=None, vstep=None, *args, **kwargs):
        super(ContourPlot, self).__init__(packed_data_items, ax, *args, **kwargs)
        self.vstep = vstep
        self.filled = False
        self.contnlevels = contnlevels
        self.contlevels = contlevels
        self.contlabel = contlabel
        self.contwidth = contwidth
        self.cont_label_kwargs = cont_label_kwargs if cont_label_kwargs is not None else {}

    def __call__(self):
        import numpy as np
        from matplotlib import colors, ticker

        # Set the options specific to a datagroup with the contour type
        mplkwargs = self.mplkwargs

        mplkwargs["colors"] = self.color

        mplkwargs["linewidths"] = self.contwidth

        if self.logv:
            mplkwargs['locator'] = ticker.LogLocator()

        if self.contlevels:
            mplkwargs['levels'] = self.contlevels
        elif self.contnlevels:
            mplkwargs['levels'] = self.contnlevels
        elif self.vstep:
            mplkwargs['levels'] = (mplkwargs.get('vmin', self.data.min) -
                                   mplkwargs.get('vmax', self.data.max)) / self.vstep

        contour_type = self.ax.contourf if self.filled else self.ax.contour

        self.map = contour_type(self.x, self.y, self.data, **mplkwargs)

        if self.contlabel:
            self.ax.clabel(self.map, **self.cont_label_kwargs)

        super(ContourPlot, self).__call__()


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        super(ContourfPlot, self).__init__(packed_data_items, *args, **kwargs)
        self.filled = True
