from cis.plotting.genericplot import GenericPlot, Generic2DPlot


class ScatterPlot(GenericPlot):

    # def __init__(self, packed_data, *args, **kwargs):
    #     super(ScatterPlot, self).__init__(packed_data, *args, **kwargs)
    #     self.xlabel = self.x.name()
    #     self.ylabel = self.data.name()

    def __call__(self, ax):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        # TODO: This is better now but I'm still not convinced about having mplkwargs being changed globably like this
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
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        # TODO: Refactor these checks, maybe create a dict of mplkwargs and local attributes to loop over, and probably
        #  combine with the normal scatter plot above
        if self.itemwidth is not None:
            self.mplkwargs["s"] = self.itemwidth

        if self.itemstyle is not None:
            self.mplkwargs["marker"] = self.itemstyle

        if self.edgecolor is not None:
            self.mplkwargs["edgecolors"] = self.edgecolor
        else:
            self.mplkwargs["edgecolors"] = ''
            
        self.mplkwargs["c"] = self.data

        self.mappable = ax.scatter(self.x, self.y, *self.mplargs, **self.mplkwargs)

        super(ScatterPlot2D, self).__call__(ax)
