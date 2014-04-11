from jasmin_cis.plotting.generic_plot import Generic_Plot

class Heatmap(Generic_Plot):
    def plot(self):
        '''
        Plots a heatmap
        '''
        from jasmin_cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        if len(self.packed_data_items) != 1:
            raise InvalidNumberOfDatagroupsSpecifiedError("Invalid number of datagroups specified. Only one datagroup can be plotted for a heatmap.")

        # Set the options specific to a datagroup with the heatmap type
        self.mplkwargs['cmap'] = self.plot_args['datagroups'][self.datagroup]['cmap']

        if self.plot_args['datagroups'][self.datagroup]['cmin'] is not None:
            self.plot_args["valrange"]["vmin"] = self.plot_args['datagroups'][self.datagroup]['cmin']
        if self.plot_args['datagroups'][self.datagroup]['cmax'] is not None:
            self.plot_args["valrange"]["vmax"] = self.plot_args['datagroups'][self.datagroup]['cmax']

        if self.is_map(): self.mplkwargs["latlon"] = True

        self.plotting_library.pcolormesh(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"], self.unpacked_data_items[0]["data"], *self.mplargs, **self.mplkwargs)

        self.mplkwargs.pop("latlon", None)

    def set_default_axis_label(self, axis):
        return self.set_3daxis_label(axis)

    def create_legend(self):
        pass

    def format_plot(self):
        self.format_time_axis()
        self.format_3d_plot()