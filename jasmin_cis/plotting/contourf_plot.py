import matplotlib.pyplot as plt

class Contourf_Plot(object):
    #'contourf' : PlotType(1, 2, plot_contourf),
    def plot(self, data_item):
        '''
        Plots a filled contour
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.plots.append(self.__get_plot_method().contourf(data_item["x"], data_item["y"], data_item["data"], *self.args, **self.kwargs))
        self.kwargs.pop("latlon", None)

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

    def create_legend(self, datafiles):
        pass

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