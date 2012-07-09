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
from chaco.tools.api import PanTool, ZoomTool

from matplotlib.colors import colorConverter
import matplotlib.collections as mcoll
import matplotlib.patches as mpatches


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
                    'lx_{0}_{1}'.format(i, j),
                    'ly_{0}_{1}'.format(i, j),
                    li,
                )

            for (j, co) in enumerate(ax.collections):
                self._plot_from_collection(
                    plot,
                    'cx_{0}_{1}'.format(i, j),
                    'cy_{0}_{1}'.format(i, j),
                    co,
                )

            for (j, pa) in enumerate(ax.patches):
                self._plot_from_patch(
                    plot,
                    'px_{0}_{1}'.format(i, j),
                    'py_{0}_{1}'.format(i, j),
                    pa,
                )

            self._migrate_plot_attributes(ax, plot)
            self._setup_plot_tools(plot)
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
    def _plot_from_collection(plot, xname, yname, collection):
        """
        Plot in Chaco Plot object `plot` given MPL Collection `collection`.
        """
        if isinstance(collection, mcoll.PathCollection):
            # then assume it is the data plotted via Axes.scatter
            ofs = collection.get_offsets()
            plot.data.set_data(xname, ofs[:, 0])
            plot.data.set_data(yname, ofs[:, 1])
            plot.plot(
                (xname, yname),
                type="scatter",
                color=tuple(*collection.get_facecolor()))

    @staticmethod
    def _plot_from_patch(plot, xname, yname, patch):
        """
        Plot in Chaco Plot object `plot` given MPL Patch `patche`.
        """

        is_data_set = True
        if isinstance(patch, mpatches.Rectangle):
            x = patch.get_x()
            y = patch.get_y()
            w = patch.get_width()
            h = patch.get_height()
            xdata = [x, x, x + w, x + w]
            ydata = [y, y + h, y + h, y]
            plot.data.set_data(xname, xdata)
            plot.data.set_data(yname, ydata)
        elif isinstance(patch, mpatches.Polygon):
            xy = patch.get_xy()
            plot.data.set_data(xname, xy[:, 0])
            plot.data.set_data(yname, xy[:, 1])
        else:
            is_data_set = False

        if is_data_set:
            plot.plot(
                (xname, yname),
                type="polygon",
                face_color=patch.get_facecolor(),
                edge_color=patch.get_edgecolor())

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

    @staticmethod
    def _setup_plot_tools(plot):
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(plot)
        plot.overlays.append(zoom)


def mpl2chaco(fig):
    """
    Convert a MPL figure object to Chaco figure instance
    """
    return MPLChaco(fig)
