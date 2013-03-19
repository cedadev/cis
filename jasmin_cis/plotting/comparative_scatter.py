from jasmin_cis.plotting.generic_plot import Generic_Plot

class Comparative_Scatter(Generic_Plot):
    def plot(self):
        from jasmin_cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) == 2:
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
            if datagroup["itemstyle"]:
                self.mplkwargs["marker"] = datagroup["itemstyle"]
            else:
                self.mplkwargs.pop("marker", None)

            if datagroup["color"]:
                self.mplkwargs["color"] = datagroup["color"]
            else:
                self.mplkwargs.pop("color", None)

            ax.scatter(self.unpacked_data_items[0]["data"], self.unpacked_data_items[1]["data"], s=scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs)
        else:
            raise InvalidNumberOfDatagroupsSpecifiedError("Comparative scatter requires two datagroups")

    def unpack_data_items(self):
        return self.unpack_comparative_data()

    def calculate_axis_limits(self, axis, min_val, max_val, step):
        if axis == "x":
            axis_index = 0
        elif axis == "y":
            axis_index = 1

        calculated_min, calculated_max = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[axis_index]["data"])

        valrange = {}
        valrange[axis + "min"] = calculated_min if min_val is None else min_val
        valrange[axis + "max"] = calculated_max if max_val is None else max_val
        valrange[axis + "step"] = step

        return valrange

    def format_plot(self):
        # We don't format the time axis here as we're only plotting data against data
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        self.set_default_axis_label_for_comparative_plot(axis)

    def create_legend(self):
        pass

    def is_map(self):
        return False
