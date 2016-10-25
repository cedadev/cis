"""
Plot a Taylor diagram comparing datasets. This is quite different to the other plot types and so does more formatting
itself than we normally would.

From Zak Kipling's implemention in https://scm.physics.ox.ac.uk/svn/climproc_python/trunk/scripts/taylor.py
"""
from itertools import cycle, repeat
from six.moves import zip
import logging
from matplotlib.transforms import Transform
import matplotlib.cm

import numpy as np
from cis.plotting.genericplot import APlot


class CosTransform(Transform):
    """Cosine transform for a coordinate axis"""
    input_dims = 1
    output_dims = 1
    is_separable = True
    has_inverse = True

    def transform_non_affine(self, a):
        return np.ma.cos(a)

    def inverted(self):
        return ArcCosTransform()


class ArcCosTransform(Transform):
    """Inverse cosine transform for a coordinate axis"""
    input_dims = 1
    output_dims = 1
    is_separable = True
    has_inverse = True

    def transform_non_affine(self, a):
        return np.ma.arccos(a)

    def inverted(self):
        return CosTransform()


class Bunch(object):
    """
    Bunch a dict up into a 'namespace'

    Courtesy of http://stackoverflow.com/questions/2597278/python-load-variables-in-a-dict-into-namespace
    """
    def __init__(self, adict):
        self.__dict__.update(adict)


