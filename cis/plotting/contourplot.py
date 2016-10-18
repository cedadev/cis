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

    def __call__(self, ax):
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

        contour_type = ax.contourf if self.filled else ax.contour

        self.mappable = contour_type(self.x, self.y, self.data, **mplkwargs)

        if self.contlabel:
            ax.clabel(self.mappable, **self.cont_label_kwargs)

        super(ContourPlot, self).__call__(ax)

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


class ContourfPlot(ContourPlot):

    def __init__(self, packed_data_items, *args, **kwargs):
        super(ContourfPlot, self).__init__(packed_data_items, *args, **kwargs)
        self.filled = True
