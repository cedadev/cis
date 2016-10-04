from .genericplot import Generic2DPlot


class ContourPlot(Generic2DPlot):

    def __init__(self, packed_data_items, contnlevels=None,
                 contlevels=None, contlabel=None, contwidth=None, contfontsize=None, *args, **kwargs):
        super(ContourPlot).__init__(packed_data_items, *args, **kwargs)
        self.filled = False
        self.contnlevels = contnlevels
        self.contlevels = contlevels
        self.contlabel = contlabel
        self.contwidth = contwidth
        self.contfontsize = contfontsize

    def plot(self):
        import numpy as np

        # Set the options specific to a datagroup with the contour type
        mplkwargs = self.mplkwargs
        mplkwargs['cmap'] = self.cmap
        mplkwargs["contlabel"] = self.contlabel
        mplkwargs["cfontsize"] = self.contfontsize
        mplkwargs["colors"] = self.color

        mplkwargs["linewidths"] = self.contwidth
        if self.cmin is not None:
            vmin = self.cmin
        if self.cmax is not None:
            vmax = self.cmax

        vmin = mplkwargs.pop("vmin")
        vmax = mplkwargs.pop("vmax")

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

        if self.filled:
            contour_type = self.ax.contourf
        else:
            contour_type = self.ax.contour

        if self.is_map() and self.data.ndim == 2:
            # This fails for an unknown reason on one dimensional data
            mplkwargs["latlon"] = True

        self.color_axis.append(contour_type(self.x, self.y,
                                            self.data, contour_level_list, **mplkwargs))
        if mplkwargs["contlabel"] and not self.filled:
            self.ax.clabel(self.color_axis[0], fontsize=mplkwargs["cfontsize"], inline=1, fmt='%.3g')
        elif mplkwargs["contlabel"] and self.filled:
            self.ax.clabel(self.color_axis[0], fontsize=mplkwargs["cfontsize"], inline=0, fmt='%.3g')


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        super().__init__(packed_data_items, *args, **kwargs)
        self.filled = False