class Taylor(APlot):

    def __init__(self, packed_data, labels=None, colors=None, markers=None, extend=0.0, fold=False, logv=False,
                 gammamax=None, solid=False, stdbiasmax=None, bias=None,
                 cbarscale=None, cbarorient=None, cbarlabel=None, *args, **kwargs):
        """
        A routine for producing taylor diagrams using matplotlib

        :param list packed_data: A list of CommonData objects to compare, the first item is taken as the reference
        :param list labels: List of labels for each of the datasets
        :param list colors: Specify colour(s) to use
        :param list markers: Specify marker(s) to use
        :param float extend: Extend plot for negative correlation, default 0.0
        :param bool fold: Fold plot for negative correlation or large variance, default False
        :param bool logv: Work on logarithms of data sets
        :param float gammamax: Fix maximum extent of radial axis
        :param bool solid: Use solid markers, default False
        :param float stdbiasmax: Fix maximum standardised bias
        :param string bias: Indicate bias using the specified method (colo[u]r, size or flag). Default is None
        :param float cbarscale: A scale factor for the colorbar
        :param string cbarorient: The colorbar orientation ('vertical' or 'horizontal')
        :param string cbarlabel: A label for the colorbar
        :param kwargs: Any other arguments for plot, such as alpha
        """
        # xaxis and yaxis are None in this special case
        super(Taylor, self).__init__(packed_data, None, None, *args, **kwargs)

        self.labels = [l or d.name() for l, d in zip(labels, packed_data)]
        self.colors = colors
        self.extend = extend
        self.fold = fold
        self.gammamax = gammamax
        self.solid = solid
        self.usrstdbiasmax = stdbiasmax
        self.bias = bias
        self.cbarscale = cbarscale
        self.cbarorient = cbarorient or 'horizontal'
        self.cbarlabel = cbarlabel

        self.itemwidth = self.itemwidth or 6

        if self.bias in ('color', 'colour'):
            self.solid = True
            if colors:
                raise ValueError('Cannot use colo[u]r kwarg with bias=colo[u]r')
        elif self.bias == 'size':
            if self.itemwidth:
                ValueError('Cannot use markersize kwarg with --bias=size')
        elif self.bias is not None and self.bias != 'flag':
            raise ValueError('Invalid bias argument specified, should be either colo[u]r, size or flag')

        if logv:
            packed_data = [np.ma.log(d.data) for d in packed_data]

        means = np.ma.array([np.ma.mean(d.data) for d in packed_data])
        sigmas = np.ma.array([np.ma.std(d.data, ddof=1) for d in packed_data])

        logging.info("Means: {}".format(means))
        # Treat the first array as the reference
        ref_mean = means[0]
        ref_sigma = sigmas[0]

        self.stdbiases = (means - ref_mean) / ref_sigma
        self.gammas = sigmas / ref_sigma

        # Calculate the correlations against the first array
        self.corrs = np.ma.array([np.ma.corrcoef(d.data, packed_data[0].data)[0, 1] for d in packed_data])
        self.corrs = np.ma.minimum(np.ma.maximum(self.corrs, -1.), 1.)

        if markers is None:
            if self.bias == 'size':
                #           -   0   +
                self.markers = ['v', 's', '^']
            else:
                if solid:
                    self.markers = ['o', 'v', '^', '<', '>', 's', 'p', 'h', 'D', '*']
                else:
                    self.markers = ['x', '+', 'o', 'v', '^', '<', '>', 's', 'p', 'h', 'D', '*']
        else:
            self.markers = markers

        mask = np.ma.getmaskarray(self.gammas)
        if self.gammamax and not fold:
            mask = np.logical_or(mask, self.gammas > self.gammamax)
        if self.bias:
            mask = np.logical_or(mask, np.ma.getmaskarray(self.stdbiases))
            if self.usrstdbiasmax:
                mask = np.ma.logical_or(mask, np.ma.abs(self.stdbiases) > self.usrstdbiasmax)

        self.gammamax = self.gammamax or np.ma.amax(np.ma.masked_where(mask, self.gammas))
        if self.bias:
            self.maxstdbias = self.usrstdbiasmax or np.ma.amax(np.ma.abs(np.ma.masked_where(mask, self.stdbiases)))
            self.minstdbias = min(np.ma.amin(np.ma.abs(np.ma.masked_where(mask[1:], self.stdbiases[1:]))), self.maxstdbias / 8)
            self.stdbiasrange = self.maxstdbias - self.minstdbias

        if self.bias:
            self.any_overbias = False
            self.any_underbias = False
        if extend > -1.:
            self.labels = [l + ' $-$' if c < extend else l for l, c in zip(self.labels, self.corrs)]
            if fold:
                if extend == 0.:
                    self.corrs = np.ma.abs(self.corrs)
                else:
                    self.corrs = np.ma.maximum(self.corrs, extend)
        if self.gammamax:
            self.labels = [l + ' $>$' if g > self.gammamax else l for l, g in zip(self.labels, self.gammas)]
            if fold:
                self.gammas = np.ma.minimum(self.gammas, self.gammamax)
        if self.bias and self.usrstdbiasmax:
            self.any_overbias = np.ma.any(self.stdbiases > self.usrstdbiasmax)
            self.any_underbias = np.ma.any(self.stdbiases < -self.usrstdbiasmax)
            self.labels = [l + ' B-' if b < -self.usrstdbiasmax else l for l, b in zip(self.labels, self.stdbiases)]
            self.labels = [l + ' B+' if b > self.usrstdbiasmax else l for l, b in zip(self.labels, self.stdbiases)]
            if fold:
                self.stdbiases = np.ma.maximum(np.ma.minimum(self.stdbiases, self.usrstdbiasmax), -self.usrstdbiasmax)

        if self.bias in ('color', 'colour'):
            self.mplkwargs['cmap'] = matplotlib.cm.get_cmap('RdBu_r')
            self.mplkwargs['cmap'].set_bad('gray')
            self.mplkwargs['norm'] = matplotlib.colors.Normalize(-self.maxstdbias, self.maxstdbias)

    def __call__(self, ax):
        from matplotlib.projections import PolarAxes
        from matplotlib.transforms import IdentityTransform, blended_transform_factory

        tr = blended_transform_factory(ArcCosTransform(), IdentityTransform()) + PolarAxes.PolarTransform()

        ax.axis["left"].set_axis_direction("left")  # point left ticks inwards
        ax.axis["left"].toggle(ticklabels=False, label=False)  # don't label left axis
        ax.axis["right"].toggle(ticklabels=True, label=True)  # label bottom axis instead
        ax.axis["right"].set_axis_direction("bottom")  # orient labels sensibly

        ax.axis["bottom"].set_visible(False)  # kill axis squeezed into bottom-left corner
        ax.axis["top"].toggle(ticklabels=True, label=True)  # label curved axis

        ax.axis["right"].label.set_text("$\sigma / \sigma_0$")
        ax.axis["top"].label.set_text("Correlation")

        ax.grid(True)

        ax2 = ax.get_aux_axes(tr)

        if self.bias != 'size':
            size = self.itemwidth

        logging.info("Label     Correlation     Gamma     StdBias     Marker     Size")
        for label, corr, gamma, stdbias, marker, color in zip(self.labels, self.corrs, self.gammas, self.stdbiases,
                                                              cycle(self.markers),
                                                              (cycle(self.colors) if self.colors
                                                               else repeat(None))):
            if self.bias == 'size':
                marker = self.markers[((stdbias > 0.) - (stdbias < 0.)) + 1]
                size = min(max((abs(stdbias) - self.minstdbias) / self.stdbiasrange, 0.), 1.)
                size = self.itemwidth * (0.25 + 1.75 * size)

            logging.info("        ".join([str(s) for s in (label, corr, gamma, stdbias, marker, size)]))

            if self.bias in ('color', 'colour'):
                if size is not None:
                    self.mplkwargs['s'] = size ** 2
                p = ax2.scatter(corr, gamma, c=stdbias, marker=marker, label=label, **self.mplkwargs)
                # So that correct colours are used in legend...
                p.update_scalarmappable()
            else:
                if size is not None:
                    self.mplkwargs['markersize'] = size
                if color is not None:
                    if ':' in color:
                        facecolor, edgecolor = [x or 'none' for x in color.split(':', 2)]
                        maincolor = facecolor if facecolor != 'none' else edgecolor
                        have_edge = (edgecolor not in 'none')
                        if not have_edge: edgecolor = facecolor
                    else:
                        maincolor = color
                        if self.solid:
                            facecolor, edgecolor = color, 'black'
                        else:
                            facecolor, edgecolor = 'none', color
                        have_edge = not self.solid
                    self.mplkwargs['markerfacecolor'] = facecolor
                    self.mplkwargs['markeredgecolor'] = edgecolor
                else:
                    have_edge = not self.solid

                for p in ax2.plot(corr, gamma, marker=marker,
                                  label=label, linestyle=' ', **self.mplkwargs):
                    if color is None:
                        maincolor = p.get_markerfacecolor()
                        if self.solid:
                            facecolor, edgecolor = maincolor, maincolor
                        else:
                            facecolor, edgecolor = 'none', maincolor

                            p.set_markeredgecolor(edgecolor)
                            p.set_markerfacecolor(facecolor)

                    if self.bias == 'flag':
                        std_cent_rmse = np.ma.sqrt(1. + gamma * (gamma - 2 * corr))
                        if std_cent_rmse > .0001:
                            cos_theta = corr
                            sin_theta = np.ma.sqrt(1 - corr ** 2)
                            cos_flag_angle = gamma * np.sqrt(1. - corr ** 2) / std_cent_rmse
                            sin_flag_angle = (corr * gamma - 1.) / std_cent_rmse
                            assert (np.abs(np.log(cos_flag_angle ** 2 + sin_flag_angle ** 2)) < .001)
                            ax.plot((gamma * cos_theta, gamma * cos_theta + stdbias * cos_flag_angle),
                                    (gamma * sin_theta, gamma * sin_theta - stdbias * sin_flag_angle),
                                    linestyle=('dashed' if not self.solid and facecolor == 'none' else 'solid'),
                                    marker=' ', color=maincolor)

        arc = np.linspace(0., np.pi, 50)
        for radius in np.arange(0., 2 * self.gammamax, .2):
            ax.plot(1.0 + np.cos(arc) * radius, np.sin(arc) * radius, linestyle='dotted', color='green')

        ax2.plot(np.linspace(1.0, self.extend, 50),
                 np.linspace(1.0, 1.0, 50),
                 linestyle='dashed', color='black')

        if self.extend < 0.:
            ax.plot((0., 0.), ax.get_ylim(), linestyle='solid', color='black')

        ax.legend(loc='upper right', numpoints=1, scatterpoints=1)

        if self.bias in ('color', 'colour'):
            extend = 'neither'
            if self.fold and self.usrstdbiasmax:
                if self.any_overbias and self.any_underbias:
                    extend = 'both'
                elif self.any_overbias:
                    extend = 'max'
                elif self.any_underbias:
                    extend = 'min'
            if self.cbarscale:
                cbar_kwargs = dict(shrink=self.cbarscale)
            else:
                cbar_kwargs = dict(fraction=0.046, pad=0.1)
            cb = ax.get_figure().colorbar(p, ax=ax, orientation=self.cbarorient, extend=extend, **cbar_kwargs)
            cb.set_label(self.cbarlabel or 'bias / $\sigma_0$')

        return ax

    def is_map(self):
        return False

    def set_log_scales(self, ax, logx, logy):
        pass  # Don't!
