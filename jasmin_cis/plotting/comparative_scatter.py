from jasmin_cis.plotting.generic_plot import Generic_Plot

class Comparative_Scatter(Generic_Plot):
    def plot(self):
        # Add y=x line
        ax = self.matplotlib.gca()
        if self.plot_args.get("logx", False) and self.plot_args.get("logy", False):
            import numpy.ma as ma
            positive_item0 = ma.array(self.unpacked_data_items[0]["data"], mask=self.unpacked_data_items[0]["data"]<=0)
            positive_item1 = ma.array(self.unpacked_data_items[1]["data"], mask=self.unpacked_data_items[1]["data"]<=0)
            min_val = min(positive_item0.min(), positive_item1.min())
            max_val = max(positive_item0.max(), positive_item1.max())
        else:
            min_val = min(self.unpacked_data_items[0]["data"].min(), self.unpacked_data_items[1]["data"].min())
            max_val = max(self.unpacked_data_items[0]["data"].max(), self.unpacked_data_items[1]["data"].max())
        y_equals_x_array = [min_val, max_val]
        ax.plot(y_equals_x_array, y_equals_x_array, color = "black", linestyle = "dashed")

        scatter_size = self.plot_args.get("itemwidth", 1) if self.plot_args.get("itemwidth", 1) is not None else 1
        datagroup = self.plot_args["datagroups"][0]
        marker = datagroup["itemstyle"] if datagroup["itemstyle"] else 'o'
        colour = datagroup["color"] if datagroup["color"] else "b"

        self.mplkwargs.pop("latlon", None)

        ax.scatter(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], color=colour, marker=marker, s=scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs)

    def calculate_axis_limits(self, axis):
        valrange = {}
        if axis == "x":
            axis_index = 0
        elif axis == "y":
            axis_index = 1

        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[axis_index]["data"])
        return valrange

    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        self.set_default_axis_label_for_comparative_plot(axis)

    def create_legend(self):
        pass

    def draw_coastlines(self, draw_grid = False):
        pass


