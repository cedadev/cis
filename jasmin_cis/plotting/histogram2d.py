from generic_plot import Generic_Plot

class Histogram_2D(Generic_Plot):
    def plot(self):
        '''
        color
        range x moreso than y
        two variables
        get rid of bar lines and not filled in
        @return:
        '''
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")
        for unpacked_data_item in self.unpacked_data_items:
            self.matplotlib.hist(unpacked_data_item["x"], *self.mplargs, **self.mplkwargs)
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def format_plot(self):
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        from plot import format_units
        import jasmin_cis.exceptions as cisex
        import iris.exceptions as irisex
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if axis == "x":
                try:
                    units = self.packed_data_items[0].coord(axis=axis).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units


                if len(self.packed_data_items) == 1:
                    try:
                        name = self.packed_data_items[0].coord(axis=axis).name()
                    except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                        name = self.packed_data_items[0].name()
                    # only 1 data to plot, display
                    self.plot_args[axislabel] = name + format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = format_units(units)
            elif axis == "y":
                self.plot_args[axislabel] = "Frequency"



    def calculate_axis_limits(self, axis):
        valrange = {}
        if axis == "x":
            coord_axis = "x"
        elif axis == "y":
            coord_axis = "data"
        valrange[axis + "min"], valrange[axis + "max"] = self.calculate_min_and_max_values_of_array_including_case_of_log(axis, self.unpacked_data_items[0][coord_axis])
        return valrange

    def apply_axis_limits(self, valrange, axis):
        pass

