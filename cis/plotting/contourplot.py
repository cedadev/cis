from .genericplot import Generic2DPlot

DEFAULT_NUMBER_OF_CONTOUR_LEVELS = 7


class ContourPlot(Generic2DPlot):

    def __init__(self, packed_data_items, contnlevels=None,
                 contlevels=None, contlabel=None, contwidth=None, cont_label_kwargs=None, vstep=None, *args, **kwargs):
        super(ContourPlot, self).__init__(packed_data_items, *args, **kwargs)
        self.vstep = vstep
        self.filled = False
        self.contnlevels = contnlevels
        self.contlevels = contlevels
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

        if self.contlevels:
            levels = self.contlevels
        elif self.contnlevels:
            levels = self.contnlevels
        elif self.vstep:
            levels = (mplkwargs.get('vmax', self.data.max()) -
                                   mplkwargs.get('vmin', self.data.min())) / self.vstep
        else:
            levels = DEFAULT_NUMBER_OF_CONTOUR_LEVELS

        contour_type = ax.contourf if self.filled else ax.contour

        self.mappable = contour_type(self.x, self.y, self.data, levels, **mplkwargs)

        if self.contlabel:
            ax.clabel(self.mappable, **self.cont_label_kwargs)

        super(ContourPlot, self).__call__(ax)


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        super(ContourfPlot, self).__init__(packed_data_items, *args, **kwargs)
        self.filled = True
