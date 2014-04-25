from jasmin_cis.exceptions import InvalidPlotTypeError
from jasmin_cis.plotting.generic_plot import Generic_Plot
from jasmin_cis.plotting.heatmap import Heatmap
from jasmin_cis.plotting.contour_plot import Contour_Plot
from jasmin_cis.plotting.contourf_plot import Contourf_Plot
from jasmin_cis.plotting.scatter_plot import Scatter_Plot
import numpy


class Overlay(Generic_Plot):

    def plot(self):
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
                Heatmap([self.packed_data_items[i]], self.plot_args, wrap=True, *self.mplargs, **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'contour':
                Contour_Plot([self.packed_data_items[i]], self.plot_args, datagroup=i, wrap=True, *self.mplargs,
                             **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'contourf':
                Contourf_Plot([self.packed_data_items[i]], self.plot_args, datagroup=i, wrap=True, *self.mplargs,
                              **self.mplkwargs)
            elif self.plot_args['datagroups'][i]['type'] == 'scatter':
                Scatter_Plot([self.packed_data_items[i]], self.plot_args, wrap=True, *self.mplargs, **self.mplkwargs)
            else:
                raise InvalidPlotTypeError("Invalid or no plot type requested for overlay plot, please choose from "
                                           "heatmap, contour, contourf or scatter, for example: "
                                           "'temperature:my_data.nc:type=contourf'. Requested option was "
                                           "'{}'.".format(self.plot_args['datagroups'][i]['type']))

            if i == 0:
                self.format_time_axis()
                self.format_3d_plot()

    def format_plot(self):
        pass

    def set_default_axis_label(self, axis):
        self.set_3daxis_label(axis)

