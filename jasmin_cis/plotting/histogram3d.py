from generic_plot import Generic_Plot

class Histogram_3D(Generic_Plot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]
    def plot(self):
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        xbins = self.calculate_number_of_bins("x")
        ybins = self.calculate_number_of_bins("y")

        # Add y=x line
        min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
        max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
        y_equals_x_array = [min_val, max_val]
        self.matplotlib.plot(y_equals_x_array, y_equals_x_array, color = "black", linestyle = "dashed")

        self.matplotlib.hist2d(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], bins = [xbins, ybins], *self.mplargs, **self.mplkwargs)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def calculate_number_of_bins(self, axis):
        if axis == "x":
            axis_index = 0
        elif axis == "y":
            axis_index = 1

        if self.plot_args[axis + "range"] is not None:
            step = self.plot_args[axis + "range"].get(axis + "step", None)
        else:
            step = None

        if step is None:
            number_of_bins = 10
        else:
            number_of_bins = int((self.unpacked_data_items[axis_index]["data"].max() - self.unpacked_data_items[axis_index]["data"].min())/step)

        return number_of_bins

    def format_plot(self):
        self.format_3d_plot()

    def set_default_axis_label(self, axis):
        self.set_default_axis_label_for_comparative_plot(axis)

    def calculate_axis_limits(self, axis):
        valrange = {}
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            coord_axis = "data"
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][coord_axis])
        return valrange

    def apply_axis_limits(self, valrange, axis):
        if valrange is not None:
            if axis == "x":
                step = valrange.pop("xstep", None)
                self.matplotlib.xlim(**valrange)
                if step is not None: valrange["xstep"] = step
            elif axis == "y":
                step = valrange.pop("ystep", None)
                self.matplotlib.ylim(**valrange)
                if step is not None: valrange["ystep"] = step

    def create_legend(self):
        pass

    def add_color_bar(self):
        cbar = self.matplotlib.colorbar(orientation = self.plot_args["cbarorient"])

        cbar.set_label("Frequency")


