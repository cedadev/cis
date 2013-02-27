from generic_plot import Generic_Plot

class Comparative_Scatter(Generic_Plot):
    def plot(self):
        self.mplkwargs.pop("latlon", None)
        self.plot_method.scatter(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], c="b", s=20, edgecolors = "none", *self.mplargs, **self.mplkwargs)

    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        from generic_plot import is_map
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        from plot import format_units
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if is_map(self.packed_data_items[0]):
                self.plot_args[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    units = self.packed_data_items[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                if len(self.packed_data_items) == 1:
                    # only 1 data to plot, display
                    try:
                        name = self.packed_data_items[0].coord(axis=axis).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = self.packed_data_items[0].name()
                    self.plot_args[axislabel] = name + format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = units

    def create_legend(self):
        pass


