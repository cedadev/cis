from generic_plot import Generic_Plot

class Contour_Plot(Generic_Plot):
    #'contour' : PlotType(1, 2, plot_contour),
    def plot(self):
        '''
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        my_contour = self.plot_method.contour(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], *self.mplargs, **self.mplkwargs)
        lim_dict = {}
        lim_dict["vmin"] = self.mplkwargs["vmin"]
        lim_dict["vmax"] = self.mplkwargs["vmax"]
        my_contour.set_clim(**lim_dict)
    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_3d_plot()
