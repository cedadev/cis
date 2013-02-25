import matplotlib.pyplot as plt
#TODO FIX
class Scatter_Overlay(object):
    #'scatteroverlay' : PlotType(None, 2, plot_scatteroverlay)
    def plot(self, data_item):
        '''
        Plots a heatmap overlayed with one or more scatter plots
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        if self.num_of_preexisting_plots == 0:
            self.kwargs.pop("marker", None)
            self.kwargs["label"] = "_nolegend_"
            self.plot_heatmap(data_item)
            self.kwargs.pop("label")
            # Heatmap overlay self.__add_color_bar()
        else:
            self.plot_scatter(data_item)
        self.num_of_preexisting_plots += 1

    def set_axis_label(self, axis, options):
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if options[axislabel] is None:
            if self.__is_map():
                options[axislabel] = "Longitude" if axis == "x" else "Latitude"
            else:
                try:
                    name = self.data[0].coord(axis=axis).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.data[0].name()

                try:
                    units = self.data[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.data[0].units

                # in general, display both name and units in brackets
                options[axislabel] = name + self.__format_units(units)

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
        handles = self.plots[1:]
        legend_titles = legend_titles[1:]
        legend = plt.legend(handles, legend_titles, loc="best", scatterpoints = 1, markerscale = 0.5)
        legend.draggable(state = True)

    def add_color_bar(self):
        # nformat = "%e"
        # nformat = "%.3f"
        # nformat = "%.3e"
        nformat = "%.3g"

        if not self.logv:
            try:
                step = self.v_range.get("vstep", (self.kwargs["vmax"]-self.kwargs["vmin"]) / 5)
            except AttributeError:
                step = (self.kwargs["vmax"]-self.kwargs["vmin"]) / 5
            ticks = []
            tick = self.kwargs["vmin"]
            while tick <= self.kwargs["vmax"]:
                ticks.append(tick)
                tick = tick + step
        else:
            ticks = None

        cbar = plt.colorbar(orientation = self.colour_bar_orientation, ticks = ticks, format = nformat)

        cbar.set_label(self.__format_units(self.data[0].units))
