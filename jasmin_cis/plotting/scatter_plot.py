from jasmin_cis.plotting.generic_plot import Generic_Plot

class Scatter_Plot(Generic_Plot):

    def plot(self):
        '''
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        '''
        self.plots = []
        scatter_size = self.plot_args.get("itemwidth", 1) if self.plot_args.get("itemwidth", 1) is not None else 1
        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.plot_args["datagroups"][self.datagroup]
            if datafile["itemstyle"]:
                self.mplkwargs["marker"] = datafile["itemstyle"]
            else:
                self.mplkwargs.pop("marker", None)

            self.mplkwargs["cmap"] = datafile["cmap"]

            self.mplkwargs["c"] = datafile.get("color", None)
            if self.mplkwargs["c"] is None:
                if unpacked_data_item.get("y", None) is not None: # i.e. the scatter plot is 3D
                    self.mplkwargs["c"] = unpacked_data_item["data"]
                else:
                    self.mplkwargs.pop("c", None)

            if datafile["edgecolor"]:
                edge_color = datafile["edgecolor"]
            else:
                edge_color = "None"

            x_coords = unpacked_data_item["x"]

            if unpacked_data_item.get("y", None) is not None:
                #3D
                self.scatter_type = "3D"
                y_coords = unpacked_data_item["y"]
            else:
                #2D
                self.scatter_type = "2D"
                y_coords = unpacked_data_item["data"]


            self.plots.append(self.plotting_library.scatter(x_coords, y_coords, s = scatter_size, edgecolors = edge_color, *self.mplargs, **self.mplkwargs))

    def calculate_axis_limits(self, axis, min_val, max_val, step):
        '''
        :param axis: The axis to calculate the limits for
        :param min_val: The user specified minimum value for the axis
        :param max_val: The user specified maximum value for the axis
        :param step: The distance between each tick on the axis
        :return: A dictionary containing the min and max values for the axis, and the step between each tick
        '''
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            if self.scatter_type == "2D":
                coord_axis = "data"
            elif self.scatter_type == "3D":
                coord_axis = "y"
        calculated_min, calculated_max = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][coord_axis])

        valrange = {}
        valrange[axis + "min"] = calculated_min if min_val is None else min_val
        valrange[axis + "max"] = calculated_max if max_val is None else max_val
        valrange[axis + "step"] = step

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.plot_args["y_variable"] == "air_pressure" and min_val is None and max_val is None:
            valrange[axis + "min"], valrange[axis + "max"] = valrange[axis + "max"], valrange[axis + "min"]

        return valrange

    def format_plot(self):
        self.format_time_axis()
        if self.scatter_type == "3D":
            self.format_3d_plot()
        elif self.scatter_type == "2D":
            self.format_2d_plot()

    def set_default_axis_label(self, axis):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if self.is_map():
                self.plot_args[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    units = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                if len(self.packed_data_items) == 1:
                    # only 1 data to plot, display
                    try:
                        name = self.packed_data_items[0].coord(name=self.plot_args[axis + "_variable"]).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = self.packed_data_items[0].name()
                    self.plot_args[axislabel] = name + " " + self.format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = units

    def create_legend(self):
        legend_titles = []
        datagroups = self.plot_args["datagroups"]
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        handles = self.plots
        legend = self.matplotlib.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)