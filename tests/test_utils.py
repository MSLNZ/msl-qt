import os.path
from tempfile import NamedTemporaryFile

import pytest

from msl.qt import Qt
from msl.qt import QtCore
from msl.qt import QtGui
from msl.qt import QtWidgets
from msl.qt import utils


def test_screen_geometry():
    # just check that these don't raise an exception
    assert isinstance(utils.screen_geometry(), QtCore.QRect)
    assert isinstance(utils.screen_geometry(QtWidgets.QLabel()), QtCore.QRect)
    assert isinstance(utils.screen_geometry(QtWidgets.QLabel(parent=QtWidgets.QLabel())), QtCore.QRect)


def test_drag_enter_paths():
    mime = QtCore.QMimeData()

    event = QtGui.QDragEnterEvent(QtCore.QPoint(0, 0), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)
    paths = utils.drag_drop_paths(event)
    assert len(paths) == 0

    url1 = QtCore.QUrl('/path/to/image.jpeg')
    url1.setScheme('file')

    url2 = QtCore.QUrl('')  # does not pass the isValid() and scheme() == 'file' checks

    url3 = QtCore.QUrl('/path/to/image.jpeg')
    url3.setScheme('ftp')  # does not pass the scheme() == 'file' check

    url4 = QtCore.QUrl('/path/to/image.png')
    url4.setScheme('file')

    url5 = QtCore.QUrl('/path/to/image2.jpg')
    url5.setScheme('file')

    mime.setUrls([url1, url2, url3, url4, url5])
    event = QtGui.QDragEnterEvent(QtCore.QPoint(0, 0), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)

    paths = utils.drag_drop_paths(event)
    assert len(paths) == 3
    assert '/path/to/image.jpeg' in paths
    assert '/path/to/image.png' in paths
    assert '/path/to/image2.jpg' in paths

    paths = utils.drag_drop_paths(event, pattern='*.jp*g')
    assert len(paths) == 2
    assert '/path/to/image.jpeg' in paths
    assert '/path/to/image2.jpg' in paths

    paths = utils.drag_drop_paths(event, pattern='*.png')
    assert len(paths) == 1
    assert '/path/to/image.png' in paths


def test_save_image():
    file = NamedTemporaryFile()

    # no file extension is specified so cannot determine the image format
    with pytest.raises(OSError, match=r'Cannot save image'):
        utils.save_image(QtWidgets.QWidget(), file.name)

    path = file.name+'.png'
    assert not os.path.isfile(path)
    pixmap = utils.save_image(QtWidgets.QWidget(), path)
    assert os.path.isfile(path)
    assert isinstance(pixmap, QtGui.QPixmap)

    file.close()
