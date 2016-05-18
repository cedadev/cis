import logging

import numpy as np
from .APlot import APlot
from cis.exceptions import CISError
from .formatter import LogFormatterMathtextSpecial

# TODO: Carry on splitting out the 2d and 3d plot methods. Make the relavant plots subclass the right one. Pull out any
# obviously static methods. and split files. This should make the classes more manageable and easier to test.


class GenericPlot(APlot):

    def __init__(self, packed_data_items, *mplargs, **mplkwargs):
        super().__init__(packed_data_items, *mplargs, **mplkwargs)

        logging.debug("Unpacking the data items")
        # TODO: Drop one of self.unpacked_data_items or self.packed_data_items
        # If I drop the unpacked then I'll need to store the x and y coords somewhere and worry about the cube transforms,
        #  if I drop the packed items then I'll need to store the metadata somewhere (units, axis labels etc).
        self.unpacked_data_items = self.unpack_data_items()

        self.plot()

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
    def __init__(self, packed_data_items, ax=None, logv=False, vmin=None, vmax=None, vstep=None,
                 transparency=None, cmap=None, cmin=None, cmax=None, x_wrap_start=None, *args, **kwargs):
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
        super().__init__(packed_data_items, ax, *args, **kwargs)

        self.logv = logv
        self.vmin = vmin
        self.vmax = vmax
        self.vstep = vstep

        self.cmin = cmin
        self.cmax = cmax
        self.cmap = cmap
        self.transparency = transparency

        if self.logv:
            from matplotlib.colors import LogNorm
            self.mplkwargs["norm"] = LogNorm()

        self.assign_variables_to_x_and_y_axis()

        logging.debug("Unpacking the data items")
        self.x_wrap_start = x_wrap_start
        self.unpacked_data_items = self.unpack_data_items()

        self.mplkwargs["vmin"], self.mplkwargs["vmax"] = self.calculate_min_and_max_values()

        self.plot()


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

    def calculate_min_and_max_values(self):
        """
        Calculates the min and max values of all the data given
        Stores the values in the matplotlib keyword args to be directly passed into the plot methods.
        """
        from .APlot import calc_min_and_max_vals_of_array_incl_log

        data_min, data_max = calc_min_and_max_vals_of_array_incl_log(self.data)

        vmin = self.vmin if self.vmin is not None else data_min
        vmax = self.vmax if self.vmax is not None else data_max

        return vmin, vmax

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

