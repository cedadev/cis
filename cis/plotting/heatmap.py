from cis.plotting.genericplot import Generic2DPlot
from iris.coords import BOUND_MODE


class Heatmap(Generic2DPlot):

    MODE = BOUND_MODE

    def __init__(self, packed_data_items, *args, **kwargs):
        # Do this here because if this is ungridded data, we won't be able to complete the super() call
        super(Heatmap, self).__init__(packed_data_items, *args, **kwargs)

    def __call__(self, ax):
        """
        Plots a heatmap
        """
        self.mappable = ax.pcolormesh(self.x, self.y, self.data, *self.mplargs, **self.mplkwargs)

        super(Heatmap, self).__call__(ax)
