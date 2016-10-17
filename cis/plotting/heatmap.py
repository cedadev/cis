import logging
import numpy

from cis.exceptions import UserPrintableException
from cis.plotting.genericplot import Generic2DPlot


class Heatmap(Generic2DPlot):

    def __init__(self, packed_data_items, ax, *args, **kwargs):
        # Do this here because if this is ungridded data, we won't be able to complete the super() call
        super(Heatmap, self).__init__(packed_data_items, ax, *args, **kwargs)

    def __call__(self):
        """
        Plots a heatmap
        """
        self.ax.pcolormesh(self.x, self.y, self.data, *self.mplargs, **self.mplkwargs)

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
    from cartopy.util import add_cyclic_point
    import iris
    import numpy as np
    import numpy.ma as ma
    data = packed_data_item.data
    x = get_coord(packed_data_item, xvar, data)
    y = get_coord(packed_data_item, yvar, data)
    x_dim = packed_data_item.coord_dims(x)
    y_dim = packed_data_item.coord_dims(y)
    # for coord in (x, y):
    #     if not coord.has_bounds():
    #         coord.guess_bounds()
    # y_bounds = y.bounds
    x_vals = x.contiguous_bounds()
    y_vals = y.contiguous_bounds()

    print(x.points[0], x.points[-1])
    # print x.bounds[0], x.bounds[-1]

    print(x_vals[0], x_vals[-1])

    # if getattr(x, 'circular', False):
    #     data, x_vals = add_cyclic_point(data, x_vals, x_dim[0])

    # print [x.bounds[-1][1]]

    # x_vals = [b[0] for b in x.bounds] #+ [x.bounds[-1][1]]
    # y_vals = [b[0] for b in y_bounds] + [y_bounds[-1][1]]

    print(x_vals[0], x_vals[-1])

    # Get the order right
    if x_dim > y_dim:
        xv, yv = numpy.meshgrid(x_vals, y_vals)
    else:
        yv, xv = numpy.meshgrid(y_vals, x_vals)
    #
    # if getattr(x, 'circular', False):
    #     _, direction = iris.util.monotonic(x.points,
    #                                        return_direction=True)
    #     yv = np.append(yv, yv[:, 0:1], axis=1)
    #     xv = np.append(xv, xv[:, 0:1] + 360 * direction, axis=1)
    #     data = ma.concatenate([data, data[:, 0:1]], axis=1)

    return xv, yv, data
