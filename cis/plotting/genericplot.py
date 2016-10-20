import logging

import numpy as np
from .APlot import APlot
from cis.exceptions import CISError


# TODO: Carry on splitting out the 2d and 3d plot methods. Make the relavant plots subclass the right one. Pull out any
# obviously static methods. and split files. This should make the classes more manageable and easier to test.


def format_plot(ax, logx, logy, grid, xstep, ystep, fontsize, xlabel, ylabel, title):
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

    if xstep is not None:
        min_val, max_val = ax.get_xlim()
        ticks = np.arange(min_val, max_val + xstep, xstep)

        ax.set_xticks(ticks)

    if ystep is not None:
        min_val, max_val = ax.get_ylim()
        ticks = np.arange(min_val, max_val + ystep, ystep)

        ax.set_yticks(ticks)

    if fontsize is not None:
        matplotlib.rcParams.update({'font.size': fontsize})

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    ax.relim()
    ax.autoscale()


class GenericPlot(APlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        from cis.plotting.APlot import get_label
        super(GenericPlot, self).__init__(packed_data_items, *args, **kwargs)

        logging.debug("Unpacking the data items")
        self.x, self.data = self.xaxis.points, packed_data_items.data

        self.mplkwargs['label'] = self.label or packed_data_items.name()
        self.xlabel, self.ylabel = get_label(self.xaxis), get_label(packed_data_items)

    def __call__(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

    def is_map(self):
        return False


class Generic2DPlot(APlot):

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, transparency=None, logv=None, vstep=None,
                 cbarscale=None, cbarorient=None, colourbar=True, cbarlabel=None,
                 coastlines=True, coastlinescolour='k', *args, **kwargs):
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
        from .APlot import format_units
        super(Generic2DPlot, self).__init__(packed_data_items, *args, **kwargs)

        self.logv = logv
        self.vstep = vstep
        self.cbarscale = cbarscale
        if cbarorient is None:
            self.cbarorient = 'horizontal' if self.is_map() else 'vertical'
        else:
            self.cbarorient = cbarorient
        self.colourbar = colourbar
        self.cbarlabel = cbarlabel or format_units(packed_data_items.units)

        self.coastlines = coastlines
        self.coastlinescolour = coastlinescolour

        self.transparency = transparency

        if self.logv:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        logging.debug("Unpacking the data items")
        # TODO I shouldn't need to do this
        self.data, self.x, self.y = self.unpack_data_items(packed_data_items)

        self.xlabel = self.guess_axis_label(packed_data_items, self.xaxis)
        self.ylabel = self.guess_axis_label(packed_data_items, self.yaxis)
        self.label = packed_data_items.name()

    def __call__(self, ax):
        from .plot import add_color_bar
        from .plot import drawcoastlines, auto_set_map_ticks
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.label)
        if self.colourbar:
            add_color_bar(self.mappable, self.vstep, self.logv, self.cbarscale, self.cbarorient, self.cbarlabel)

        if self.is_map():
            if self.coastlines:
                drawcoastlines(ax, self.coastlinescolour)
            auto_set_map_ticks(ax, self.mplkwargs.get('transform', None))

    def is_map(self):
        if self.xaxis.name().lower().startswith("lon") and self.yaxis.name().lower().startswith("lat"):
            return True

    def unpack_data_items(self, data_object):
        """
        :param data_object    A cube or an UngriddedData object
        :return: A dictionary containing x, y and data as numpy arrays
        """
        from iris.cube import Cube
        import iris.plot as iplt
        import iris
        import logging
        from cartopy.util import add_cyclic_point
        import numpy as np

        no_of_dims = len(data_object.shape)

        data = data_object.data  # ndarray

        x = self.xaxis.points
        y = self.yaxis.points

        if isinstance(data_object, Cube):
            plot_defn = iplt._get_plot_defn(data_object, iris.coords.POINT_MODE, ndims=no_of_dims)
            if plot_defn.transpose:
                data = data.T
                x = x.T
                y = y.T

            # Check for auxiliary coordinates.
            aux_coords = False
            for coord in data_object[0].coords(dim_coords=False):
                aux_coords = True

            if no_of_dims == 2:
                # If we have found some auxiliary coordinates in the data and the shape of x data or y data is the same as
                # data assume we have a hybrid coordinate (which is two dimensional b nature. Perhaps need a more robust
                # method for detecting this.
                if aux_coords and (data.shape == x.shape or data.shape == y.shape):
                    # Work out which set of data needs expanding to match the coordinates of the others. Note there can only
                    # ever be one hybrid coordinate axis.
                    if y.shape == data.shape:
                        if y[:, 0].shape == x.shape:
                            x, _y = np.meshgrid(x, y[0, :])
                        elif y[0, :].shape == x.shape:
                            x, _y = np.meshgrid(x, y[:, 0])
                    elif x.shape == data.shape:
                        if x[:, 0].shape == y.shape:
                            y, _x = np.meshgrid(y, x[0, :])
                        elif x[0, :].shape == y.shape:
                            y, _x = np.meshgrid(y, x[:, 0])
                else:
                    if len(x) == data.shape[-1]:
                        try:
                            data, x = add_cyclic_point(data, x)
                        except ValueError as e:
                            logging.warn('Unable to add cyclic data point for x-axis. Error was: ' + e.args[0])
                        x, y = np.meshgrid(x, y)
                    elif len(y) == data.shape[-1]:
                        try:
                            data, y = add_cyclic_point(data, y)
                        except ValueError as e:
                            logging.warn('Unable to add cyclic data point for y-axis. Error was: ' + e.args[0])
                        y, x = np.meshgrid(y, x)

        logging.debug("Shape of x: " + str(x.shape))
        if y is not None:
            logging.debug("Shape of y: " + str(y.shape))
        logging.debug("Shape of data: " + str(data.shape))

        return data, x, y