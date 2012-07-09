================================
 Matplotlib to Chaco converter.
================================

Usage::

    from mplchaco import mpl2chaco
    mpl2chaco(fig).configure_traits()

Note that when using from IPython, make sure execute ``%gui wx``
**before** importing `mplchaco`.  Otherwise, opening Chaco window
blocks IPython.

See `demo <https://github.com/tkf/mplchaco/wiki/Demo>`_.


Why?
====

IPython's inline plot in Qt console and Notebook frontend is great,
but it does not support interactive stuff such as zooming, so you
would like to change Matplotlib backend to something that support GUI.
However, Matplotlib does not support changing GUI.

This Python module converts Matplotlib figure into Chaco figure so
that you can have inline plot in IPython and also GUI frontend to play
with data!
