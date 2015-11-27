from cis.exceptions import InvalidPlotTypeError
from cis.plotting.generic_plot import Generic_Plot
from cis.plotting.heatmap import Heatmap
from cis.plotting.contour_plot import Contour_Plot
from cis.plotting.contourf_plot import Contourf_Plot
from cis.plotting.scatter_plot import Scatter_Plot

import numpy


class Overlay(Generic_Plot):

    def get_data_items_max(self):
        return self.unpacked_data_items[0]['x'].max()

    def calculate_min_and_max_values(self):
        pass

    def plot(self):
        x_wrap_start = None
        for i in numpy.arange(0, len(self.plot_args['datagroups'])):

            if self.plot_args['datagroups'][i]['color'] is None and self.plot_args['datagroups'][i]['cmap'] is None \
               and self.plot_args['datagroups'][i]['type'] == 'contour':
                self.plot_args['datagroups'][i]['color'] = "black"

            if self.plot_args['datagroups'][i]['contlabel'] is None:
                # Default to contour labels on if not filled, off if filled
                self.plot_args['datagroups'][i]['contlabel'] = \
                    self.plot_args['datagroups'][i]['type'] == 'contour'

            if self.plot_args['datagroups'][i]['transparency'] is not None:
                self.mplkwargs['alpha'] = 1.0 - self.plot_args['datagroups'][i]['transparency']  # change to an opacity

            if self.plot_args['datagroups'][i]['type'] == 'heatmap':
                p = Heatmap([self.packed_data_items[i]], self.plot_args, x_wrap_start, *self.mplargs, **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'contour':
                p = Contour_Plot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                 **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'contourf':
                p = Contourf_Plot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                  **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'scatter':
                p = Scatter_Plot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                 **self.mplkwargs)
            else:
                raise InvalidPlotTypeError("Invalid or no plot type requested for overlay plot, please choose from "
                                           "heatmap, contour, contourf or scatter, for example: "
                                           "'temperature:my_data.nc:type=contourf'. Requested option was "
                                           "'{}'.".format(self.plot_args['datagroups'][i]['type']))

            self.color_axis.append(p.color_axis)

            if i == 0:
                self.format_time_axis()
                self.format_3d_plot()

    def format_plot(self):
        pass

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)

    def add_color_bar(self):
        """
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        """
        from cis.plotting.formatter import LogFormatterMathtextSpecial

        step = self.plot_args["valrange"].get("vstep", None)
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)

        if self.plot_args.get("logv", False):
            formatter = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
        else:
            formatter = None
        #
        scale = self.plot_args["cbarscale"]
        if scale is None:
            orientation = self.plot_args.get("cbarorient", "vertical")
            default_scales = {"horizontal": 1.0, "vertical": 0.55}
            scale = default_scales.get(orientation, 1.0)
        else:
            scale = float(scale)

        for i, color_axis in enumerate(self.color_axis):
            cbar = self.matplotlib.colorbar(color_axis, orientation=self.plot_args["cbarorient"], ticks=ticks,
                                            shrink=scale, format=formatter)

            if not self.plot_args["logv"]:
                cbar.formatter.set_scientific(True)
                cbar.formatter.set_powerlimits((-3, 3))
                cbar.update_ticks()

            label = self.packed_data_items[i].long_name

            cbar.set_label(label)
