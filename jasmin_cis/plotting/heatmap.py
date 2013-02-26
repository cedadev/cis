from generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    #'heatmap' : PlotType(1, 2, plot_heatmap),
    def plot(self, data_file, vmin, vmax):
        '''
        Plots a heatmap
        Stores the min and max values of the data to be used later on for setting the colour scheme of scatter plots
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax
        self.plot_method.pcolormesh(self.unpacked_data_item["x"], self.unpacked_data_item["y"], self.unpacked_data_item["data"], *self.mplargs, **self.mplkwargs)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self, i):
        self.format_3d_plot(i)