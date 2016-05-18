import logging

import numpy as np
from .APlot import APlot
from cis.exceptions import CISError
from .formatter import LogFormatterMathtextSpecial

# TODO: Carry on splitting out the 2d and 3d plot methods. Make the relavant plots subclass the right one. Pull out any
# obviously static methods. and split files. This should make the classes more manageable and easier to test.


class GenericPlot(APlot):

    def format_plot(self):
        """
        Used by 2d subclasses to format the plot
        """
        import logging
        from cis.plotting.plot import plot_options

        logx = self.logx
        logy = self.logy
        if logx or logy:
            self.set_log_scale(logx, logy)
        else:
            try:
                self.matplotlib.gca().ticklabel_format(style='sci', scilimits=(-3, 3), axis='both')
            except AttributeError:
                logging.warning("Couldn't apply scientific notation to axes")

        if self.grid:
            self.matplotlib.grid(True, which="both")

        self.set_axes_ticks(2)

        self.set_font_size()

        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        for key in list(plot_options.keys()):
            # Call the method associated with the option
            if key in list(self.plot_args.keys()) and self.plot_args[key] is not None:
                plot_options[key](self.plot_args[key])

        if len(self.packed_data_items) > 1:
            self.create_legend()


class Generic2DPlot(APlot):

    DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS = 5

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, ax=None, calculate_min_and_max_values=True, datagroup=0, datagroups=None,
                 nocolourbar=False, logx=False, logy=False, logv=False, xmin=None, xmax=None, xstep=None, ymin=None,
                 ymax=None, ystep=None, vmin=None, vmax=None, vstep=None, cbarorient='horizontal', grid=False,
                 xlabel=None, ylabel=None, cbarlabel=None, title=None, fontsize=None, itemwidth=1, xtickangle=None,
                 ytickangle=None, coastlinecolour='k', nasabluemarble=False, xaxis=None, yaxis=None, cbarscale=None,
                 *mplargs, **mplkwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param calculate_min_and_max_values: If true calculates min and max for the data values
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """
        super().__init__(packed_data_items, ax, datagroup, datagroups, logx, logy, xmin,
                         xmax, xstep, ymin, ymax, ystep, grid, xlabel, ylabel, title, fontsize, itemwidth, xtickangle,
                         ytickangle, xaxis, yaxis, *mplargs, **mplkwargs)
        import matplotlib.pyplot as plt

        self.packed_data_items = packed_data_items

        if ax is None:
            _, self.ax = plt.subplots()
        else:
            self.ax = ax

        self.datagroup = datagroup
        self.datagroups = datagroups
        self.nocolourbar = nocolourbar
        self.logx = logx
        self.logy = logy
        self.logv = logv
        self.xmin = xmin
        self.xmax = xmax
        self.xstep = xstep
        self.ymin = ymin
        self.ymax = ymax
        self.ystep = ystep
        self.vmin = vmin
        self.vmax = vmax
        self.vstep = vstep
        self.cbarorient = cbarorient
        self.grid = grid
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.cbarlabel = cbarlabel
        self.title = title
        self.fontsize = fontsize
        self.itemwidth = itemwidth
        self.xtickangle = xtickangle
        self.ytickangle = ytickangle
        self.coastlinecolour = coastlinecolour
        self.nasabluemarble = nasabluemarble
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.cbarscale = cbarscale

        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        self.color_axis = []

        if logv:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        self.assign_variables_to_x_and_y_axis()

        logging.debug("Unpacking the data items")
        self.set_x_wrap_start(xmin)
        self.offset_longitude = xmin != self.x_wrap_start
        self.unpacked_data_items = self.unpack_data_items()

        if calculate_min_and_max_values:
            self.calculate_min_and_max_values()

        if self.is_map():
            self.setup_map()
            self.check_data_is_2d()

        self.plot()

    def setup_map(self):
        import cartopy.crs as ccrs

        # The projection of the data gets offset
        self.projection = ccrs.PlateCarree(central_longitude=(self.x_wrap_start + 180.0))
        # But not the transform...
        self.transform = ccrs.PlateCarree()
        self.cartopy_axis = self._replace_axes_with_cartopy_axes(self.ax, self.projection)
        self.mplkwargs['transform'] = self.transform

    @staticmethod
    def _replace_axes_with_cartopy_axes(ax, projection):
        from cartopy.mpl.geoaxes import GeoAxes
        from matplotlib.axes import SubplotBase
        if not isinstance(ax, GeoAxes):
            fig = ax.get_figure()
            if isinstance(ax, SubplotBase):
                new_ax = fig.add_subplot(ax.get_subplotspec(),
                                         projection=projection,
                                         title=ax.get_title(),
                                         xlabel=ax.get_xlabel(),
                                         ylabel=ax.get_ylabel())
            else:
                new_ax = fig.add_axes(projection=projection,
                                      title=ax.get_title(),
                                      xlabel=ax.get_xlabel(),
                                      ylabel=ax.get_ylabel())

            # delete the axes which didn't have a cartopy projection
            fig.delaxes(ax)
        else:
            new_ax = ax
        return new_ax

    def _get_extent(self):
        """
         Calculates the diagonal extent of plot area in Km
        :return: The diagonal size of the plot in Km
        """
        from cis.utils import haversine
        x0, x1, y0, y1 = self.cartopy_axis.get_extent()
        return haversine(y0, x0, y1, x1)

    def _test_natural_earth_available(self):
        """
        Test whether we can download the natural earth cartographies.
        :return: Can we access natural earth?
        """
        from cartopy.io.shapereader import natural_earth
        from urllib.error import HTTPError
        try:
            natural_earth_available = natural_earth()
        except HTTPError:
            natural_earth_available = False
        return natural_earth_available

    def drawcoastlines(self):
        """
        Adds coastlines or nasa blue marble back ground to a plot (no coastlines are plotted over nasa blue marble).
        There are three levels of resolution used based on the spatial scale of the plot. These are determined using
        values determined by eye for bluemarble and the coastlines independently.
        """
        from matplotlib.image import imread
        import os.path as path
        bluemarble_scales = [(0, 'raster/world.topo.bathy.200407.3x1350x675.png'),
                             (5000, 'raster/world.topo.bathy.200407.3x2700x1350.png'),
                             (2500, 'raster/world.topo.bathy.200407.3x5400x2700.png')]

        coastline_scales = [(0, '110m'), (500, '50m'), (100, '10m')]

        ext = self._get_extent()

        if self.nasabluemarble is not False:
            bluemarble_res = bluemarble_scales[0][1]
            for scale, res in bluemarble_scales[1:]:
                if scale > ext:
                    bluemarble_res = res

            img = imread(path.join(path.dirname(path.realpath(__file__)), bluemarble_res))
            self.cartopy_axis.imshow(img, origin='upper', transform=self.transform, extent=[-180, 180, -90, 90])
        else:
            if self._test_natural_earth_available():
                coastline_res = coastline_scales[0][1]
                for scale, res in coastline_scales[1:]:
                    if scale > ext:
                        coastline_res = res

                self.cartopy_axis.coastlines(color=self.coastlinecolour, resolution=coastline_res)
            else:
                logging.warning('Unable to access the natural earth topographies required for plotting coastlines. '
                                'Check internet connectivity and try again')

    def format_plot(self):
        """
        Used by 3d subclasses to format the plot
        """
        from cis.plotting.plot import plot_options
        import cis.plotting.overlay

        self.format_time_axis()

        logx = self.logx
        logy = self.logy
        if logx or logy:
            self.set_log_scale(logx, logy)

        if self.grid:
            self.matplotlib.grid(True, which="both")

        if self.is_map():
            self.drawcoastlines()

        self.set_axes_ticks(3)

        self.set_font_size()
        # If any of the options have not been specified, then use the defaults
        self.set_default_axis_label("X")
        self.set_default_axis_label("Y")

        if self.xlabel is None:
            self.xlabel = ""
        if self.ylabel is None:
            self.ylabel = ""
        if self.title is None:
            self.title = self.packed_data_items[0].long_name

        for key in list(plot_options.keys()):
            # Call the method associated with the option
            if key in list(self.plot_args.keys()):
                plot_options[key](self.plot_args[key])

        if not self.nocolourbar:
            self.add_color_bar()

        if len(self.packed_data_items) > 1 and not isinstance(self, cis.plotting.overlay.Overlay):
            self.create_legend()

    def set_default_axis_label(self, axis):
        """
        Used by 3d plots to calculate the default axis label.
        Uses Latitude or Longitude if a map is being plotted
        :param axis: The axis to calculate the default label for
        """
        import cis.exceptions as cisex
        import iris.exceptions as irisex
        from .APlot import format_units
        axis = axis.lower()
        axislabel = axis + "label"

        if getattr(self, axislabel) is None:
            if self.is_map():
                setattr(self, axislabel, "Longitude" if axis == "x" else "Latitude")
            else:
                try:
                    name = self.packed_data_items[0].coord(getattr(self, axis + 'axis')).name()
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    name = self.packed_data_items[0].name()

                try:
                    units = self.packed_data_items[0].coord(getattr(self, axis + 'axis')).units
                except (cisex.CoordinateNotFoundError, irisex.CoordinateNotFoundError):
                    units = self.packed_data_items[0].units

                # in general, display both name and units in brackets
                setattr(self, axislabel, name + " " + format_units(units))

    def contour_plot(self, filled):
        """
        Used by both contour and contourf to plot a contour plot
        :param filled: A boolean specifying whether or not the contour plot should be filled
        """

        # Set the options specific to a datagroup with the contour type
        self.mplkwargs['cmap'] = self.datagroups[self.datagroup]['cmap']
        self.mplkwargs["contlabel"] = self.datagroups[self.datagroup]['contlabel']
        self.mplkwargs["cfontsize"] = self.datagroups[self.datagroup]['contfontsize']
        self.mplkwargs["colors"] = self.datagroups[self.datagroup]['color']

        self.mplkwargs["linewidths"] = self.datagroups[self.datagroup]['contwidth']
        if self.datagroups[self.datagroup]['cmin'] is not None:
            self.vmin = self.datagroups[self.datagroup]['cmin']
        if self.datagroups[self.datagroup]['cmax'] is not None:
            self.vmax = self.datagroups[self.datagroup]['cmax']

        self.calculate_min_and_max_values()

        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        if self.vstep is None and \
                        self.datagroups[self.datagroup]['contnlevels'] is None:
            nconts = self.DEFAULT_NUMBER_OF_COLOUR_BAR_STEPS + 1
        elif self.vstep is None:
            nconts = self.datagroups[self.datagroup]['contnlevels']
        else:
            nconts = (vmax - vmin) / self.vstep

        if self.datagroups[self.datagroup]['contlevels'] is None:
            if self.logv is None:
                contour_level_list = np.linspace(vmin, vmax, nconts)
            else:
                contour_level_list = np.logspace(np.log10(vmin), np.log10(vmax), nconts)
        else:
            contour_level_list = self.datagroups[self.datagroup]['contlevels']

        if filled:
            contour_type = self.matplotlib.contourf
        else:
            contour_type = self.matplotlib.contour

        if self.is_map() and self.unpacked_data_items[0]["data"].ndim == 2:
            # This fails for an unknown reason on one dimensional data
            self.mplkwargs["latlon"] = True

        self.color_axis.append(contour_type(self.unpacked_data_items[0]["x"], self.unpacked_data_items[0]["y"],
                                       self.unpacked_data_items[0]["data"], contour_level_list, *self.mplargs, **self.mplkwargs))
        if self.mplkwargs["contlabel"] and not filled:
            self.matplotlib.clabel(self.color_axis[0], fontsize=self.mplkwargs["cfontsize"], inline=1, fmt='%.3g')
        elif self.mplkwargs["contlabel"] and filled:
            self.matplotlib.clabel(self.color_axis[0], fontsize=self.mplkwargs["cfontsize"], inline=0, fmt='%.3g')

        self.mplkwargs.pop("latlon", None)
        self.mplkwargs.pop("tri", None)

        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def calculate_min_and_max_values(self):
        """
        Calculates the min and max values of all the data given
        Stores the values in the matplotlib keyword args to be directly passed into the plot methods.
        """
        vmin = self.vmin
        vmax = self.vmax

        if vmin is None:
            if self.logv:
                vmin = min(d["data"][d["data"] > 0].min() for d in self.unpacked_data_items)
            else:
                vmin = min(d["data"].min() for d in self.unpacked_data_items)
        if vmax is None:
            if self.logv:
                vmax = max(d["data"][d["data"] > 0].max() for d in self.unpacked_data_items)
            else:
                vmax = max(d["data"].max() for d in self.unpacked_data_items)

        # TODO: This should really just return the values, and let the calling function put them where they want.
        self.mplkwargs["vmin"] = float(vmin)
        self.mplkwargs["vmax"] = float(vmax)

    def add_color_bar(self):
        """
        Adds a colour bar to a plot
        Allows specifying of tick spacing and orientation
        """
        from .APlot import format_units

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

        cbar = self.matplotlib.colorbar(self.color_axis[0], orientation=orientation, ticks=ticks,
                                        shrink=scale, format=formatter)

        if not self.logv:
            cbar.formatter.set_scientific(True)
            cbar.formatter.set_powerlimits((-3, 3))
            cbar.update_ticks()

        if self.cbarlabel is None:
            label = format_units(self.packed_data_items[0].units)
        else:
            label = self.cbarlabel

        cbar.set_label(label)

    def check_data_is_2d(self):
        if len(self.packed_data_items[0].shape) > 2:
            raise CISError("Data is not 1D or 2D - can't plot it on a map.")

