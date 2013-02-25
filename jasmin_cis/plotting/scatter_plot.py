from generic_plot import Generic_Plot

class Scatter_Plot(Generic_Plot):
    #'scatter' : PlotType(None, 2, plot_scatter),
    def plot(self, datafile, *args, **kwargs):
        '''
        Plots a scatter plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        if datafile["itemstyle"]:
            kwargs["marker"] = datafile["itemstyle"]
        if datafile["color"]:
            kwargs["color"] = datafile["color"]

        colour_scheme = kwargs.get("color", None)
        mark = kwargs.pop("marker", "o")
        if colour_scheme is None:
            if self.unpacked_data_item.get("y", None) is not None: # i.e. the scatter plot is 3D
                colour_scheme = self.unpacked_data_item["data"]
            else:
                colour_scheme = "b" # Default color scheme used by matplotlib

        scatter_size = kwargs.get("linewidth", 1)

        if self.unpacked_data_item.get("y", None) is not None:
            #3D
            self.scatter_type = "3D"
            y_coords = self.unpacked_data_item["y"]
        else:
            #2D
            self.scatter_type = "2D"
            y_coords = self.unpacked_data_item["data"]

        self.plot_method.scatter(self.unpacked_data_item["x"], y_coords, c = colour_scheme, marker = mark, s = scatter_size, edgecolors = "none", *args, **kwargs)

    def format_plot(self, options):
        if self.scatter_type == "3D":
            self.format_3d_plot(options)
        elif self.scatter_type == "2D":
            self.format_2d_plot(options)

    def set_axis_label(self, axis, options):
        from generic_plot import is_map
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if is_map(self.packed_data_item):
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
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
                    options[axislabel] = name + self.__format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    options[axislabel] = units

        return options

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