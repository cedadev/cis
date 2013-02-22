import matplotlib.pyplot as plt

class Scatter_Plot(object):
    #'scatter' : PlotType(None, 2, plot_scatter),
    def plot(self, data_item, datafile, *args, **kwargs):
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
            if data_item.get("y", None) is not None: # i.e. the scatter plot is 3D
                colour_scheme = data_item["data"]
            else:
                colour_scheme = "b" # Default color scheme used by matplotlib

        scatter_size = kwargs.get("linewidth", 1)

        #plot_method = self.__get_plot_method()
        from mpl_toolkits.basemap import Basemap
        basemap = Basemap()
        plot_method = basemap
        kwargs["latlon"] = True

        kwargs.pop("latlon", None)

        if data_item.get("y", None) is not None:
            return plot_method.scatter(data_item["x"], data_item["y"], c = colour_scheme, marker = mark, s = scatter_size, edgecolors = "none", *args, **kwargs)
        else:
            #self.plot_type = "scatter2D"
            return plot_method.scatter(data_item["x"], data_item["data"], c = colour_scheme, marker = mark, s = scatter_size, edgecolors = "none", *args, **kwargs)

    def set_axis_label(self, axis, options, data):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            #if self.__is_map():
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
                '''
                else:
                    try:
                        name = data[0].coord(axis=axis).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = data[0].name()

                    try:
                        units = data[0].coord(axis=axis).units
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        units = data[0].units

                    if len(data) == 1:
                        # only 1 data to plot, display
                        options[axislabel] = name + self.__format_units(units)
                    else:
                        # if more than 1 data, legend will tell us what the name is. so just displaying units
                        options[axislabel] = units
                        '''

        return options

    def create_legend(self, datafiles):
        legend_titles = []
        for i, item in enumerate(self.data):
            if datafiles is not None and datafiles[i]["label"]:
                legend_titles.append(datafiles[i]["label"])
            else:
                if " " in item.long_name:
                    legend_titles.append(" ".join(item.long_name.split()[:-1]))
                else:
                    legend_titles.append(item.long_name)
        handles = self.plots
        legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)

    def add_color_bar(self, logv, vmin, vmax, v_range, colour_bar_orientation, units):
        from plot import format_units
        # nformat = "%e"
        # nformat = "%.3f"
        # nformat = "%.3e"
        nformat = "%.3g"

        if not logv:
            try:
                step = v_range.get("vstep", (vmax-vmin) / 5)
            except AttributeError:
                step = (vmax-vmin) / 5
            ticks = []
            tick = vmin
            while tick <= vmax:
                ticks.append(tick)
                tick = tick + step
        else:
            ticks = None

        cbar = plt.colorbar(orientation = colour_bar_orientation, ticks = ticks, format = nformat)

        cbar.set_label(format_units(units))