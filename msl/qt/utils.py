"""
General functions.
"""
import fnmatch
import logging

from . import application, QtWidgets

__all__ = (
    'drag_drop_paths',
    'screen_geometry',
)

logger = logging.getLogger(__package__)


def drag_drop_paths(event, *, pattern=None):
    """Returns the list of file paths from a drag-enter or drop event.

    Parameters
    ----------
    event : :class:`QtGui.QDragEnterEvent` or :class:`QtGui.QDropEvent`
        A drag-enter or drop event.
    pattern : :class:`str`, optional
        Include only the file paths that match the `pattern`. For example,
        to only include JPEG or JPG image files use ``'*.jp*g'``.

        See :func:`fnmatch.fnmatch`.

    Returns
    -------
    :class:`list` of :class:`str`
        The list of file paths.
    """
    if event.mimeData().hasUrls():
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls if url.isValid() and url.scheme() == 'file']
        if pattern is None:
            return paths
        return fnmatch.filter(paths, pattern)
    return []


def screen_geometry(widget=None):
    """Get the geometry of a desktop screen.

    Parameters
    ----------
    widget : :class:`QtWidgets.QWidget`, optional
        Get the geometry of the screen that contains this widget.

    Returns
    -------
    :class:`QtCore.QRect`
        If a `widget` is specified then the geometry of the screen that
        contains the `widget` otherwise returns the geometry of the primary
        screen (i.e., the screen where the main widget resides).
    """
    if widget is None:
        return application().primaryScreen().geometry()

    handle = widget.window().windowHandle()
    if handle is not None:
        return handle.screen().geometry()

    parent = widget.parentWidget()
    if parent is not None:
        handle = parent.window().windowHandle()
        if handle is not None:
            return handle.screen().geometry()

    # the Qt docs say that this function is deprecated
    return QtWidgets.QDesktopWidget().availableGeometry(widget)
