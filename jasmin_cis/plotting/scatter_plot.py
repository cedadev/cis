from generic_plot import Generic_Plot

class Scatter_Plot(Generic_Plot):
    def plot(self):
        '''
        Plots one or many scatter plots
        Stores the plot in a list to be used for when adding the legend
        '''
        self.plots = []
        scatter_size = self.plot_args.get("itemwidth", 1) if self.plot_args.get("itemwidth", 1) is not None else 1
        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.plot_args["datagroups"][i]
            if datafile["itemstyle"]:
                self.mplkwargs["marker"] = datafile["itemstyle"]
            else:
                self.mplkwargs["marker"] = 'o'

            colour_scheme = self.mplkwargs.get("color", None)
            if colour_scheme is None:
                if unpacked_data_item.get("y", None) is not None: # i.e. the scatter plot is 3D
                    colour_scheme = unpacked_data_item["data"]
                else:
                    colour_scheme = "b" # Default color scheme used by matplotlib

            if unpacked_data_item.get("y", None) is not None:
                #3D
                self.scatter_type = "3D"
                y_coords = unpacked_data_item["y"]

                from datetime import datetime
                from jasmin_cis.time_util import convert_datetime_to_num_array
                if isinstance(self.unpacked_data_items[0]["x"].flatten()[0], datetime):
                    self.unpacked_data_items[0]["x"] = convert_datetime_to_num_array(self.unpacked_data_items[0]["x"])
            else:
                #2D
                self.scatter_type = "2D"
                y_coords = unpacked_data_item["data"]

            self.mplkwargs.pop("latlon", None)
            self.plots.append(self.plot_method.scatter(unpacked_data_item["x"], y_coords, c = colour_scheme, s = scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs))

            if self.scatter_type == "3D" and isinstance(self.unpacked_data_items[0]["x"].flatten()[0], datetime):
                self.set_x_axis_as_time()

    def calculate_axis_limits(self, axis):
        valrange = {}
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            if self.scatter_type == "2D":
                coord_axis = "data"
            elif self.scatter_type == "3D":
                coord_axis = "y"
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][coord_axis])
        return valrange

    def format_plot(self):
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
                    units = self.packed_data_items[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                if len(self.packed_data_items) == 1:
                    # only 1 data to plot, display
                    try:
                        name = self.packed_data_items[0].coord(axis=axis).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = self.packed_data_items[0].name()
                    self.plot_args[axislabel] = name + self.format_units(units)
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
                if " " in item.long_name:
                    legend_titles.append(" ".join(item.long_name.split()[:-1]))
                else:
                    legend_titles.append(item.long_name)
        handles = self.plots
        legend = self.matplotlib.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)