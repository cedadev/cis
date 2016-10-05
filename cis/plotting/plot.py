"""
Class for plotting graphs.
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
from cis.plotting.contourplot import ContourPlot, ContourfPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.lineplot import LinePlot
from cis.plotting.scatterplot import ScatterPlot
from cis.plotting.comparativescatter import ComparativeScatter
from cis.plotting.overlay import Overlay
from cis.plotting.histogram import Histogram
from cis.plotting.histogram2d import Histogram2D
import logging
from .APlot import format_units
from .genericplot import format_plot

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


def is_map(data, xaxis, yaxis):
    """
    :return: A boolean saying if the first packed data item contains lat and lon coordinates
    """
    from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
    from cis.exceptions import CoordinateNotFoundError as cisNotFoundError
    try:
        x = data.coord(xaxis)
        y = data.coord(yaxis)
    except (cisNotFoundError, irisNotFoundError):
        return False

    if x.name().lower().startswith("lon") and y.name().lower().startswith("lat"):
        return True
    else:
        return False


def name_preferring_standard(coord_item):
    for name in [coord_item.standard_name, coord_item.var_name, coord_item.long_name]:
        if name:
            return name
    return ''


def _try_coord(data, coord_dict):
    import cis.exceptions as cis_ex
    import iris.exceptions as iris_ex
    try:
        coord = data.coord(**coord_dict)
    except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
        coord = None
    return coord


def get_axis(d, axis, name=None):

    coord = _try_coord(d, dict(name_or_coord=name)) or _try_coord(d, dict(standard_name=name)) \
            or _try_coord(d, dict(axis=axis))

    # This is primarily for gridded data, but for Ungridded Data should just pick out the first Coord in the list.
    if coord is None:
        for c in d.coords():
            if axis == 'X':
                if c.shape[0] == d.shape[0]:
                    coord = c
                    break
            elif axis == 'Y' and len(d.shape) > 1:
                if c.shape[1] == d.shape[1]:
                    coord = c
                    break

    logging.info("Plotting " + coord.name() + " on the {} axis".format(axis))

    return coord


def apply_axis_limits(ax, xmin=None, xmax=None, ymin=None, ymax=None, transform=None, projection=None, reverse_y=False):
    """
    Applies the specified limits to the given axis
    """
    from cartopy.mpl.geoaxes import GeoAxes

    # First make sure all of the data fits
    ax.relim()
    ax.autoscale()

    if reverse_y:
        ax.invert_yaxis()

    # Then apply user limits (using different interfaces for different axes types...)
    if isinstance(ax, GeoAxes):
        # We can't optionally pass in certain bounds to set_extent so we need to pull out the existing ones and only
        #  change the ones we've been given.
        x1, x2, y1, y2 = ax.get_extent()
        xmin = xmin or x1
        xmax = xmax or x2
        ymin = ymin or y1
        ymax = ymax or y2
        try:
            #TODO: Not sure if we still need this logic...
            ax.set_extent([xmin, xmax, ymin, ymax], crs=transform)
        except ValueError:
            ax.set_extent([xmin, xmax, ymin, ymax], crs=projection)
    else:
        ax.set_xlim(xmin=xmin, xmax=xmax)
        ax.set_ylim(ymin=ymin, ymax=ymax)


def set_x_axis_as_time(ax):
    from matplotlib import ticker
    from cis.time_util import convert_std_time_to_datetime

    def format_date(x, pos=None):
        return convert_std_time_to_datetime(x).strftime('%Y-%m-%d')

    def format_datetime(x, pos=None):
        # use iosformat rather than strftime as strftime can't handle dates before 1900 - the output is the same
        date_time = convert_std_time_to_datetime(x)
        day_min, day_max = ax.get_xlim()
        day_range = day_max - day_min
        if day_range < 1 and date_time.second == 0:
            return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute
        elif day_range < 1:
            return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute + ':' + "%02d" % date_time.second
        elif day_range > 5:
            return str(date_time.date())
        else:
            return date_time.isoformat(' ')

    def format_time(x, pos=None):
        return convert_std_time_to_datetime(x).strftime('%H:%M:%S')

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_datetime))
    # ax.set_xticks(rotation=45, ha="right")
    # Give extra spacing at bottom of plot due to rotated labels
    # ax.get_figure().subplots_adjust(bottom=0.3)
    # Just let matplotlib do it...
    ax.get_figure().autofmt_xdate()
    # ax.xaxis.set_minor_formatter(ticker.FuncFormatter(format_time))


def _get_extent(ax):
    """
     Calculates the diagonal extent of plot area in Km
    :return: The diagonal size of the plot in Km
    """
    from cis.utils import haversine
    x0, x1, y0, y1 = ax.get_extent()
    return haversine(y0, x0, y1, x1)


def _test_natural_earth_available():
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


def drawcoastlines(ax, coastlinescolour):
    """
    Adds coastlines to a plot.
    There are three levels of resolution used based on the spatial scale of the plot. These are determined using
    values determined by eye for bluemarble and the coastlines independently.
    """
    coastline_scales = [(0, '110m'), (500, '50m'), (100, '10m')]

    ext = _get_extent(ax)

    if _test_natural_earth_available():
        coastline_res = coastline_scales[0][1]
        for scale, res in coastline_scales[1:]:
            if scale > ext:
                coastline_res = res

        ax.coastlines(color=coastlinescolour, resolution=coastline_res)
    else:
        logging.warning('Unable to access the natural earth topographies required for plotting coastlines. '
                        'Check internet connectivity and try again')


def drawbluemarble(ax, transform):
    """
    Adds nasa blue marble back ground to a plot
    There are three levels of resolution used based on the spatial scale of the plot. These are determined using
    values determined by eye for bluemarble and the coastlines independently.
    """
    from matplotlib.image import imread
    import os.path as path
    bluemarble_scales = [(0, 'raster/world.topo.bathy.200407.3x1350x675.png'),
                         (5000, 'raster/world.topo.bathy.200407.3x2700x1350.png'),
                         (2500, 'raster/world.topo.bathy.200407.3x5400x2700.png')]

    coastline_scales = [(0, '110m'), (500, '50m'), (100, '10m')]

    ext = _get_extent(ax)

    # Search for the right resolution
    bluemarble_res = bluemarble_scales[0][1]
    for scale, res in bluemarble_scales[1:]:
        if scale > ext:
            bluemarble_res = res

    img = imread(path.join(path.dirname(path.realpath(__file__)), bluemarble_res))
    ax.imshow(img, origin='upper', transform=transform, extent=[-180, 180, -90, 90])


def auto_set_map_ticks(ax, transform):
    """
    Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
    Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
    vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
    """
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from matplotlib.ticker import MaxNLocator

    max_x_bins = 9
    max_y_bins = 7  # as plots are wider rather than taller

    lon_steps = [1, 3, 6, 9, 10]
    lat_steps = [1, 3, 6, 9, 10]
    variable_step = [1, 2, 4, 5, 10]

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    if (xmax - xmin) < 5:
        lon_steps = variable_step
    if (ymax - ymin) < 5:
        lat_steps = variable_step

    # We need to make a special exception for particularly narrow and wide plots, which will be lat vs lon
    # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
    # the maximum number of bins.
    if (ymax - ymin) > 2.2 * (xmax - xmin):
        max_x_bins = 4
        max_y_bins = 11
    elif (xmax - xmin) > 2.2 * (ymax - ymin):
        max_x_bins = 14
        max_y_bins = 4

    lon_locator = MaxNLocator(nbins=max_x_bins, steps=lon_steps)
    ax.set_xticks(lon_locator.tick_values(xmin, xmax), crs=transform)
    ax.xaxis.set_major_formatter(LongitudeFormatter())

    lat_locator = MaxNLocator(nbins=max_y_bins, steps=lat_steps)
    ax.set_yticks(lat_locator.tick_values(ymin, ymax), crs=transform)
    ax.yaxis.set_major_formatter(LatitudeFormatter())


def auto_set_ticks(ax, axis, lat_lon=False):
    """
    Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
    Log axes generally come out nicely spaced without needing manual intervention.
    """
    # TODO: The decision whether to do the actual setting should be done outside this function
    # TODO: Split into one function which just works on a single axis, with lat or lon as a bool
    from matplotlib.ticker import MaxNLocator, AutoMinorLocator
    import numpy as np
    max_bins = 9

    lat_lon_steps = [1, 3, 6, 9, 10]
    variable_step = [1, 2, 4, 5, 10]

    mpl_axis = getattr(ax, "{}axis".format(axis))

    # Use lat/lon steps if we're a lat/lon axis with a large enough range
    steps = lat_lon_steps if lat_lon and np.diff(mpl_axis.get_data_interval()) > 5 else variable_step

    mpl_axis.set_major_locator(MaxNLocator(nbins=max_bins, steps=steps))
    mpl_axis.set_minor_locator(AutoMinorLocator())
    mpl_axis.grid(False, which='minor')


class Plotter(object):

    def __init__(self, data, type=None, out_filename=None, xaxis=None, yaxis=None, layer_opts=None, plotheight=None,
                 plotwidth=None, logx=False, logy=False, xmin=None, nocolourbar=False, nasabluemarble=False,
                 xmax=None, xstep=None, ymin=None, ymax=None, ystep=None, cbarlabel=None, coastlinescolour='k',
                 grid=False, xlabel=None, ylabel=None, title=None, fontsize=None,
                 cbarscale=None, cbarorient=None, projection=None, *args, **kwargs):
        """
        Constructor for the plotter. Note that this method also does the actual plotting.

        :param data: A list of packed (i.e. GriddedData or UngriddedData objects) data items to be plotted
        :param type: The plot type to be used, as a string
        :param out_filename: The filename of the file to save the plot to. Optional. Various file extensions can be
         used, with png being the default
        :param args: Any other arguments received from the parser
        :param kwargs: Any other keyword arguments received from the plotter
        """
        from cis.exceptions import InvalidNumberOfDatagroupsSpecifiedError
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs
        from .genericplot import Generic2DPlot

        layer_opts = layer_opts or [{}]

        if type in plot_types:
            type = type
        elif type is None:
            type = get_default_plot_type(data)
        else:
            raise ValueError("Invalid plot type, must be one of: {}".format(plot_types.keys()))

        if not plot_types[type].valid_number_of_datagroups(len(data)):
            raise InvalidNumberOfDatagroupsSpecifiedError("Invalid number of datagroups specified. Only one datagroup "
                                                          "can be plotted for a {}.".format(type))

        self.set_width_and_height(plotwidth, plotheight)

        # Initially we have no axis
        ax = None

        # Each plot is really just one 'layer', it should only get arguments relevant for that layer.
        # TODO: I'll have to choose colors for each layer if they haven't been set already...
        for d, params in zip(data, layer_opts):
            layer_args = dict(list(kwargs.items()) + list(params.items()))
            # TODO Move xaxis and yaxis into layer_opts
        ax = data.plot(how=plot_types[type], ax=ax, x=xaxis, y=yaxis, layer_opts=layer_opts, *args, **kwargs)

        # TODO: All of the below functions should be static, take their own arguments and apply only to the plot.ax
        # instance
        apply_axis_limits(ax, xmin, xmax, ymin, ymax, projection=projection, reverse_y=(yaxis == 'air_pressure'))

        xlabel = xlabel or self.plot_types[type].guess_axis_label(data, xaxis)
        ylabel = ylabel or self.plot_types[type].guess_axis_label(data, yaxis)

        # TODO figure out what to do about the transforms floating about the place.
        format_plot(ax, logx, logy, grid, xstep, ystep, fontsize, xlabel, ylabel, title, transform, legend=len(data)>1)

        if isinstance(self.plot_types[type], Generic2DPlot) and not nocolourbar:
            self.plot_types[type].add_color_bar(cbarlabel=cbarlabel or format_units(data[0].units), cbarscale=cbarscale,
                                                cbarorient=cbarorient)

        self.output_to_file_or_screen(out_filename)

    def output_to_file_or_screen(self, out_filename=None):
        """
        Outputs to screen unless a filename is given

        :param out_filename: The filename of the file to save the plot to. Various file extensions can be used, with
         png being the default
        """
        import logging
        if out_filename is None:
            self.fig.show()
        else:
            logging.info("saving plot to file: " + out_filename)
            width = self.fig.get_figwidth()
            self.fig.savefig(out_filename, bbox_inches='tight',
                             pad_inches=0.05 * width)  # Will overwrite if file already exists

    def set_width_and_height(self, width, height):
        """
        Sets the width and height of the plot
        Uses an aspect ratio of 4:3 if only one of width and height are specified
        If neither width or height are specified it defaults to 8 by 6 inches.
        """

        if height is not None:
            if width is None:
                width = height * (4.0 / 3.0)
        elif width is not None:
            height = width * (3.0 / 4.0)
        else:
            height = 6
            width = 8

        self.fig.set_figheight(height)
        self.fig.set_figwidth(width)


plot_types = {"contour": ContourPlot,
              "contourf": ContourfPlot,
              "heatmap": Heatmap,
              "line": LinePlot,
              "scatter": ScatterPlot,
              "comparativescatter": ComparativeScatter,
              "overlay": Overlay,
              "histogram2d": Histogram,
              "histogram3d": Histogram2D}


def get_default_plot_type(data):
    """
    Sets the default plot type based on the number of dimensions of the data
    :param CommonData data: The data to plot
    :return: The default plot type as a string
    """
    from cis.exceptions import InvalidPlotTypeError
    from iris.cube import Cube
    import logging
    number_of_coords = 0
    for coord in data.coords(dim_coords=True):
        if len(coord.shape) != 1 or coord.shape[0] != 1:
            number_of_coords += 1
    try:
        if number_of_coords == 1:
            plot_type = "line"
        elif isinstance(data, Cube):
            plot_type = "heatmap"
        else:
            plot_type = "scatter"
        logging.info("No plot type specified. Plotting data as a " + plot_type)
        return plot_type
    except KeyError:
        # TODO: When is this code actually hit...?
        coord_shape = None
        all_coords_are_of_same_shape = False
        for coord in data.coords():
            if coord_shape is None:
                coord_shape = coord.shape
                all_coords_are_of_same_shape = True
            elif coord_shape != coord.shape:
                all_coords_are_of_same_shape = False
                break

        error_message = "There is no valid plot type for this variable\nIts shape is: " + str(data.shape)
        if all_coords_are_of_same_shape:
            error_message += "\nThe shape of its coordinates is: " + str(data.coords()[0].shape)
        raise InvalidPlotTypeError(error_message)


def get_x_wrap_start(data, user_xmin=None):
    from cis.utils import find_longitude_wrap_start

    # FIND THE WRAP START OF THE DATA
    data_wrap_start = find_longitude_wrap_start(data)

    # NOW find the wrap start of the user specified range
    if user_xmin is not None:
        x_wrap_start = -180 if user_xmin < 0 else 0
    else:
        x_wrap_start = data_wrap_start

    return x_wrap_start
