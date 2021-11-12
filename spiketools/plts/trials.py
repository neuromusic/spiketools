"""Plots for trials related measures and analyses."""

import numpy as np

from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.annotate import _add_significance_to_plot
from spiketools.plts.utils import check_ax, savefig, set_plt_kwargs
from spiketools.utils.select import get_avg_func, get_var_func
from spiketools.utils.base import flatten

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_rasters(data, line=0, show_axis=False, colors=None, ax=None, **plt_kwargs):
    """Plot rasters across multiple trials.

    Parameters
    ----------
    data : list of list
        Spike times per trial.
    line : float, optional, default: 0
        Position to draw a vertical line. If None, no line is drawn.
    show_axis : bool, optional, default: False
        Whether to show the axis around the plot.
    colors : str or list of str
        xx
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if isinstance(data[0][0], list):
        lens = [len(el) for el in data]
        colors = DEFAULT_COLORS[0:len(lens)] if not colors else colors
        colors = flatten([[col] * ll for col, ll in zip(colors, lens)])
        data = flatten(data)

    ax.eventplot(data, colors=colors)

    if line is not None:
        ax.vlines(line, -1, len(data), lw=2.5, color='green', alpha=0.5)

    if not show_axis:
        ax.set_axis_off()


@savefig
@set_plt_kwargs
def plot_firing_rates(x_vals, y_vals, average=None, shade=None, labels=None,
                      stats=None, sig_level=0.05, ax=None, **plt_kwargs):
    """Plot continuous spike firing rates.

    Parameters
    ----------
    x_vals : 1d array
        Values for the x-axis, for example time values or bin numbers.
    y_vals : list of array
        One or many set of values for the y-axis.
        If each array is 1d values are plotted directly.
        If 2d, is to be averaged before plotting.
    average : {'mean', 'median'}, optional
        Averaging to apply to firing rate activity before plotting.
    shade : {'sem', 'std'} or list of array, optional
        Measure of variance to compute and/or plot as shading.
    labels : list of str, optional
        Labels for each set of y-values.
        If provided, a legend is added to the plot.
    stats : list, optional
        Statistical results, including p-values, to use to annotate the plot.
    sig_level : float, optional, default: 0.05
        Threshold level to consider a result significant.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if not isinstance(y_vals[0], np.ndarray):
        y_vals = [y_vals]

    if isinstance(shade, str):
        shade = [get_var_func(shade)(arr, 0) for arr in y_vals]

    if isinstance(average, str):
        y_vals = [get_avg_func(average)(arr, 0) for arr in y_vals]

    for ind, ys in enumerate(y_vals):

        ax.plot(x_vals, ys, lw=3, label=labels[ind] if labels else None, **plt_kwargs)

        if shade:
            ax.fill_between(x_vals, ys-shade[ind], ys+shade[ind], alpha=0.25)

    if labels:
        ax.legend(loc='best')

    if stats:
        _add_significance_to_plot(stats, sig_level=sig_level, ax=ax)