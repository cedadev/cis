"""
Class for plotting graphs.
Also contains a dictionary for the valid plot types.
All plot types need to be imported and added to the plot_types dictionary in order to be used.
"""
import logging

from cis.plotting.comparativescatter import ComparativeScatter
from cis.plotting.contourplot import ContourPlot, ContourfPlot
from cis.plotting.heatmap import Heatmap
from cis.plotting.histogram import Histogram
from cis.plotting.histogram2d import Histogram2D
from cis.plotting.lineplot import LinePlot
from cis.plotting.scatterplot import ScatterPlot, ScatterPlot2D

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']


plot_types = {"contour": ContourPlot,
              "contourf": ContourfPlot,
              "heatmap": Heatmap,
              "line": LinePlot,
              "scatter": ScatterPlot,
              "scatter2d": ScatterPlot2D,
              "comparativescatter": ComparativeScatter,
              "histogram": Histogram,
              "histogram2d": Histogram2D}


def format_units(units):
    """
    :param units: The units of a variable, as a string
    :return: The units surrounding brackets, or the empty string if no units given
    """
    if "since" in str(units):
        # Assume we are on a time if the units contain since.
        return ""
    elif units:
        return "(" + str(units) + ")"
    else:
        return ""


def get_label(common_data, units=True):
    name = common_data.name() or ""
    if units:
        if name:
            name += " "
        name += format_units(common_data.units)
    return name


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
            if axis == 'X' or len(d.shape) == 1:
                if c.shape[0] == d.shape[0]:
                    coord = c
                    break
            elif axis == 'Y' and len(d.shape) > 1:
                if c.shape[1] == d.shape[1]:
                    coord = c
                    break

    logging.info("Plotting " + coord.name() + " on the {} axis".format(axis))

    return coord


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
    from six.moves.urllib.error import HTTPError
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


def drawbluemarble(ax):
    """
    Adds nasa blue marble back ground to a plot
    There are three levels of resolution used based on the spatial scale of the plot. These are determined using
    values determined by eye for bluemarble and the coastlines independently.
    """
    from matplotlib.image import imread
    import cartopy.crs as ccrs
    import os.path as path
    from cis.utils import no_autoscale

    source_proj = ccrs.PlateCarree()

    bluemarble_scales = [(0, 'raster/world.topo.bathy.200407.3x1350x675.png'),
                         (5000, 'raster/world.topo.bathy.200407.3x2700x1350.png'),
                         (2500, 'raster/world.topo.bathy.200407.3x5400x2700.png')]

    ext = _get_extent(ax)

    # Search for the right resolution
    bluemarble_res = bluemarble_scales[0][1]
    for scale, res in bluemarble_scales[1:]:
        if scale > ext:
            bluemarble_res = res

    img = imread(path.join(path.dirname(path.realpath(__file__)), bluemarble_res))
    # Don't change the scale of the plot
    with no_autoscale(ax):
        ax.imshow(img, origin='upper', transform=source_proj, extent=[-180, 180, -90, 90])


def auto_set_map_ticks(ax, gridlines=True):
    """
    Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
    Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
    vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
    """
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

    try:
        gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5)
        # Turn off the top and right-hand labels
        gl.xlabels_top = False
        gl.ylabels_right = False

        # Format the lat/lon labels nicely
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
    except TypeError:
        # Labels not supported for this projection, try without...
        gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5)

    if not gridlines:
        gl.xlines = False
        gl.ylines = False
    # TODO It would be nice to have ticks if we don't have lines...
    # ax.tick_params(direction='out')


