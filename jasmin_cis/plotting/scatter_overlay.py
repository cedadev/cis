from jasmin_cis.plotting.generic_plot import Generic_Plot
from jasmin_cis.plotting.heatmap import Heatmap
from jasmin_cis.plotting.scatter_plot import Scatter_Plot

class Scatter_Overlay(Generic_Plot):
    def plot(self):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        '''
        from jasmin_cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) > 1:
            Heatmap([self.packed_data_items[0]], self.plot_args, *self.mplargs, **self.mplkwargs)
            scatter_plot_args = self.plot_args
            scatter_plot_args["datagroups"] = self.plot_args["datagroups"][1:]
            self.scatter_plots = Scatter_Plot(self.packed_data_items[1:], scatter_plot_args, calculate_min_and_max_values = False, *self.mplargs, **self.mplkwargs)
        else:
            raise InvalidNumberOfDatagroupsSpecifiedError("Scatter overlay requires two or more datagroups")

    def set_axis_label(self, axis, options):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if self.is_map():
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                options[axislabel] = name + " " + self.format_units(units)

        return options

    def create_legend(self):
        self.scatter_plots.create_legend()

    def format_plot(self):
        self.format_time_axis()
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)