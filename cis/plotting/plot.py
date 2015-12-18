"""
Class for plotting graphs.
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
from cis.plotting.contour_plot import Contour_Plot
from cis.plotting.contourf_plot import Contourf_Plot
from cis.plotting.heatmap import Heatmap
from cis.plotting.line_plot import Line_Plot
from cis.plotting.scatter_plot import Scatter_Plot
from cis.plotting.comparative_scatter import Comparative_Scatter
from cis.plotting.overlay import Overlay
from cis.plotting.histogram2d import Histogram_2D
from cis.plotting.histogram3d import Histogram_3D
from cis.utils import wrap_longitude_coordinate_values, listify

import matplotlib.pyplot as plt

plot_options = {'title': plt.title,
                'xlabel': plt.xlabel,
                'ylabel': plt.ylabel,
                'fontsize': plt.rcParams.update}

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


class Plotter(object):
    plot_types = {"contour": Contour_Plot,
                  "contourf": Contourf_Plot,
                  "heatmap": Heatmap,
                  "line": Line_Plot,
                  "scatter": Scatter_Plot,
                  "comparativescatter": Comparative_Scatter,
                  "overlay": Overlay,
                  "histogram2d": Histogram_2D,
                  "histogram3d": Histogram_3D}

    def __init__(self, packed_data_items, plot_type=None, out_filename=None, plotheight=None,
                 plotwidth=None, *mplargs, **mplkwargs):
        """
        Constructor for the plotter. Note that this method also does the actual plotting.

        :param packed_data_items: A list of packed (i.e. Iris cubes or UngriddedData objects) data items to be plotted
        :param plot_type: The plot type to be used, as a string
        :param out_filename: The filename of the file to save the plot to. Optional. Various file extensions can be
         used, with png being the default
        :param mplargs: Any other arguments received from the parser
        :param mplkwargs: Any other keyword arguments received from the plotter
        """

        # packed_data_items = self._remove_length_one_dimensions(packed_data_items)

        if plot_type is None:
            plot_type = self.set_default_plot_type(packed_data_items)

        # Create figure and a single axis (we assume for now not more than one 'subplot').
        self.fig, ax = plt.subplots()

        self.set_width_and_height(plotwidth, plotheight)
        plot = self.plot_types[plot_type](ax, packed_data_items, *mplargs, **mplkwargs)
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
        import matplotlib.pyplot as plt
        if out_filename is None:
            plt.show()
        else:
            logging.info("saving plot to file: " + out_filename)
            width = self.fig.get_figwidth()
            plt.savefig(out_filename, bbox_inches='tight',
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

    def set_default_plot_type(self, data):
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

    def _remove_length_one_dimensions(self, packed_data):
        from iris.util import squeeze
        from cis.data_io.gridded_data import GriddedData
        listify(packed_data)
        new_data_list = []
        for data in packed_data:
            if data.is_gridded:
                new_data_list.append(GriddedData.make_from_cube(squeeze(data)))
            else:
                new_data_list.append(data)
        return new_data_list
