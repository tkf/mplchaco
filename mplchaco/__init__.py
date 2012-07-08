"""
Matplotlib to Chaco converter.

Usage::

    from mplchaco import mpl2chaco
    mpl2chaco(fig).configure_traits()

Note that when using from IPython, make sure execute ``%gui wx``
**before** importing `mplchaco`.  Otherwise, opening Chaco window
blocks IPython.

"""

from chaco.api import ArrayPlotData, Plot
from chaco.base_plot_container import BasePlotContainer
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance, List
from traitsui.api import View, Item

from matplotlib.colors import colorConverter


class RelativeLocationPlotContainer(BasePlotContainer):

    """
    Container class using MPL's bbox to locate plots.
    """

    boxes = List(value=[])

    def add_plot(self, plot, box):
        self.add(plot)
        self.boxes.append(box)

    def _do_layout(self):
        # See also: `chaco.api.GridPlotContainer._do_layout`
        (width, height) = self.bounds
        for (plot, box) in zip(self.components, self.boxes):
            # `box` already considers spacing.
            # So, do not use `outer_*` here.
            plot.position = [box.x0 * width, box.y0 * height]
            plot.width = (box.x1 - box.x0) * width
            plot.height = (box.y1 - box.y0) * height
            plot.do_layout()


class MPLChaco(HasTraits):

    plot = Instance(RelativeLocationPlotContainer)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        width=1000, height=600, resizable=True
    )

    def __init__(self, fig):
        """Initialize given an instance of `matplotlib.figure.Figure`."""
        super(MPLChaco, self).__init__()
        self._fig = fig

    def _plot_default(self):
        fig = self._fig
        axes = fig.get_axes()
        container = RelativeLocationPlotContainer()
        pd = ArrayPlotData()

        for (i, ax) in enumerate(axes):
            plot = Plot(pd)

            for (j, li) in enumerate(ax.get_lines()):
                self._plot_from_line(
                    plot,
                    'x_{0}_{1}'.format(i, j),
                    'y_{0}_{1}'.format(i, j),
                    li,
                )

            self._migrate_plot_attributes(ax, plot)
            container.add_plot(plot, ax.get_position())

        return container

    @staticmethod
    def _plot_from_line(plot, xname, yname, line):
        """
        Plot lines in Chaco Plot object `plot` given MPL Line2D `line`.
        """
        plot.data.set_data(xname, line.get_xdata())
        plot.data.set_data(yname, line.get_ydata())

        if line.get_linestyle() != "None":
            plot.plot(
                (xname, yname),
                color=colorConverter.to_rgba(line.get_color()))
        if line.get_marker() != "None":
            plot.plot(
                (xname, yname),
                type="scatter",
                color=colorConverter.to_rgba(line.get_markerfacecolor()))

    @staticmethod
    def _migrate_plot_attributes(mpl, cha):
        """
        Copy attributes of MPL Axes `mpl` to Chaco Plot `cha`.
        """
        cha.title = mpl.get_title()
        cha.x_axis.title = mpl.get_xlabel()
        cha.y_axis.title = mpl.get_ylabel()

        # As Chaco does not support symlog, use linear instead
        conv_scale = lambda s: "linear" if s == "symlog" else s
        cha.index_scale = conv_scale(mpl.get_xscale())
        cha.value_scale = conv_scale(mpl.get_yscale())


def mpl2chaco(fig):
    """
    Convert a MPL figure object to Chaco figure instance
    """
    return MPLChaco(fig)
