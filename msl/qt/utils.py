"""
General functions.
"""
import fnmatch
import logging

from . import QtGui
from . import application

__all__ = (
    'drag_drop_paths',
    'save_image',
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


def save_image(widget, path, *, quality=-1):
    """Save a widget to an image file.

    Parameters
    ----------
    widget : :class:`QtWidgets.QWidget`
        The widget to save as an image.
    path : :class:`str`
        The file path to save the image to. The image format is chosen
        based on the file extension.
    quality : :class:`int`, optional
        The quality factor. Must be in the range 0 to 100 or -1. Specify 0 to
        obtain small compressed files, 100 for large uncompressed files, and
        -1 (the default) to use the default settings.

    Returns
    -------
    :class:`QtGui.QPixmap`
        The `widget` as a pixmap object.
    """
    pixmap = QtGui.QPixmap(widget.size())
    widget.render(pixmap)
    success = pixmap.toImage().save(path, quality=quality)
    if not success:
        raise OSError(f'Cannot save image to {path!r}')
    return pixmap


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

    # then just ignore the QWidget
    return screen_geometry()
