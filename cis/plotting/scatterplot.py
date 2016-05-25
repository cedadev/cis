from cis.plotting.genericplot import GenericPlot, Generic2DPlot
from cis.plotting.APlot import APlot


# TODO: The generic scatter shouldn't have any of the if 2D stuff in...
class GenericScatter(APlot):

    @staticmethod
    def guess_axis_label(data, axisvar=None, axis=None):
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        from .APlot import format_units

        try:
            units = data[0].coord(axisvar).units
        except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
            units = data[0].units

        if len(data) == 1:
            try:
                name = data[0].coord(axisvar).name()
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                name = data[0].name()
            # only 1 data to plot, display
            label = name + " " + format_units(units)
        else:
            # if more than 1 data, legend will tell us what the name is. so just displaying units
            label = format_units(units)
        return label


class ScatterPlot(GenericPlot, GenericScatter):

    def plot(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        # TODO: This is better now but I'm still not convinced about having mplkwargs being changed globably like this
        self.mplkwargs["s"] = self.itemwidth

        self.mplkwargs["marker"] = self.itemstyle

        self.mplkwargs["edgecolors"] = self.edgecolor

        self.mplkwargs["c"] = self.color

        self.color_axis.append(self.ax.scatter(self.x, self.data, *self.mplargs, **self.mplkwargs))


class ScatterPlot2D(Generic2DPlot, GenericScatter):

    def plot(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        self.mplkwargs["s"] = self.itemwidth

        self.mplkwargs["marker"] = self.itemstyle

        self.mplkwargs["cmap"] = self.cmap

        self.mplkwargs["edgecolors"] = self.edgecolor

        self.mplkwargs["c"] = self.data

        self.color_axis.append(
            self.ax.scatter(self.x, self.y, *self.mplargs, **self.mplkwargs))
