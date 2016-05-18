from cis.exceptions import InvalidPlotTypeError
from cis.plotting.genericplot import GenericPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.contourplot import ContourPlot, ContourfPlot
from cis.plotting.scatterplot import ScatterPlot

import numpy


# TODO: This shouldn't be a generic plot - it needs to be a static method in plot.Plot and should probably work for 2D
# as well as 3D plots.
class Overlay(GenericPlot):

    def get_data_items_max(self):
        return self.unpacked_data_items[0]['x'].max()

    def calculate_min_and_max_values(self):
        pass

    def plot(self):
        x_wrap_start = None
        for i in numpy.arange(0, len(self.datagroups)):

            if self.datagroups[i]['color'] is None and self.datagroups[i]['cmap'] is None \
               and self.datagroups[i]['type'] == 'contour':
                self.datagroups[i]['color'] = "black"

            if self.datagroups[i]['contlabel'] is None:
                # Default to contour labels on if not filled, off if filled
                self.datagroups[i]['contlabel'] = \
                    self.datagroups[i]['type'] == 'contour'

            if self.datagroups[i]['transparency'] is not None:
                self.mplkwargs['alpha'] = 1.0 - self.datagroups[i]['transparency']  # change to an opacity

            if self.datagroups[i]['type'] == 'heatmap':
                p = Heatmap([self.packed_data_items[i]], self.plot_args, x_wrap_start, *self.mplargs, **self.mplkwargs)
            elif self.datagroups[i]['type'] == 'contour':
                p = ContourPlot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                **self.mplkwargs)
            elif self.datagroups[i]['type'] == 'contourf':
                p = ContourfPlot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                 **self.mplkwargs)
            elif self.datagroups[i]['type'] == 'scatter':
                p = ScatterPlot([self.packed_data_items[i]], self.plot_args, x_wrap_start, datagroup=i, *self.mplargs,
                                **self.mplkwargs)
            else:
                raise InvalidPlotTypeError("Invalid or no plot type requested for overlay plot, please choose from "
                                           "heatmap, contour, contourf or scatter, for example: "
                                           "'temperature:my_data.nc:type=contourf'. Requested option was "
                                           "'{}'.".format(self.datagroups[i]['type']))

            self.color_axis.extend(p.color_axis)

            if i == 0:
                self.format_time_axis()
                self.format_3d_plot()

    def format_plot(self):
        self.matplotlib.gcf().delaxes(self.matplotlib.gcf().axes[-1])
        self.add_color_bar()

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)

    def add_color_bar(self):
        """
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        """
        from cis.plotting.formatter import LogFormatterMathtextSpecial

        step = self.vstep
        if step is None:
            ticks = None
        else:
            from matplotlib.ticker import MultipleLocator
            ticks = MultipleLocator(step)

        if self.logv:
            formatter = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
        else:
            formatter = None
        #
        scale = self.cbarscale
        orientation = self.cbarorient
        if scale is None:
            default_scales = {"horizontal": 1.0, "vertical": 0.55}
            scale = default_scales.get(orientation, 1.0)
        else:
            scale = float(scale)

        for i, color_axis in enumerate(self.color_axis):
            cbar = self.matplotlib.colorbar(color_axis, orientation=orientation, ticks=ticks,
                                            shrink=scale, format=formatter)

            if not self.logv:
                cbar.formatter.set_scientific(True)
                cbar.formatter.set_powerlimits((-3, 3))
                cbar.update_ticks()

            label = self.packed_data_items[i].long_name

            cbar.set_label(label)
