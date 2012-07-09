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
from chaco.shell.plot_maker import marker_trans, line_trans
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
    """
    A list of `matplotlib.transforms.Bbox`.
    """

    def add_plot(self, plot, box):
        """
        Add a plot and its location information to this container.

        Parameters
        ----------

        plot : chaco.api.Plot
            Chaco plot object.
        box : matplotlib.transforms.Bbox
            Use ``ax.get_position()`` to get this value.

        """
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
        """
        Initialize `self.plot`.

        Traits package magically sets `self.plot` to the returned
        value of this function.

        See also:

        * http://docs.enthought.com/traits/traits_user_manual/advanced.html
          #dynamic-initialization

        """
        fig = self._fig
        axes = fig.get_axes()
        container = RelativeLocationPlotContainer()
        pd = ArrayPlotData()

        def do_plot(plot, func, i, sources):
            for (j, src) in enumerate(sources):
                suffix = "{0}_{1}".format(i, j)
                func(plot, suffix, src)

        for (i, ax) in enumerate(axes):
            plot = Plot(pd)

            do_plot(plot, self._plot_from_line,       i, ax.get_lines())
            do_plot(plot, self._plot_from_collection, i, ax.collections)
            do_plot(plot, self._plot_from_patch,      i, ax.patches)

            self._migrate_plot_attributes(ax, plot)
            self._setup_plot_tools(plot)
            container.add_plot(plot, ax.get_position())

        return container

    @staticmethod
    def _plot_from_line(plot, suffix, line):
        """
        Plot lines in Chaco Plot object `plot` given MPL Line2D `line`.
        """
        xname = "lx_{0}".format(suffix)
        yname = "ly_{0}".format(suffix)
        plot.data.set_data(xname, line.get_xdata())
        plot.data.set_data(yname, line.get_ydata())

        ls = line.get_linestyle()
        if ls != "None":
            plot.plot(
                (xname, yname),
                line_style=line_trans.get(ls, "solid"),
                color=colorConverter.to_rgba(line.get_color()))

        marker = line.get_marker()
        if marker != "None":
            chaco_marker = marker_trans.get(marker, "circle")
            if chaco_marker == 'down triangle':
                # Workaround the bug in Chaco shell.
                # (https://github.com/enthought/chaco/issues/70)
                chaco_marker = 'inverted_triangle'
            plot.plot(
                (xname, yname),
                type="scatter",
                marker=chaco_marker,
                color=colorConverter.to_rgba(line.get_markerfacecolor()))

    @staticmethod
    def _plot_from_collection(plot, suffix, collection):
        """
        Plot in Chaco Plot object `plot` given MPL Collection `collection`.
        """
        xname = "cx_{0}".format(suffix)
        yname = "cy_{0}".format(suffix)
        if isinstance(collection, mcoll.PathCollection):
            # then assume it is the data plotted via Axes.scatter
            ofs = collection.get_offsets()
            plot.data.set_data(xname, ofs[:, 0])
            plot.data.set_data(yname, ofs[:, 1])
            plot.plot(
                (xname, yname),
                type="scatter",
                color=tuple(*collection.get_facecolor()))
            # FIXME: treat marker type

            # Note: marker type cannot be retrieved now because it is
            # already converted into a path.  A right way to do it is
            # to generate something like a custom marker based on the
            # path.

    @staticmethod
    def _plot_from_patch(plot, suffix, patch):
        """
        Plot in Chaco Plot object `plot` given MPL Patch `patche`.
        """
        xname = "px_{0}".format(suffix)
        yname = "py_{0}".format(suffix)

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
