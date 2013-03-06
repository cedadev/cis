from jasmin_cis.plotting.generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    def plot(self):
        '''
        Plots a heatmap
        '''
        x_coords = self.unpacked_data_items[0]["x"]

        self.plot_method.pcolormesh(x_coords, self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], *self.mplargs, **self.mplkwargs)


    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_time_axis()
        self.format_3d_plot()