from generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    #'heatmap' : PlotType(1, 2, plot_heatmap),
    def plot(self):
        '''
        Plots a heatmap
        Stores the min and max values of the data to be used later on for setting the colour scheme of scatter plots
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.plot_method.pcolormesh(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], *self.mplargs, **self.mplkwargs)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_3d_plot()