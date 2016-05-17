"""
Class for plotting graphs.
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
from cis.plotting.contourplot import ContourPlot
from cis.plotting.contourfplot import ContourfPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.lineplot import LinePlot
from cis.plotting.scatterplot import ScatterPlot
from cis.plotting.comparativescatter import ComparativeScatter
from cis.plotting.overlay import Overlay
from cis.plotting.histogram import Histogram
from cis.plotting.histogram2d import Histogram2D

plot_options = {'title': 'set_title',
                'xlabel': 'set_xlabel',
                'ylabel': 'set_ylabel',
                'fontsize': 'matplotlib.rcParams.update'}

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


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

    def __init__(self, data, type=None, out_filename=None, plotheight=None,
                 plotwidth=None, *args, **kwargs):
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

        if type in self.plot_types:
            type = type
        elif type is None:
            type = self.set_default_plot_type(data)
        else:
            raise ValueError("Invalid plot type, must be one of: {}".format(list(self.plot_types.keys())))

        # Create figure and a single axis (we assume for now not more than one 'subplot').
        self.fig, ax = plt.subplots()

        self.set_width_and_height(plotwidth, plotheight)
        plot = self.plot_types[type](data, ax=ax, *args, **kwargs)
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
