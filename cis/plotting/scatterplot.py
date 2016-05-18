from cis.plotting.genericplot import GenericPlot


class ScatterPlot(GenericPlot):
    def plot(self):
        """
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        """
        from cis.plotting.plot import colors

        self.mplkwargs["s"] = self.itemwidth

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            local_kwargs = self.mplkwargs.copy()
            datafile = self.datagroups[i]

            if "itemstyle" in datafile:
                local_kwargs["marker"] = datafile["itemstyle"]

            if 'cmap' in datafile:
                local_kwargs["cmap"] = datafile["cmap"]

            # Default to no edgecolour
            if "edgecolor" in datafile:
                local_kwargs["edgecolors"] = datafile["edgecolor"]
            elif 'marker' not in local_kwargs or local_kwargs['marker'] == 'o':
                local_kwargs["edgecolors"] = 'None'

            if "c" not in local_kwargs:
                if datafile.get("color", None):
                    local_kwargs["c"] = datafile["color"]
                elif unpacked_data_item.get("y", None) is not None:  # i.e. the scatter plot is 3D
                    local_kwargs["c"] = unpacked_data_item["data"]
                else:
                    local_kwargs["c"] = colors[i % len(colors)]

            x_coords = unpacked_data_item["x"]

            if unpacked_data_item.get("y", None) is not None:
                # 3D
                self.scatter_type = "3D"
                y_coords = unpacked_data_item["y"]
            else:
                # 2D
                self.scatter_type = "2D"
                y_coords = unpacked_data_item["data"]

            self.color_axis.append(
                self.matplotlib.scatter(x_coords, y_coords, *self.mplargs, **local_kwargs))

    def calculate_axis_limits(self, axis, min_val, max_val):
        """
        :param axis: The axis to calculate the limits for
        :param min_val: The user specified minimum value for the axis
        :param max_val: The user specified maximum value for the axis
        :param step: The distance between each tick on the axis
        :return: A dictionary containing the min and max values for the axis, and the step between each tick
        """
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            if self.scatter_type == "2D":
                coord_axis = "data"
            elif self.scatter_type == "3D":
                coord_axis = "y"
        c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis, self.unpacked_data_items[0][coord_axis])

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.yaxis == "air_pressure" and min_val is None and max_val is None:
            new_min, new_max = new_max, new_min

        return new_min, new_max

    def format_plot(self):
        self.format_time_axis()
        if self.scatter_type == "3D":
            self.format_3d_plot()
        elif self.scatter_type == "2D":
            self.format_2d_plot()

    def set_default_axis_label(self, axis):
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        from .APlot import format_units
        axis = axis.lower()
        axislabel = axis + "label"

        if getattr(self, axislabel) is None:
            if self.is_map():
                setattr(self, axislabel, "Longitude" if axis == "x" else "Latitude")
            else:
                try:
                    units = self.packed_data_items[0].coord(getattr(self, axis + "axis")).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                if len(self.packed_data_items) == 1:
                    # only 1 data to plot, display
                    try:
                        name = self.packed_data_items[0].coord(getattr(self, axis + "axis")).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = self.packed_data_items[0].name()
                        setattr(self, axislabel, name + " " + format_units(units))
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                        setattr(self, axislabel, units)

    def create_legend(self):
        legend_titles = []
        datagroups = self.datagroups
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and "label" in datagroups[i]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = self.matplotlib.legend(self.color_axis, legend_titles, loc="best", scatterpoints=1)
        legend.draggable(state=True)
