from cis.plotting.genericplot import GenericPlot, Generic2DPlot
from cis.plotting.APlot import APlot


# TODO: The generic scatter shouldn't have any of the if 2D stuff in...
class GenericScatter(APlot):

    pass
    # @staticmethod
    # def guess_axis_label(data, axisvar=None, axis=None):
    #     import cis.exceptions as cisex
    #     import iris.exceptions as irisex
    #     from .APlot import format_units
    #
    #     try:
    #         units = data.coord(axisvar).units
    #     except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
    #         units = data.units
    #
    #     try:
    #         name = data[0].coord(axisvar).name()
    #     except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
    #         name = data[0].name()
    #     # only 1 data to plot, display
    #     label = name + " " + format_units(units)
    #
    #     return label


class ScatterPlot(GenericPlot, GenericScatter):

    def __call__(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        super(ScatterPlot, self).__call__()
        # TODO: This is better now but I'm still not convinced about having mplkwargs being changed globably like this
        if self.itemwidth is not None:
            self.mplkwargs["s"] = self.itemwidth

        if self.itemstyle is not None:
            self.mplkwargs["marker"] = self.itemstyle

        if self.edgecolor is not None:
            self.mplkwargs["edgecolors"] = self.edgecolor

        if self.color is not None:
            self.mplkwargs["c"] = self.color

        # By plotting the data as flat arrays with a line style of 'o' we get a scatter plot - with the added
        #  benefit of not having to keep track of the layers ourselves.
        self.ax.plot(self.x.flat, self.data.flat, 'o', *self.mplargs, **self.mplkwargs)


class ScatterPlot2D(Generic2DPlot, GenericScatter):

    def __call__(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        super(ScatterPlot2D, self).__call__()

        self.mplkwargs["s"] = self.itemwidth

        self.mplkwargs["marker"] = self.itemstyle

        self.mplkwargs["cmap"] = self.cmap

        self.mplkwargs["edgecolors"] = self.edgecolor

        self.mplkwargs["c"] = self.data

        self.ax.scatter(self.x, self.y, *self.mplargs, **self.mplkwargs)
