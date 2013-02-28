'''
Class for plotting graphs.
Also contains dictionaries for the valid plot types and formatting options
'''
from contour_plot import Contour_Plot
from contourf_plot import Contourf_Plot
from heatmap import Heatmap
from line_plot import Line_Plot
from scatter_overlay import Scatter_Overlay
from scatter_plot import Scatter_Plot
from comparative_scatter import Comparative_Scatter
from histogram2d import Histogram_2D
from histogram3d import Histogram_3D
import matplotlib.pyplot as mpl

def format_units(units):
    if units:
        return " ($" + str(units) + "$)"
    else:
        return ""

plot_options = { 'title' : mpl.title,
                 'xlabel' : mpl.xlabel,
                 'ylabel' : mpl.ylabel,
                 'fontsize' : mpl.rcParams.update }

class Plotter(object):

    
    default_plot_types = { 1 : 'line',
                           2 : 'heatmap'}

    plot_types = {"contour" : Contour_Plot,
                  "contourf" : Contourf_Plot,
                  "heatmap" : Heatmap,
                  "line": Line_Plot,
                  "scatteroverlay" : Scatter_Overlay,
                  "scatter" : Scatter_Plot,
                  "comparativescatter" : Comparative_Scatter,
                  "histogram2d" : Histogram_2D,
                  "histogram3d" : Histogram_3D}

    def __init__(self, packed_data_items, plot_args, plot_type = None, out_filename = None, *mplargs, **mplkwargs):
        '''
        Constructor for the Plotter
        
        @param data             A list of data objects (either Cubes or UngriddedData)
        @param plot_type        The plot type, as a string
        @param out_filename     The filename to save the plot to
        @param *mplargs            mplargs to be passed into matplotlib
        @param **mplkwargs         kwargs to be passed into matplotlib
        '''
        self.mplkwargs = mplkwargs
        self.remove_unassigned_arguments()

        self.packed_data_items = packed_data_items
        v_range = self.mplkwargs.pop("valrange", {})

        if plot_args.get("logv", False):
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        if plot_type is None: plot_type = self.__set_default_plot_type(packed_data_items)

        # Do plot
        self.plot_types[plot_type](packed_data_items, v_range, plot_args, out_filename, *mplargs, **mplkwargs)

    def remove_unassigned_arguments(self):
        '''
        Removes arguments from the mplkwargs if they are equal to None
        '''
        for key in self.mplkwargs.keys():
            if self.mplkwargs[key] is None:
                self.mplkwargs.pop(key)

    def __set_default_plot_type(self, data):
        '''
        Sets the default plot type based on the number of dimensions of the data
        '''
        from jasmin_cis.exceptions import InvalidPlotTypeError
        variable_dim = len(data[0].shape) # The first data object is arbitrarily chosen as all data objects should be of the same shape anyway
        try:
            return self.default_plot_types[variable_dim]
        except KeyError:
            raise InvalidPlotTypeError("There is no valid plot type for this variable - check its dimensions")