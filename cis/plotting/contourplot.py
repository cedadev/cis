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

        # Set the options specific to a datagroup with the contour type
        mplkwargs = self.mplkwargs

        mplkwargs["colors"] = self.color

        mplkwargs["linewidths"] = self.contwidth
        if self.cmin is not None:
            vmin = self.cmin
        if self.cmax is not None:
            vmax = self.cmax

        if self.vstep is None and \
                        self.contnlevels is None:
            nconts = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        elif self.vstep is None:
            nconts = self.contnlevels
        else:
            nconts = (vmax - vmin) / self.vstep

        if self.contlevels is None:
            if self.logv is None:
                contour_level_list = np.linspace(vmin, vmax, nconts)
            else:
                contour_level_list = np.logspace(np.log10(vmin), np.log10(vmax), nconts)
        else:
            contour_level_list = self.contlevels

        contour_type = self.ax.contourf if self.filled else self.ax.contour

        contours = contour_type(self.x, self.y, self.data, contour_level_list, **mplkwargs)

        if self.contlabel:
            self.ax.clabel(contours, **self.cont_label_kwargs)

        super(ContourPlot, self).__call__()


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        super(ContourfPlot, self).__init__(packed_data_items, *args, **kwargs)
        self.filled = True
