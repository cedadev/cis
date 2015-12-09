from cis.plotting.generic_plot import Generic_Plot


class Line_Plot(Generic_Plot):
    line_styles = ["solid", "dashed", "dashdot", "dotted"]

    def plot(self):
        """
        Plots one or many line graphs
        """
        self.mplkwargs["linewidth"] = self.plot_args.get("itemwidth", 1) if self.plot_args.get("itemwidth",
                                                                                               1) is not None else 1

        self.mplkwargs.pop("vmax", None)
        self.mplkwargs.pop("vmin", None)

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.plot_args["datagroups"][i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in Line_Plot.line_styles:
                    self.mplkwargs["linestyle"] = datafile["itemstyle"]
                else:
                    from cis.exceptions import InvalidLineStyleError
                    raise InvalidLineStyleError(
                        "'" + datafile["itemstyle"] + "' is not a valid line style, please use one of: " + str(
                            self.line_styles))
            else:
                self.mplkwargs.pop("linestyle", None)

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs.pop("color", None)

            self.matplotlib.plot(unpacked_data_item["x"], unpacked_data_item["data"], *self.mplargs, **self.mplkwargs)

    def format_plot(self):
        self.format_time_axis()
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            try:
                units = self.packed_data_items[0].coord(self.plot_args[axis + "_variable"]).units
            except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                units = self.packed_data_items[0].units

            if len(self.packed_data_items) == 1:
                try:
                    name = self.packed_data_items[0].coord(self.plot_args[axis + "_variable"]).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()
                # only 1 data to plot, display
                self.plot_args[axislabel] = name + " " + self.format_units(units)
            else:
                # if more than 1 data, legend will tell us what the name is. so just displaying units
                self.plot_args[axislabel] = self.format_units(units)

    def calculate_axis_limits(self, axis, min_val, max_val):
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            coord_axis = "data"
        c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis, self.unpacked_data_items[0][coord_axis])

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.plot_args["y_variable"] == "air_pressure" and min_val is None and max_val is None:
            new_min, new_max = new_max, new_min

        return new_min, new_max
