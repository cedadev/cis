from generic_plot import Generic_Plot

class Contourf_Plot(Generic_Plot):
    #'contour' : PlotType(1, 2, plot_contour),
    def plot(self):
        '''
        Plots a filled contour plot
        Stores the plot in a list to be used for when adding the legend

        @param data_item:    A dictionary containing the x coords, y coords and data as arrays
        '''
        self.contour_plot(True)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_3d_plot()
