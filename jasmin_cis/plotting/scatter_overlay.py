from generic_plot import Generic_Plot
from heatmap import Heatmap
from scatter_plot import Scatter_Plot
#TODO FIX
class Scatter_Overlay(Generic_Plot):
    def plot(self):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        '''

        Heatmap(self.packed_data_items, self.plot_args, *self.mplargs, **self.mplkwargs)
        scatter_plot_args = self.plot_args
        scatter_plot_args["datagroups"] = self.plot_args["datagroups"][1:]
        self.scatter_plots = Scatter_Plot(self.packed_data_items[1:], self.plot_args, *self.mplargs, **self.mplkwargs)

    def set_axis_label(self, axis, options):
        from generic_plot import is_map
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if is_map(self.packed_data_items[0]):
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_items[0].coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                options[axislabel] = name + format_units(units)

        return options

    def create_legend(self):
        self.scatter_plots.create_legend()

    def format_plot(self):
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)