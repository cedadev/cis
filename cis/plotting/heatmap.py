import numpy
from cis.plotting.genericplot import Generic2DPlot


class Heatmap(Generic2DPlot):

    def __init__(self, packed_data_items, ax, *args, **kwargs):
        # Do this here because if this is ungridded data, we won't be able to complete the super() call
        super(Heatmap, self).__init__(packed_data_items, ax, *args, **kwargs)

    def __call__(self):
        """
        Plots a heatmap
        """
        self.map = self.ax.pcolormesh(self.x, self.y, self.data, *self.mplargs, **self.mplkwargs)

        super(Heatmap, self).__call__()

    def unpack_data_items(self, packed_data_items, x_wrap_start=None):
        self.x, self.y, self.data = make_color_mesh_cells(packed_data_items, self.xaxis, self.yaxis)


def make_color_mesh_cells(packed_data_item, xvar, yvar):
    """
    Generate the correct cell corners for use with a heatmap, since heatmap doesn't take
    cell centers but cell corners
    :param packed_data_item: IRIS cube
    :param plot_args: dictionary of plot arguments
    :return:
    """
    from cis.utils import get_coord

    data = packed_data_item.data
    x = get_coord(packed_data_item, xvar, data)
    y = get_coord(packed_data_item, yvar, data)

    x_dim = packed_data_item.coord_dims(x)
    y_dim = packed_data_item.coord_dims(y)

    x_vals = x.contiguous_bounds()
    y_vals = y.contiguous_bounds()

    # Get the order right
    if x_dim > y_dim:
        xv, yv = numpy.meshgrid(x_vals, y_vals)
    else:
        yv, xv = numpy.meshgrid(y_vals, x_vals)

    return xv, yv, data
