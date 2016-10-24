import logging
from abc import ABCMeta, abstractmethod
import six
from cis.plotting.formatted_plot import set_log_scales
from iris.coords import POINT_MODE


@six.add_metaclass(ABCMeta)
class APlot(object):

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, xaxis, yaxis, color=None,
                 edgecolor=None, itemstyle=None, itemwidth=None, label=None, *mplargs, **mplkwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """
        # Raw data attributes (for unpacking the packed data into)
        self.data = None
        self.x = None
        self.y = None

        self.xaxis = xaxis
        self.yaxis = yaxis
        self.color = color
        self.label = label
        self.edgecolor = edgecolor
        self.itemstyle = itemstyle
        self.itemwidth = itemwidth

        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        self.color_axis = []

    @abstractmethod
    def __call__(self, ax):
        """
        The method that will do the plotting. To be implemented by each subclass of Generic_Plot.
        """
        pass

    @abstractmethod
    def is_map(self):
        """
        :return: A boolean saying if this plot should be represented as a map
        """
        pass

    def is_rectangular_projection(self, ax):
        from cartopy.crs import _RectangularProjection
        return self.is_map() and isinstance(ax.projection, _RectangularProjection)

    def set_log_scales(self, ax, logx, logy):
        """
        Optionally log-scale one or both of the axis. Default for Aplot is to rescale after logging.
        """
        set_log_scales(ax, logx, logy, True)


class GenericPlot(APlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        from cis.plotting.plot import get_label
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

    MODE = POINT_MODE

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, logv=None, vstep=None,
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
        from .plot import get_label
        super(Generic2DPlot, self).__init__(packed_data_items, *args, **kwargs)

        logging.debug("Unpacking the data items")
        # TODO I shouldn't need to do this
        self.data, self.x, self.y = self.unpack_data_items(packed_data_items)

        self.xlabel = get_label(self.xaxis)
        self.ylabel = get_label(self.yaxis)

        self.logv = logv
        self.vstep = vstep
        self.cbarscale = cbarscale
        if cbarorient is None:
            # Set the color bar to be horizontal if we're plotting a wide map, otherwise vertical
            self.cbarorient = 'horizontal' if self.is_map() and \
                                              (self.x.max() - self.x.min()) > \
                                              (self.y.max() - self.y.min()) else 'vertical'
        else:
            self.cbarorient = cbarorient

        self.colourbar = colourbar
        self.cbarlabel = cbarlabel or self.label

        self.coastlines = coastlines
        self.coastlinescolour = coastlinescolour

        if self.logv:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

    def __call__(self, ax):
        from .plot import add_color_bar
        from .plot import drawcoastlines, get_best_map_ticks, set_map_ticks
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        if self.colourbar:
            add_color_bar(self.mappable, self.vstep, self.logv, self.cbarscale, self.cbarorient, self.cbarlabel)
        else:
            ax.set_title(self.label)

        if self.is_map():
            if self.coastlines:
                drawcoastlines(ax, self.coastlinescolour)
            set_map_ticks(ax, *get_best_map_ticks(ax))

    def is_map(self):
        if self.xaxis.name().lower().startswith("lon") and self.yaxis.name().lower().startswith("lat"):
            return True

    def set_log_scales(self, ax, logx, logy):
        if self.is_map():
            logging.debug("Ignoring log formatting for map plot")
        else:
            # Don't rescale as it doesn't work for collections (heatmaps, scatter2d etc)
            set_log_scales(ax, logx, logy, False)

    def unpack_data_items(self, data_object):
        """
        :param data_object: A cube or an UngriddedData object
        :param x: a numpy array of x points
        :param y: a numpy array of y points
        :return: A dictionary containing x, y and data as numpy arrays
        """
        from iris.cube import Cube
        import logging

        x = self.xaxis.points if self.MODE == POINT_MODE else self.xaxis.contiguous_bounds()
        y = self.yaxis.points if self.MODE == POINT_MODE else self.yaxis.contiguous_bounds()

        if isinstance(data_object, Cube):
            data, x, y = self._cube_manipulation(data_object, x, y)
        else:
            data = data_object.data

        logging.debug("Shape of x: " + str(x.shape))
        if y is not None:
            logging.debug("Shape of y: " + str(y.shape))
        logging.debug("Shape of data: " + str(data.shape))

        return data, x, y

    @staticmethod
    def _cube_manipulation(cube, x, y):
        import iris.plot as iplt
        import iris
        from cartopy.util import add_cyclic_point
        import numpy as np

        no_of_dims = len(cube.shape)
        data = cube.data

        plot_defn = iplt._get_plot_defn(cube, iris.coords.POINT_MODE, ndims=no_of_dims)
        if plot_defn.transpose:
            data = data.T
            x = x.T
            y = y.T

        # Check for auxiliary coordinates.
        aux_coords = False
        for coord in cube[0].coords(dim_coords=False):
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
        return data, x, y