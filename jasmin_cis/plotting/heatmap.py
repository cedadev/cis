from generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    #'heatmap' : PlotType(1, 2, plot_heatmap),
    def plot(self, data_file):
        '''
        Plots a heatmap
        Stores the min and max values of the data to be used later on for setting the colour scheme of scatter plots
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.plot_method.pcolormesh(self.unpacked_data_item["x"], self.unpacked_data_item["y"], self.unpacked_data_item["data"], *self.mplargs, **self.mplkwargs)

    def set_axis_label(self, axis, options):
        return self.set_3daxis_label(axis, options)

    def format_plot(self, options):
        self.format_3d_plot(options)