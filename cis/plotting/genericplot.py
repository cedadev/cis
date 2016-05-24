import logging

import numpy as np
from .APlot import APlot
from cis.exceptions import CISError
from .formatter import LogFormatterMathtextSpecial

# TODO: Carry on splitting out the 2d and 3d plot methods. Make the relavant plots subclass the right one. Pull out any
# obviously static methods. and split files. This should make the classes more manageable and easier to test.


def set_yaxis_ticks(ax, step=None, tickangle=None, transform=None):
    from cartopy.mpl.ticker import LatitudeFormatter
    from cartopy.mpl.geoaxes import GeoAxes
    from numpy import arange

    tick_kwargs = {}

    if isinstance(ax, GeoAxes):
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        tick_kwargs['crs'] = transform

    if tickangle is None:
        tick_kwargs['ha'] = "right"
    else:
        tick_kwargs['rotation'] = tickangle
        tick_kwargs['ha'] = "right"

    if step is not None:
        min_val, max_val = ax.get_ylim()
        ticks = arange(min_val, max_val + step, step)

        ax.set_yticks(ticks, **tick_kwargs)
    elif tick_kwargs:
        ax.set_yticks(**tick_kwargs)


def set_xaxis_ticks(ax, step=None, tickangle=None, transform=None):
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from cartopy.mpl.geoaxes import GeoAxes
    from numpy import arange

    tick_kwargs = {}

    if isinstance(ax, GeoAxes):
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        tick_kwargs['crs'] = transform

    if tickangle is None:
        tick_kwargs['ha'] = "center"
    else:
        tick_kwargs['rotation'] = tickangle
        tick_kwargs['ha'] = "right"

    if step is not None:
        min_val, max_val = ax.get_xlim()
        ticks = arange(min_val, max_val + step, step)

        ax.set_xticks(ticks, **tick_kwargs)
    elif tick_kwargs:
        ax.set_xticks(**tick_kwargs)


def format_plot(ax, logx, logy, grid, xstep, ystep, xtickangle, ytickangle, fontsize, xlabel, ylabel, title,
                transform=None, legend=False):
    """
    Used by 2d subclasses to format the plot
    """
    import matplotlib

    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")

    if grid:
        ax.grid(True, which="both")

    set_xaxis_ticks(ax, xstep, xtickangle, transform)
    set_yaxis_ticks(ax, ystep, ytickangle, transform)

    if fontsize is not None:
        matplotlib.rcParams.update({'font.size': fontsize})

    # If any of the options have not been specified, then use the defaults
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.set_title(title)

    if legend:
        legend = ax.legend(loc="best")
        legend.draggable(state=True)


class GenericPlot(APlot):

    def __init__(self, packed_data_items, *mplargs, **mplkwargs):
        super().__init__(packed_data_items, *mplargs, **mplkwargs)

        logging.debug("Unpacking the data items")
        # TODO: Drop one of self.unpacked_data_items or self.packed_data_items
        # If I drop the unpacked then I'll need to store the x and y coords somewhere and worry about the cube transforms,
        #  if I drop the packed items then I'll need to store the metadata somewhere (units, axis labels etc).
        self.unpacked_data_items = self.unpack_data_items()

        self.mplkwargs['label'] = self.label or packed_data_items.longname

        self.plot()


class Generic2DPlot(APlot):

    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, ax=None, logv=False, vmin=None, vmax=None, vstep=None,
                 transparency=None, cmap=None, cmin=None, cmax=None, x_wrap_start=None, *args, **kwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param calculate_min_and_max_values: If true calculates min and max for the data values
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """
        super().__init__(packed_data_items, ax, *args, **kwargs)

        self.logv = logv
        self.vmin = vmin
        self.vmax = vmax
        self.vstep = vstep

        self.cmin = cmin
        self.cmax = cmax
        self.cmap = cmap
        self.transparency = transparency

        if self.logv:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        logging.debug("Unpacking the data items")
        self.x_wrap_start = x_wrap_start
        self.unpacked_data_items = self.unpack_data_items()

        self.mplkwargs["vmin"], self.mplkwargs["vmax"] = self.calculate_min_and_max_values()

        self.plot()

    def calculate_min_and_max_values(self):
        """
        Calculates the min and max values of all the data given
        Stores the values in the matplotlib keyword args to be directly passed into the plot methods.
        """
        from .APlot import calc_min_and_max_vals_of_array_incl_log

        data_min, data_max = calc_min_and_max_vals_of_array_incl_log(self.data)

        vmin = self.vmin if self.vmin is not None else data_min
        vmax = self.vmax if self.vmax is not None else data_max

        return vmin, vmax

    @staticmethod
    def add_color_bar(fig, mappable, cbarorient, cbarscale, cbarlabel, logv, vstep):
        """
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        """
        from .APlot import format_units
        from matplotlib.colorbar import ColorbarBase

        step = vstep
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)

        if logv:
            formatter = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
        else:
            formatter = None
        #
        scale = cbarscale
        orientation = cbarorient
        if scale is None:
            default_scales = {"horizontal": 1.0, "vertical": 0.55}
            scale = default_scales.get(orientation, 1.0)
        else:
            scale = float(scale)

        cbar = fig.colorbar(mappable, orientation=orientation, ticks=ticks,
                                        shrink=scale, format=formatter)

        if not logv:
            cbar.formatter.set_scientific(True)
            cbar.formatter.set_powerlimits((-3, 3))
            cbar.update_ticks()

        cbar.set_label(cbarlabel)

