import logging
from cis.plotting.genericplot import APlot


class ComparativeScatter(APlot):

    def __init__(self, packed_data_items, *mplargs, **mplkwargs):
        super(ComparativeScatter, self).__init__(packed_data_items, *mplargs, **mplkwargs)

        logging.debug("Unpacking the data items")
        self.x, self.y = self.xaxis.data, packed_data_items.data

        self.label = packed_data_items.long_name if self.label is None else self.label

        self.xlabel = self.xaxis.name()
        self.ylabel = packed_data_items.name()

    def __call__(self):
        if self.itemwidth is not None:
            self.mplkwargs["s"] = self.itemwidth

        if self.itemstyle is not None:
            self.mplkwargs["marker"] = self.itemstyle

        if self.edgecolor is not None:
            self.mplkwargs["edgecolors"] = self.edgecolor

        if self.color is not None:
            self.mplkwargs["c"] = self.color

        if self.label is not None:
            self.mplkwargs['label'] = self.label

        self.ax.scatter(self.x, self.y, *self.mplargs, **self.mplkwargs)

        self._plot_xy_line()

        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def _plot_xy_line(self):
        import numpy as np
        # Turn the scaling off so that we don't change the limits by plotting the line
        self.ax.set_autoscale_on(False)

        lims = [np.min([self.ax.get_xlim(), self.ax.get_ylim()]),  # min of both axes
                np.max([self.ax.get_xlim(), self.ax.get_ylim()])]  # max of both axes

        # now plot both limits against each other for the x=y line
        self.ax.plot(lims, lims, color="black", linestyle="dashed")

        # Turn scaling back on
        self.ax.set_autoscale_on(True)
