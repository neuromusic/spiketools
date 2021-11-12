"""Plots for spikes."""

from spiketools.utils.select import get_avg_func, get_var_func
from spiketools.plts.data import plot_bar
from spiketools.plts.utils import check_ax, savefig, set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_waveform(waveform, average=None, shade=None, add_traces=False, ax=None, **plt_kwargs):
    """Plot a spike waveform.

    Parameters
    ----------
    waveform : 1d or 2d array
        Voltage values of the spike waveform.
    average : {'mean', 'median'}, optional
        Averaging to apply to firing rate activity before plotting.
    shade : {'sem', 'std'} or 1d array, optional
        Measure of variance to compute and/or plot as shading.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if isinstance(shade, str):
        shade = get_var_func(shade)(waveform, 0)

    if isinstance(average, str):
        all_waveforms = waveform
        waveform = get_avg_func(average)(waveform, 0)

    ax.plot(waveform, **plt_kwargs)

    if add_traces:
        line = ax.lines[0]
        ax.plot(line.get_xdata(), all_waveforms.T,
                lw=1, alpha=0.5, color=line.get_color())

    if shade is not None:
        ax.fill_between(ax.lines[0].get_xdata(), waveform-shade, waveform+shade, alpha=0.25)

    ax.set(title='Spike Waveform')


@savefig
@set_plt_kwargs
def plot_isis(isis, bins=None, range=None, density=False, ax=None, **plt_kwargs):
    """Plot a distribution of ISIs.

    Parameters
    ----------
    isis : 1d array
        Interspike intervals.
    bins : int or list, optional
        Bin definition, either a number of bins to use, or bin definitions.
    range : tuple, optional
        Range of the data to plot.
    density : bool, optional, default: False
        Whether to draw a probability density.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    ax.hist(isis, bins=bins, range=range, density=density, **plt_kwargs)
    ax.set(xlabel='Time', title='ISIs')


@savefig
@set_plt_kwargs
def plot_unit_frs(rates, ax=None, **plt_kwargs):
    """Plot firing rates for a group of neurons.

    Parameters
    ----------
    rates : list of float
        Firing rates.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    plot_bar(rates, labels=['U' + str(ind) for ind in range(len(rates))], ax=ax, **plt_kwargs,
             xlabel='Units', ylabel='Firing Rate (Hz)', title='Firing Rates of all Units')