"""Plots for trials related measures and analyses."""

import numpy as np

from spiketools.utils.base import flatten
from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.annotate import add_vlines, add_vshades, add_significance
from spiketools.plts.utils import check_ax, get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_rasters(data, vline=None, colors=None, vshade=None,
                 show_axis=False, ax=None, **plt_kwargs):
    """Plot rasters across multiple trials.

    Parameters
    ----------
    data : list of list of float
        Spike times per trial.
        Multiple conditions can also be passed in.
    vline : float or list of float, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
    colors : str or list of str, optional
        Color(s) to plot the raster ticks.
        If more than one, should match the number of conditions.
    vshade : list of float or list of list of float, optional
        Vertical region(s) of the plot to shade in.
    show_axis : bool, optional, default: False
        Whether to show the axis around the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'line_color', 'line_lw', 'line_alpha', 'shade_color', 'shade_alpha'.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    custom_kwargs = ['line_color', 'line_lw', 'line_alpha', 'shade_color', 'shade_alpha']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # This process infers whether there is are embedded lists of multiple conditions
    check = False
    for val in data:
        # The try / except is to deal with potentially empty lists (trials with no spikes)
        try:
            # This allows for plotting a raster with a single trial
            if isinstance(val, float):
                break
            # If this value is a collection, there are multiple conditions
            elif isinstance(val[0], (list, np.ndarray)):
                check = True
                break
        except (IndexError, TypeError):
            continue

    # If multiple conditions, organize colors across trials, and flatten data for plotting
    if check:
        lens = [len(el) for el in data]
        colors = DEFAULT_COLORS[0:len(lens)] if not colors else colors
        colors = flatten([[col] * ll for col, ll in zip(colors, lens)])
        data = flatten(data)

    ax.eventplot(data, colors=colors, **plt_kwargs)

    add_vlines(vline, ax,
               color=custom_plt_kwargs.pop('line_color', 'green'),
               lw=custom_plt_kwargs.pop('line_lw', 2.5),
               alpha=custom_plt_kwargs.pop('line_alpha', 0.5))
    add_vshades(vshade, ax,
                color=custom_plt_kwargs.pop('shade_color', 'red'),
                alpha=custom_plt_kwargs.pop('shade_alpha', 0.25))

    if not show_axis:
        ax.set_axis_off()


@savefig
@set_plt_kwargs
def plot_rate_by_time(x_vals, y_vals, average=None, shade=None, colors=None,
                      labels=None, stats=None, sig_level=0.05, ax=None, **plt_kwargs):
    """Plot continuous firing rates across time.

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
    colors : str or list of str, optional
        Color(s) to plot the firing rates.
        If more than one, should match the number of conditions.
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
        Custom kwargs: 'shade_alpha', 'legend_loc'.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    custom_kwargs = ['shade_alpha', 'legend_loc']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    if not isinstance(y_vals[0], np.ndarray):
        y_vals = [y_vals]

    colors = DEFAULT_COLORS[0:len(y_vals)] if not colors else colors

    if isinstance(shade, str):
        shade = [get_var_func(shade)(arr, 0) for arr in y_vals]

    if isinstance(average, str):
        y_vals = [get_avg_func(average)(arr, 0) for arr in y_vals]

    for ind, (ys, color) in enumerate(zip(y_vals, colors)):

        ax.plot(x_vals, ys, color=color,
                label=labels[ind] if labels else None,
                lw=plt_kwargs.pop('lw', 3), **plt_kwargs)

        if shade:
            ax.fill_between(x_vals, ys-shade[ind], ys+shade[ind],
                            color=color, alpha=custom_plt_kwargs.pop('alpha', 0.25))

    if labels:
        ax.legend(loc=custom_plt_kwargs.pop('legend_loc', 'best'))

    if stats:
        add_significance(stats, sig_level=sig_level, ax=ax)


def create_raster_title(label, avg_pre, avg_post, t_val=None, p_val=None):
    """Create a standardized title for an event-related raster plot.

    Parameters
    ----------
    label : str
        Label to add to the beginning of the title.
    avg_pre, avg_post : float
        The average firing rates pre and post event.
    t_val, p_val : float, optional
        The t value and p statistic for a t-test comparing pre and post event firing.

    Returns
    -------
    title : str
        Title for the plot.
    """

    if t_val is None:
        title = '{} - Pre: {:1.2f} / Post: {:1.2f}'.format(label, avg_pre, avg_post)
    else:
        title = '{} - Pre: {:1.2f} / Post: {:1.2f} (t:{:1.2f}, p:{:1.2f})'.format(\
            label, avg_pre, avg_post, t_val, p_val)

    return title
