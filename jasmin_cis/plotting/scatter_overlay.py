from generic_plot import Generic_Plot
from heatmap import Heatmap
from scatter_plot import Scatter_Plot
#TODO FIX
class Scatter_Overlay(Generic_Plot):
    #'scatteroverlay' : PlotType(None, 2, plot_scatteroverlay)
    def plot(self):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        Heatmap(self.packed_data_items, self.v_range, self.plot_args, *self.mplargs, **self.mplkwargs).plot()
        scatter_plot_args = self.plot_args
        scatter_plot_args["datagroups"] = self.plot_args["datagroups"][1:]
        self.scatter_plots = Scatter_Plot(self.packed_data_items[1:], self.v_range, self.plot_args, *self.mplargs, **self.mplkwargs)
        self.scatter_plots.plot()

    def set_axis_label(self, axis, options):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if self.__is_map():
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.data[0].coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.data[0].name()

                try:
                    units = self.data[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.data[0].units

                # in general, display both name and units in brackets
                options[axislabel] = name + self.__format_units(units)

        return options

    def create_legend(self):
        self.scatter_plots.create_legend()
        '''
        legend_titles = []
        datagroups = self.plot_args["datagroups"]
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                if " " in item.long_name:
                    legend_titles.append(" ".join(item.long_name.split()[:-1]))
                else:
                    legend_titles.append(item.long_name)
        handles = self.plots[1:]
        legend_titles = legend_titles[1:]
        legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)'''

    def format_plot(self):
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)