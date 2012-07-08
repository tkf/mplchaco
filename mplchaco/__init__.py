from chaco.api import ArrayPlotData, Plot, GridPlotContainer
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import View, Item


class MPLChaco(HasTraits):

    plot = Instance(GridPlotContainer)

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
        container = GridPlotContainer(shape=(1, len(axes)))
        pd = ArrayPlotData()

        for (i, ax) in enumerate(axes):
            x_name = 'x_{0}_{1}'.format
            y_name = 'y_{0}_{1}'.format
            lines = ax.get_lines()
            for (j, line) in enumerate(lines):
                pd.set_data(x_name(i, j), line.get_xdata())
                pd.set_data(y_name(i, j), line.get_ydata())

            plot = Plot(pd)

            for j in range(len(lines)):
                plot.plot((x_name(i, j), y_name(i, j)),
                          line_width=3.0)

            container.add(plot)

        return container


def mpl2chaco(fig):
    """
    Convert a MPL figure object to Chaco figure instance

    Typical usage is calling ``.configure_traits()`` right after
    making the instance::

        mpl2chaco(fig).configure_traits()

    """
    return MPLChaco(fig)
