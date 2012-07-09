import os

from numpy.random import randn
from matplotlib import pyplot
from matplotlib.pyplot import figure


def demo_one_ax():
    fig = figure()
    ax = fig.gca()
    ax.plot(randn(100))
    ax.set_title("This is title")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    return fig


def demo_two_ax_horizontal():
    fig = figure()
    ax211 = fig.add_subplot(211)
    ax211.plot(randn(100))
    ax211.set_title("First title")
    ax211.set_xlabel("X1-axis")
    ax211.set_ylabel("Y1-axis")
    ax212 = fig.add_subplot(212)
    ax212.plot(randn(100))
    ax212.set_title("Second title")
    ax212.set_xlabel("X2-axis")
    ax212.set_ylabel("Y2-axis")
    return fig


def demo_two_ax_vertical():
    fig = figure()
    ax121 = fig.add_subplot(121)
    ax121.plot(randn(100))
    ax121.set_title("First title")
    ax121.set_xlabel("X1-axis")
    ax121.set_ylabel("Y1-axis")
    ax122 = fig.add_subplot(122)
    ax122.plot(randn(100))
    ax122.set_title("Second title")
    ax122.set_xlabel("X2-axis")
    ax122.set_ylabel("Y2-axis")
    return fig


def demo_subplot2grid():
    fig = figure()
    pyplot.subplot2grid((3, 3), (0, 0), colspan=3)
    pyplot.subplot2grid((3, 3), (1, 0), colspan=2)
    pyplot.subplot2grid((3, 3), (1, 2), rowspan=2)
    pyplot.subplot2grid((3, 3), (2, 0))
    pyplot.subplot2grid((3, 3), (2, 1))
    return fig


def demo_gridspec():
    import matplotlib.gridspec as gridspec
    fig = figure()
    gs = gridspec.GridSpec(2, 2,
                           width_ratios=[1, 2],
                           height_ratios=[4, 1],
                           )

    pyplot.subplot(gs[0])
    pyplot.subplot(gs[1])
    pyplot.subplot(gs[2])
    pyplot.subplot(gs[3])
    return fig


def demo_scale_log():
    fig = figure()
    ax = fig.gca()
    ax.plot([1, 10, 100])
    ax.set_yscale("log")
    return fig


def demo_scale_symlog():
    fig = figure()
    ax = fig.gca()
    ax.plot([1, 10, 100, -1, -10, -100])
    ax.set_yscale("symlog")
    return fig


def demo_two_lines():
    fig = figure()
    ax = fig.gca()
    ax.plot(randn(10))
    ax.plot(randn(10))
    return fig


def demo_two_markers():
    fig = figure()
    ax = fig.gca()
    ax.plot(randn(10), "o")
    ax.plot(randn(10), "o")
    return fig


def demo_markers():
    # these are the markers supported by chaco
    from chaco.shell.plot_maker import marker_trans

    fig = figure()
    ax = fig.gca()
    for m in marker_trans:
        ax.plot(randn(10), randn(10), linestyle="None", marker=m)
    return fig


def demo_line_styles():
    # these are the lines supported by chaco
    from chaco.shell.plot_maker import line_trans
    line_trans

    fig = figure()
    ax = fig.gca()
    for l in line_trans:
        ax.plot(randn(10), linestyle=l)
    return fig


def demo_mixed_lines_and_markers():
    fig = figure()
    ax = fig.gca()
    ax.plot(randn(10), "o-")
    ax.plot(randn(10), "o-", color="magenta", markerfacecolor="cyan")
    return fig


def demo_bar_and_step():
    fig = figure()
    ax = fig.gca()
    ax.hist(randn(1000))
    ax.hist(randn(1000), histtype='step')
    return fig


def demo_scatter_simple():
    fig = figure()
    ax = fig.gca()
    ax.scatter(randn(1000), randn(1000))
    return fig


def demo_scatter_color():
    fig = figure()
    ax = fig.gca()
    ax.scatter(randn(1000), randn(1000), c=randn(1000))
    return fig


def demo_mplex_scatter_hist():
    import numpy as np
    from matplotlib.ticker import NullFormatter

    # the random data
    x = np.random.randn(1000)
    y = np.random.randn(1000)

    nullfmt = NullFormatter()         # no labels

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # start with a rectangular Figure
    fig = figure()

    axScatter = pyplot.axes(rect_scatter)
    axHistx = pyplot.axes(rect_histx)
    axHisty = pyplot.axes(rect_histy)

    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.scatter(x, y)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = np.max([np.max(np.fabs(x)), np.max(np.fabs(y))])
    lim = (int(xymax / binwidth) + 1) * binwidth

    axScatter.set_xlim((-lim, lim))
    axScatter.set_ylim((-lim, lim))

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    return fig


demos = list(v for (k, v) in locals().iteritems() if k.startswith("demo_"))
"""
A list of demo functions.
"""

demos.sort(key=lambda x: x.__name__)


def save_plot(plot, filename, width, height):
    # http://docs.enthought.com/chaco/user_manual/how_do_i.html
    from chaco.api import PlotGraphicsContext
    plot.outer_bounds = [width, height]
    plot.do_layout(force=True)
    gc = PlotGraphicsContext((width, height), dpi=72)
    gc.render_component(plot)
    gc.save(filename)


def mkdirp(path):
    if not os.path.exists(path):
        os.makedirs(path)


def run_demo(path, ext, seed):
    from matplotlib import rcParams
    import numpy.random
    from mplchaco import mpl2chaco
    mpldir = os.path.join(path, "mpl")
    chacodir = os.path.join(path, "chaco")
    mkdirp(mpldir)
    mkdirp(chacodir)

    # like IPython inline plot
    rcParams.update({
        'figure.figsize': (6.0, 4.0),
        'font.size': 10,
        'savefig.dpi': 72,
        'figure.subplot.bottom': 0.125,
    })
    numpy.random.seed(seed)

    imgfmt = "{{0}}.{0}".format(ext).format
    for func in demos:
        fig = func()
        cfig = mpl2chaco(fig)

        dpi = fig.get_dpi()
        width = fig.get_figwidth() * dpi
        height = fig.get_figheight() * dpi

        mplpath = imgfmt(os.path.join(mpldir, func.__name__))
        chacopath = imgfmt(os.path.join(chacodir, func.__name__))
        fig.savefig(mplpath)
        save_plot(cfig.plot, chacopath, width, height)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--path', default="data")
    parser.add_argument('--ext', default="png")
    parser.add_argument('--seed', default=12345, type=int)
    args = parser.parse_args()
    run_demo(**vars(args))


if __name__ == '__main__':
    main()
