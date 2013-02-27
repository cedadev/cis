from generic_plot import Generic_Plot

class Contour_Plot(Generic_Plot):
    #'contour' : PlotType(1, 2, plot_contour),
    def plot(self):
        '''
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        from numpy import linspace
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.v_range.get("vstep", None) is None:
            step = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        else:
            step = (vmax - vmin) / self.v_range["vstep"]
        self.plot_method.contour(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], linspace(vmin, vmax, step), *self.mplargs, **self.mplkwargs)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax
    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_3d_plot()
