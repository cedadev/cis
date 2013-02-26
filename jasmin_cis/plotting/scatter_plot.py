from generic_plot import Generic_Plot

class Scatter_Plot(Generic_Plot):
    #'scatter' : PlotType(None, 2, plot_scatter),
    def plot(self, datafile, vmin, vmax):
        '''
        Plots a scatter plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax
        if datafile["itemstyle"]: self.mplkwargs["marker"] = datafile["itemstyle"]

        colour_scheme = self.mplkwargs.get("color", None)
        if colour_scheme is None:
            if self.unpacked_data_item.get("y", None) is not None: # i.e. the scatter plot is 3D
                colour_scheme = self.unpacked_data_item["data"]
            else:
                colour_scheme = "b" # Default color scheme used by matplotlib

        scatter_size = self.plot_args.get("itemwidth", 1)

        if self.unpacked_data_item.get("y", None) is not None:
            #3D
            self.scatter_type = "3D"
            y_coords = self.unpacked_data_item["y"]
        else:
            #2D
            self.scatter_type = "2D"
            y_coords = self.unpacked_data_item["data"]

        self.mplkwargs.pop("latlon", None)
        self.plot_method.scatter(self.unpacked_data_item["x"], y_coords, c = colour_scheme, s = scatter_size, edgecolors = "none", *self.mplargs, **self.mplkwargs)

    def format_plot(self, i):
        if self.scatter_type == "3D":
            self.format_3d_plot(i)
        elif self.scatter_type == "2D":
            self.format_2d_plot()

    def set_default_axis_label(self, axis):
        from generic_plot import is_map
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        from plot import format_units
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if is_map(self.packed_data_item):
                self.plot_args[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.packed_data_item.coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_item.name()

                try:
                    units = self.packed_data_item.coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_item.units

                if self.number_of_data_items == 1:
                    # only 1 data to plot, display
                    self.plot_args[axislabel] = name + format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = units

    def create_legend(self, datagroups):
        legend_titles = []
        for i, item in enumerate(self.data):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                if " " in item.long_name:
                    legend_titles.append(" ".join(item.long_name.split()[:-1]))
                else:
                    legend_titles.append(item.long_name)
        handles = self.plots
        legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)