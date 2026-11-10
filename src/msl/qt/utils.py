"""General functions."""

from __future__ import annotations

import fnmatch
import logging
from typing import TYPE_CHECKING

from ._qt import QtCore, QtGui, application

if TYPE_CHECKING:
    from pathlib import Path

    from ._qt import QtWidgets

__all__: list[str] = [
    "drag_drop_paths",
    "save_image",
    "screen_geometry",
]

logger = logging.getLogger(__package__)


def drag_drop_paths(event: QtGui.QDragEnterEvent | QtGui.QDropEvent, *, pattern: str | None = None) -> list[str]:
    """Returns the list of file paths from a drag-enter or drop event.

    Args:
        event: A drag-enter event or a drop event.
        pattern: Include only the file paths that match the `pattern`.
            For example, to only include JPEG or JPG image files use `"*.jp*g"`.
            See [fnmatch][fnmatch.fnmatch] for more details.

    Returns:
        The list of file paths.
    """
    data = event.mimeData()
    if data and data.hasUrls():
        urls = data.urls()
        paths = [url.toLocalFile() for url in urls if url.isValid() and url.scheme() == "file"]
        if pattern is None:
            return paths
        return fnmatch.filter(paths, pattern)
    return []


def save_image(widget: QtWidgets.QWidget, path: str | Path, *, quality: int = -1) -> QtGui.QPixmap:
    """Save a widget to an image file.

    Args:
        widget: The widget to save as an image.
        path: The file path to save the image to. The image format is chosen
            based on the file extension.
        quality: The quality factor. Must be in the range 0 to 100 or -1.
            Specify 0 to obtain small compressed files, 100 for large uncompressed
            files and -1 (the default) to use the default compression value.

    Returns:
        The `widget` as a pixmap object.
    """
    pixmap = QtGui.QPixmap(widget.size())
    widget.render(pixmap)
    success = pixmap.toImage().save(str(path), quality=quality)
    if not success:
        msg = f"Cannot save image to '{path}'"
        raise OSError(msg)
    return pixmap


def screen_geometry(widget: QtWidgets.QWidget | None = None) -> QtCore.QRect:
    """Get the geometry of a desktop screen.

    Args:
        widget: Get the geometry of the screen that contains this widget.

    Returns:
        If a `widget` is specified then the geometry of the screen that contains
            the `widget` is returned, otherwise the geometry of the primary screen
            (i.e., the screen where the main widget resides).
    """
    screen: QtGui.QScreen | None
    if widget is None:
        screen = application().primaryScreen()
    else:
        point = widget.mapToGlobal(QtCore.QPoint(0, 0))
        screen = application().screenAt(point)

    if screen is None:
        return QtCore.QRect()
    return screen.geometry()