def add_color_bar(mappable, vstep, logv, cbarscale, cbarorient, cbarlabel):
    """
    Adds a colour bar to a plot
    Allows specifying of tick spacing and orientation
    """
    import matplotlib.pyplot as plt
    from .formatter import LogFormatterMathtextSpecial
    from matplotlib.ticker import MultipleLocator

    cbar_kwargs = {}

    if vstep is not None:
        cbar_kwargs['ticks'] = MultipleLocator(vstep)

    if logv:
        cbar_kwargs['formatter'] = LogFormatterMathtextSpecial(10, labelOnlyBase=False)
    #
    if cbarscale is not None:
        cbar_kwargs['shrink'] = cbarscale

    if cbarorient is not None:
        cbar_kwargs['orientation'] = cbarorient

    cbar = plt.colorbar(mappable, **cbar_kwargs)

    if not logv:
        cbar.formatter.set_scientific(True)
        cbar.formatter.set_powerlimits((-3, 3))
        cbar.update_ticks()

    cbar.set_label(cbarlabel)


def basic_plot(data, how=None, ax=None, xaxis=None, yaxis=None, projection=None, central_longitude=0.0,
               label=None, *args, **kwargs):
    import cartopy.crs as ccrs
    from cartopy.mpl.geoaxes import GeoAxes
    import matplotlib.pyplot as plt
    from cis.data_io.common_data import CommonData
    from cis.data_io.gridded_data import GriddedData
    from cis.utils import squeeze

    # TODO x and y should be Coord or CommonData objects only by the time they reach the plots

    # Remove any extra gridded data dimensions
    if isinstance(data, GriddedData):
        data = squeeze(data)

    if isinstance(xaxis, CommonData):
        if how is not None:
            if how not in ['comparativescatter', 'histogram2d']:
                raise ValueError("....")
        else:
            how = 'comparativescatter'
    else:
        xaxis = get_axis(data, 'X', xaxis)
    # TODO: The y axis should probably be worked out by the plotter - it is different for 2D (data) and 3D (coord)
    # TODO: In fact, I might be better off combining the get axis calls into one method, since they are interdependant
    # for example it doesn't give sensible axis for make_regular_2d_ungridded_data with no coord axis metadata
    #  (even though they have standard names)
    yaxis = get_axis(data, 'Y', yaxis)

    how = how or data._get_default_plot_type(xaxis.standard_name == 'longitude'
                                             and yaxis.standard_name == 'latitude')

    # TODO: Check that projection=None is a valid default.
    label = get_label(data) if label is None else label

    try:
        plot = plot_types[how](data, xaxis=xaxis, yaxis=yaxis, label=label,
                               *args, **kwargs)
    except KeyError:
        raise ValueError("Invalid plot type, must be one of: {}".format(plot_types.keys()))

    if ax is None:
        if plot.is_map():
            if projection is None:
                projection = ccrs.PlateCarree(central_longitude=central_longitude)
            plot.mplkwargs['transform'] = ccrs.PlateCarree()
            _, ax = plt.subplots(subplot_kw={'projection': projection})
            # Monkey-patch the nasabluemarble method onto the axis
            GeoAxes.bluemarble = drawbluemarble
        else:
            _, ax = plt.subplots()

    # Make the plot
    plot(ax)

    if xaxis.standard_name == 'time':
        set_x_axis_as_time(ax)

    if yaxis.standard_name == 'air_pressure':
        ax.invert_yaxis()

    return plot, ax


def multilayer_plot(data_list, how=None, ax=None, yaxis=None, layer_opts=None, *args, **kwargs):
    if how in ['comparativescatter', 'histogram2d']:
        if yaxis is not None:
            raise ValueError("...")
            # TODO
        plot, ax = basic_plot(data_list[1], how, ax, xaxis=data_list[0], *args, **kwargs)
    else:
        layer_opts = [{} for i in data_list] if layer_opts is None else layer_opts

        if not isinstance(yaxis, list):
            yaxis = [yaxis for i in data_list]

        for d, y, opts in zip(data_list, yaxis, layer_opts):
            layer_kwargs = dict(list(kwargs.items()) + list(opts.items()))
            how = layer_kwargs.pop('type', how)
            label = layer_kwargs.pop('label', get_label(d, units=False))
            plot, ax = basic_plot(d, how, ax, yaxis=y, label=label, *args, **layer_kwargs)

        legend = ax.legend(loc="best")
        if legend is not None:
            legend.draggable(state=True)

    return plot, ax
