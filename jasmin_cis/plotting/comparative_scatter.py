from generic_plot import Generic_Plot

class Comparative_Scatter(Generic_Plot):
    def plot(self):
        # Add y=x line
        min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
        max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
        y_equals_x_array = [min_val, max_val]
        self.matplotlib.plot(y_equals_x_array, y_equals_x_array, color = "black", linestyle = "dashed")

        scatter_size = self.plot_args.get("itemwidth", 1) if self.plot_args.get("itemwidth", 1) is not None else 1
        datagroup = self.plot_args["datagroups"][0]
        marker = datagroup["itemstyle"] if datagroup["itemstyle"] else 'o'
        colour = datagroup["color"] if datagroup["color"] else "b"

        self.mplkwargs.pop("latlon", None)

        self.matplotlib.scatter(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], color=colour, marker=marker, s=scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs)

    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        from plot import format_units
        axis = axis.lower()
        axislabel = axis + "label"
        if axis == 'x':
            item_index = 0
        elif axis == 'y':
            item_index = 1

        if self.plot_args[axislabel] is None:
            units = self.packed_data_items[item_index].units
            name = self.packed_data_items[item_index].name()
            self.plot_args[axislabel] = name + format_units(units)

    def create_legend(self):
        pass

    def draw_coastlines(self, draw_grid = False):
        pass


