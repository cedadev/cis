import logging
import numpy

from cis.exceptions import UserPrintableException
from cis.plotting.generic_plot import Generic_Plot


class Heatmap(Generic_Plot):

    def __init__(self, ax, packed_data_items, plot_args, *mplargs, **mplkwargs):
        # Do this here because if this is ungridded data, we won't be able to complete the super() call
        if not packed_data_items[0].is_gridded:
            raise UserPrintableException("Heatmap can only be plotted for gridded data")
        super(Heatmap, self).__init__(ax, packed_data_items, plot_args, *mplargs, **mplkwargs)

    def plot(self):
        """
        Plots a heatmap
        """
        from cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) != 1:
            raise InvalidNumberOfDatagroupsSpecifiedError("Invalid number of datagroups specified. Only one datagroup "
                                                          "can be plotted for a heatmap.")

        if not self.packed_data_items[0].is_gridded:
            raise UserPrintableException("Heatmap can only be plotted for gridded data")

        # Set the options specific to a datagroup with the heatmap type
        self.mplkwargs['cmap'] = self.plot_args['datagroups'][self.datagroup]['cmap']

        if self.plot_args['datagroups'][self.datagroup]['cmin'] is not None:
            self.plot_args["vmin"] = self.plot_args['datagroups'][self.datagroup]['cmin']
        if self.plot_args['datagroups'][self.datagroup]['cmax'] is not None:
            self.plot_args["vmax"] = self.plot_args['datagroups'][self.datagroup]['cmax']

        # if self.is_map():
        #     self.mplkwargs["latlon"] = True

        x, y, data = make_color_mesh_cells(self.packed_data_items[0], self.plot_args)

        self.color_axis.append(self.matplotlib.pcolormesh(x, y, data, *self.mplargs, **self.mplkwargs))

    def get_data_items_max(self):
        # Take into account the bounds
        x_coord = self.packed_data_items[0].coord(self.plot_args['x_variable'])
        if not x_coord.has_bounds():
            x_coord.guess_bounds()
        return numpy.max(x_coord.bounds)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def create_legend(self):
        pass

    def format_plot(self):
        self.format_time_axis()
        self.format_3d_plot()


def make_color_mesh_cells(packed_data_item, plot_args):
    """
    Generate the correct cell corners for use with a heatmap, since heatmap doesn't take
    cell centers but cell corners
    :param packed_data_item: IRIS cube
    :param plot_args: dictionary of plot arguments
    :return:
    """
    from cis.utils import get_coord
    data = packed_data_item.data
    x = get_coord(packed_data_item, plot_args['x_variable'], data)
    y = get_coord(packed_data_item, plot_args['y_variable'], data)
    x_dim = packed_data_item.coord_dims(x)
    y_dim = packed_data_item.coord_dims(y)
    for coord in (x, y):
        if not coord.has_bounds():
            coord.guess_bounds()
    y_bounds = y.bounds
    x_vals = [b[0] for b in x.bounds] + [x.bounds[-1][1]]
    y_vals = [b[0] for b in y_bounds] + [y_bounds[-1][1]]

    # Get the order right
    if x_dim > y_dim:
        xv, yv = numpy.meshgrid(x_vals, y_vals)
    else:
        yv, xv = numpy.meshgrid(y_vals, x_vals)

    return xv, yv, data
