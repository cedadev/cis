from generic_plot import Generic_Plot

class Contour_Plot(Generic_Plot):
    #'contour' : PlotType(1, 2, plot_contour),
    def plot(self, datafile):
        '''
        Plots a contour plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.plot_method.contour(self.unpacked_data_item["x"], self.unpacked_data_item["y"], self.unpacked_data_item["data"], *self.args, **self.kwargs)

    def set_axis_label(self, axis, options):
        return self.set_3daxis_label(axis, options)

    def format_plot(self, options):
        self.format_3d_plot(options)
