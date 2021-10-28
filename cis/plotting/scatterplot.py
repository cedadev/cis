"""
Basic scatter plots, against either one or two coordinates.
"""
from cis.plotting.genericplot import GenericPlot, Generic2DPlot


class ScatterPlot(GenericPlot):

    def __call__(self, ax):
        """
        Plots one set of scatter points
        """
        # Translate our argument names to mpl line kwargs
        if self.itemwidth is not None:
            self.mplkwargs["markersize"] = self.itemwidth

        if self.itemstyle is not None:
            self.mplkwargs["marker"] = self.itemstyle

        if self.edgecolor is not None:
            self.mplkwargs["edgecolors"] = self.edgecolor

        if self.color is not None:
            self.mplkwargs["c"] = self.color

        # By plotting the data as flat arrays with a line style of 'o' we get a scatter plot - with the added
        #  benefit of not having to keep track of the layers ourselves.
        ax.plot(self.x.flatten(), self.data.flatten(), 'o', *self.mplargs, **self.mplkwargs)

        super(ScatterPlot, self).__call__(ax)


class ScatterPlot2D(Generic2DPlot):

    def __call__(self, ax):
        """
        Plots one set of scatter points with the colour determined by the data
        """
        if self.itemwidth is not None:
            self.mplkwargs["s"] = self.itemwidth

        if self.itemstyle is not None:
            self.mplkwargs["marker"] = self.itemstyle

        if self.edgecolor is not None:
            self.mplkwargs["edgecolors"] = self.edgecolor
        else:
            # For 2D scatter plots set the edgecolors off by default
            self.mplkwargs["edgecolors"] = None

        self.mplkwargs["c"] = self.data

        self.mappable = ax.scatter(self.x, self.y, *self.mplargs, **self.mplkwargs)

        super(ScatterPlot2D, self).__call__(ax)
