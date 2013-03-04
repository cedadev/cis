from jasmin_cis.plotting.generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    def plot(self):
        '''
        Plots a heatmap
        '''
        from datetime import datetime
        from jasmin_cis.time_util import convert_datetime_to_num_array
        if isinstance(self.unpacked_data_items[0]["x"].flatten()[0], datetime):
            self.unpacked_data_items[0]["x"] = convert_datetime_to_num_array(self.unpacked_data_items[0]["x"])

        self.plot_method.pcolormesh(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], *self.mplargs, **self.mplkwargs)

        if isinstance(self.unpacked_data_items[0]["x"].flatten()[0], datetime): self.set_x_axis_as_time()


    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def format_plot(self):
        self.format_3d_plot()