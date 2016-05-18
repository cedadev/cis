"""
Class for plotting graphs.
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
from cis.plotting.contourplot import ContourPlot, ContourfPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.lineplot import LinePlot
from cis.plotting.scatterplot import ScatterPlot
from cis.plotting.comparativescatter import ComparativeScatter
from cis.plotting.overlay import Overlay
from cis.plotting.histogram import Histogram
from cis.plotting.histogram2d import Histogram2D
import logging

plot_options = {'title': 'set_title',
                'xlabel': 'set_xlabel',
                'ylabel': 'set_ylabel',
                'fontsize': 'matplotlib.rcParams.update'}

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


def is_map(data, xaxis, yaxis):
    """
    :return: A boolean saying if the first packed data item contains lat and lon coordinates
    """
    from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
    from cis.exceptions import CoordinateNotFoundError as cisNotFoundError
    try:
        x = data[0].coord(xaxis)
        y = data[0].coord(yaxis)
    except (cisNotFoundError, irisNotFoundError):
        return False

    if x.name().lower().startswith("lon") and y.name().lower().startswith("lat"):
        return True
    else:
        return False


def name_preferring_standard(coord_item):
    for name in [coord_item.standard_name, coord_item.var_name, coord_item.long_name]:
        if name:
            return name
    return ''


def guess_y_axis(data, xaxis):
    import cis.exceptions as cis_ex
    import iris.exceptions as iris_ex
    yaxis = 'default'
    # If we're not dealing with the case where the xaxis is time and we have many y layers (which should be default)...
    if not (xaxis.lower().endswith('time') and len(data) > 1):
        try:
            return name_preferring_standard(data.coord(axis="Y"))
        except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
            if len(data.shape) > 1:
                number_of_points_in_dimension = data.shape[1]
            else:
                yaxis = "default"

            for coord in data.coords():
                if coord.shape[0] == number_of_points_in_dimension:
                    yaxis = "search:" + str(number_of_points_in_dimension)

    if "search" in yaxis:
        logging.info("Plotting unknown on the y axis")
    else:
        logging.info("Plotting " + yaxis + " on the y axis")
    return yaxis


def guess_x_axis(data):
    import cis.exceptions as cis_ex
    import iris.exceptions as iris_ex

    xaxis = "default"
    try:
        xaxis = name_preferring_standard(data.coord(axis='X'))
    except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
        number_of_points_in_dimension = data.shape[0]

        for coord in data.coords():
            if coord.shape[0] == number_of_points_in_dimension:
                xaxis = "search:" + str(number_of_points_in_dimension)
                break

    if "search" in xaxis:
        logging.info("Plotting unknown on the x axis")
    else:
        logging.info("Plotting " + xaxis + " on the x axis")

    return xaxis


class Plotter(object):
    plot_types = {"contour": ContourPlot,
                  "contourf": ContourfPlot,
                  "heatmap": Heatmap,
                  "line": LinePlot,
                  "scatter": ScatterPlot,
                  "comparativescatter": ComparativeScatter,
                  "overlay": Overlay,
                  "histogram2d": Histogram,
                  "histogram3d": Histogram2D}

    def __init__(self, data, type=None, out_filename=None, xaxis=None, yaxis=None, layer_opts=None, plotheight=None,
                 plotwidth=None, logx=False, logy=False, xmin=None,
                 xmax=None, xstep=None, ymin=None, ymax=None, ystep=None,
                 grid=False, xlabel=None, ylabel=None, title=None, fontsize=None,
                 itemwidth=1, xtickangle=None, ytickangle=None, projection=None, *args, **kwargs):
        """
        Constructor for the plotter. Note that this method also does the actual plotting.

        :param data: A list of packed (i.e. GriddedData or UngriddedData objects) data items to be plotted
        :param type: The plot type to be used, as a string
        :param out_filename: The filename of the file to save the plot to. Optional. Various file extensions can be
         used, with png being the default
        :param args: Any other arguments received from the parser
        :param kwargs: Any other keyword arguments received from the plotter
        """
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs

        if type in self.plot_types:
            type = type
        elif type is None:
            type = self.set_default_plot_type(data)
        else:
            raise ValueError("Invalid plot type, must be one of: {}".format(list(self.plot_types.keys())))

        # TODO: This could become an argument in the future
        # Create figure and a single axis (we assume for now not more than one 'subplot').

        xaxis = xaxis or guess_x_axis(data)
        yaxis = yaxis or guess_y_axis(data, xaxis)

        # TODO
        if projection is None and is_map(data, xaxis, yaxis):
            projection = ccrs.PlateCarree(central_longitude=(get_x_wrap_start(data, xmin) + 180.0))
            kwargs['transform'] = ccrs.PlateCarree()

        self.fig, ax = plt.subplots(projection=projection)

        self.set_width_and_height(plotwidth, plotheight)

        # TODO: Each plot is really just one 'layer', it should only get arguments relevant for that layer.
        for d, params in zip(data, layer_opts):
            plot = self.plot_types[type](d, ax=ax, *args, **layer_opts+kwargs)

        # TODO: All of the below functions should be static, take their own arguments and apply only to the plot.ax
        # instance
        plot.apply_axis_limits()
        plot.format_plot()

        plot.auto_set_ticks()
        self.output_to_file_or_screen(out_filename)

    def output_to_file_or_screen(self, out_filename=None):
        """
        Outputs to screen unless a filename is given

        :param out_filename: The filename of the file to save the plot to. Various file extensions can be used, with
         png being the default
        """
        import logging
        if out_filename is None:
            self.fig.show()
        else:
            logging.info("saving plot to file: " + out_filename)
            width = self.fig.get_figwidth()
            self.fig.savefig(out_filename, bbox_inches='tight',
                             pad_inches=0.05 * width)  # Will overwrite if file already exists

    def set_width_and_height(self, width, height):
        """
        Sets the width and height of the plot
        Uses an aspect ratio of 4:3 if only one of width and height are specified
        If neither width or height are specified it defaults to 8 by 6 inches.
        """

        if height is not None:
            if width is None:
                width = height * (4.0 / 3.0)
        elif width is not None:
            height = width * (3.0 / 4.0)
        else:
            height = 6
            width = 8

        self.fig.set_figheight(height)
        self.fig.set_figwidth(width)

    @staticmethod
    def set_default_plot_type(data):
        """
        Sets the default plot type based on the number of dimensions of the data
        :param data: A list of packed data items
        :return: The default plot type as a string
        """
        from cis.exceptions import InvalidPlotTypeError
        from iris.cube import Cube
        import logging
        number_of_coords = 0
        for coord in data[0].coords(dim_coords=True):
            if len(coord.shape) != 1 or coord.shape[0] != 1:
                number_of_coords += 1
        try:
            if number_of_coords == 1:
                plot_type = "line"
            elif isinstance(data[0], Cube):
                plot_type = "heatmap"
            else:
                plot_type = "scatter"
            logging.info("No plot type specified. Plotting data as a " + plot_type)
            return plot_type
        except KeyError:
            coord_shape = None
            all_coords_are_of_same_shape = False
            for coord in data[0].coords():
                if coord_shape is None:
                    coord_shape = coord.shape
                    all_coords_are_of_same_shape = True
                elif coord_shape != coord.shape:
                    all_coords_are_of_same_shape = False
                    break

            error_message = "There is no valid plot type for this variable\nIts shape is: " + str(data[0].shape)
            if all_coords_are_of_same_shape:
                error_message += "\nThe shape of its coordinates is: " + str(data[0].coords()[0].shape)
            raise InvalidPlotTypeError(error_message)


def get_x_wrap_start(data, user_xmin=None):
    from cis.utils import find_longitude_wrap_start

    # FIND THE WRAP START OF THE DATA
    data_wrap_start = find_longitude_wrap_start(data)

    # NOW find the wrap start of the user specified range
    if user_xmin is not None:
        x_wrap_start = -180 if user_xmin < 0 else 0
    else:
        x_wrap_start = data_wrap_start

    return x_wrap_start
