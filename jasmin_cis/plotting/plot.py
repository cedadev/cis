'''
Class for plotting graphs.
Also contains a dictionary for the valid plot types
All plot types need to be imported and added to the plot_types dictionary in order to be used.
'''
from jasmin_cis.plotting.contour_plot import Contour_Plot
from jasmin_cis.plotting.contourf_plot import Contourf_Plot
from jasmin_cis.plotting.heatmap import Heatmap
from jasmin_cis.plotting.line_plot import Line_Plot
from jasmin_cis.plotting.scatter_overlay import Scatter_Overlay
from jasmin_cis.plotting.scatter_plot import Scatter_Plot
from jasmin_cis.plotting.comparative_scatter import Comparative_Scatter
from jasmin_cis.plotting.overlay import Overlay
from jasmin_cis.plotting.histogram2d import Histogram_2D
from jasmin_cis.plotting.histogram3d import Histogram_3D
from jasmin_cis.utils import wrap_longitude_coordinate_values
import matplotlib.pyplot as mpl

plot_options = { 'title' : mpl.title,
                 'xlabel' : mpl.xlabel,
                 'ylabel' : mpl.ylabel,
                 'fontsize' : mpl.rcParams.update }

class Plotter(object):

    plot_types = {"contour" : Contour_Plot,
                  "contourf" : Contourf_Plot,
                  "heatmap" : Heatmap,
                  "line": Line_Plot,
                  "scatteroverlay" : Scatter_Overlay,
                  "scatter" : Scatter_Plot,
                  "comparativescatter" : Comparative_Scatter,
                  "overlay" : Overlay,
                  "histogram2d" : Histogram_2D,
                  "histogram3d" : Histogram_3D}

    def __init__(self, packed_data_items, plot_type = None, out_filename = None, *mplargs, **mplkwargs):
        '''
        Constructor for the plotter

        :param packed_data_items: A list of packed (i.e. Iris cubes or UngriddedData objects) data items to be plotted
        :param plot_type: The plot type to be used, as a string
        :param out_filename: The filename of the file to save the plot to. Optional. Various file extensions can be used, with png being the default
        :param mplargs: Any other arguments received from the parser
        :param mplkwargs: Any other keyword arguments received from the plotter
        '''
        mplkwargs.pop("xmin", None)
        mplkwargs.pop("xmax", None)
        mplkwargs.pop("xstep", None)

        mplkwargs.pop("ymin", None)
        mplkwargs.pop("ymax", None)
        mplkwargs.pop("ystep", None)

        mplkwargs.pop("vmin", None)
        mplkwargs.pop("vmax", None)
        mplkwargs.pop("vstep", None)

        # Remove arguments from mplkwargs that cannot be passed directly into the plotting methods
        plot_args = {"datagroups" : mplkwargs.pop("datagroups", None),
                     "nocolourbar" : mplkwargs.pop("nocolourbar", False),
                     "logx" : mplkwargs.pop("logx", False),
                     "logy" : mplkwargs.pop("logy", False),
                     "logv" : mplkwargs.pop("logv", False),
                     "xrange" : mplkwargs.pop("xrange", {}),
                     "yrange" : mplkwargs.pop("yrange", {}),
                     "valrange" : mplkwargs.pop("valrange", {}),
                     "cbarorient" : mplkwargs.pop("cbarorient", "horizontal"),
                     "grid" : mplkwargs.pop("grid", False),
                     "xlabel" : mplkwargs.pop("xlabel", None),
                     "ylabel" : mplkwargs.pop("ylabel", None),
                     "cbarlabel" : mplkwargs.pop("cbarlabel", None),
                     "title" : mplkwargs.pop("title", None),
                     "fontsize" : mplkwargs.pop("fontsize", None),
                     "itemwidth" : mplkwargs.pop("itemwidth", 1),
                     "xtickangle" : mplkwargs.pop("xtickangle", None),
                     "ytickangle" : mplkwargs.pop("ytickangle", None),
                     "xbinwidth" : mplkwargs.pop("xbinwidth", None),
                     "ybinwidth" : mplkwargs.pop("ybinwidth", None),
                     "coastlinescolour" : mplkwargs.pop("coastlinescolour", "k"),
                     "nasabluemarble" : mplkwargs.pop("nasabluemarble", False),
                     "x_variable" : mplkwargs.pop("x_variable"),
                     "y_variable" : mplkwargs.pop("y_variable"),
                     "plotwidth" : mplkwargs.pop("plotwidth"),
                     "plotheight" : mplkwargs.pop("plotheight"),
                     "cbarscale" : mplkwargs.pop("cbarscale") }

        self.mplkwargs = mplkwargs
        self.remove_unassigned_arguments()

        if plot_type is None: plot_type = self.set_default_plot_type(packed_data_items)

        # Do wrapping
        x_range = plot_args.get('xrange', None)
        if x_range is not None:
            x_min = x_range.get('xmin', None)
            x_max = x_range.get('xmax', None)
            if x_min is not None and x_max is not None:
                plot_args['xrange']['xmin'], plot_args['xrange']['xmax'] = \
                    wrap_longitude_coordinate_values(x_min, x_max)

        # Do plot
        f = mpl.gcf()
        f.set_figwidth(plot_args["plotwidth"])
        f.set_figheight(plot_args["plotheight"])
        plot = self.plot_types[plot_type](packed_data_items, plot_args, *mplargs, **mplkwargs)
        plot.format_plot()
        plot.apply_axis_limits(plot_args["xrange"], "x")
        plot.apply_axis_limits(plot_args["yrange"], "y")
        plot.auto_set_ticks()
        self.output_to_file_or_screen(out_filename)

    def output_to_file_or_screen(self, out_filename = None):
        '''
        Outputs to screen unless a filename is given
        :param out_filename: The filename of the file to save the plot to. Various file extensions can be used, with png being the default
        '''
        import logging
        import matplotlib.pyplot as plt
        if out_filename is None:
            plt.show()
        else:
            logging.info("saving plot to file: " + out_filename)
            f = plt.gcf()
            width = f.get_figwidth()
            plt.savefig(out_filename, bbox_inches='tight', pad_inches=0.05 * width)  # Will overwrite if file already exists

    def remove_unassigned_arguments(self):
        '''
        Removes arguments from the mplkwargs if they are equal to None
        '''
        for key in self.mplkwargs.keys():
            if self.mplkwargs[key] is None:
                self.mplkwargs.pop(key)

    def set_default_plot_type(self, data):
        '''
        Sets the default plot type based on the number of dimensions of the data
        :param data: A list of packed data items
        :return: The default plot type as a string
        '''
        from jasmin_cis.exceptions import InvalidPlotTypeError
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
                if coord_shape == None:
                    coord_shape = coord.shape
                    all_coords_are_of_same_shape = True
                elif coord_shape != coord.shape:
                    all_coords_are_of_same_shape = False
                    break

            error_message = "There is no valid plot type for this variable\nIts shape is: " + str(data[0].shape)
            if all_coords_are_of_same_shape:
                error_message += "\nThe shape of its coordinates is: " + str(data[0].coords()[0].shape)
            raise InvalidPlotTypeError(error_message)
