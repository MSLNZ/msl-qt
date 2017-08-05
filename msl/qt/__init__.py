"""
General convenience functions and package constants.
"""
import os
import sys
from collections import namedtuple

from PyQt5 import QtWidgets, QtGui, QtCore

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.1.0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""


def application(args=None):
    """Returns the QApplication instance (creating one if necessary).

    Parameters
    ----------
    args : :obj:`list` of :obj:`str`
        A list of arguments to initialize the QApplication.
        If :obj:`None` then uses :obj:`sys.argv`.

    Returns
    -------
    :obj:`QApplication`
        The QApplication instance.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv if args is None else args)

        # use a default *MSL logo* as the app icon
        logo = 'iVBORw0KGgoAAAANSUhEUgAAACgAAABCCAYAAAAlkZRRAAAACXBIWXMAAAsTAAALEwEAmpwYAAABpElEQVR' \
               'oge2ZT07CQBSHf29kLXKOsnApBEx7DAl3sT2BZzAx6C1ahYBLFzRxyQ1Q12SeiwoSQonjzMiLmW9Fh+nMlz' \
               'ft/HkFhEOuGnofRLz+3RyVztpVrhryhXjBhu8OlsN2DADQ/NYalS+m93sXVJpzACBGASAxvt+1kGuCoC3On' \
               'kGXc9824iMYBG0JgrZ4X0lMWe+KtKKkdTcvQgT3sRy2Y6URr6+bo3laV/cogpUcX28VpbV1vdtY4iyCYcsv' \
               'lSBoi7j94G474iMoXjDMg7YEQVvEC4rPDxq/xctBdH7CuAGA0/vSOBlkivk0o+iMNcfuVWq6+6uOfot4wdo' \
               'h/riKcqbqYOMrMfQTxEdQvKC4/eAu4iMYBG0RL9gAthd6yg4lco6B+AiKFzSfB1erBVQj8+CyF2PB1sPrAg' \
               'fyea4RP8TiBb+GmDIA0ArF5h/CLUCPx5AKuISAsJJYIV4w8O8hAOj2O9VbTJRNn6YpAHT6nZxQnYun49nmQ' \
               'NTrXcSaKN8t37RRU85AMRvPEgDoXnZT8Pe3un31FXMymTzL/xwrXlA8n2MHdwPYAbB5AAAAAElFTkSuQmCC'
        app.setWindowIcon(icon(logo.encode()))

    return app


def icon(obj):
    """Convert the input object into a :obj:`QIcon`.

    Parameters
    ----------
    obj : :obj:`object`
        The object to be converted. The data type of `obj` can be one of:

        * :obj:`QIcon`
        * :obj:`QPixmap`
        * :obj:`QStyle.StandardPixmap`
        * :obj:`bytes`, :obj:`bytearray` or :obj:`QtCore.QByteArray`: See also :func:`image_to_bytes`
        * :obj:`str`: The path to an image file. If only the filename is specified
          then searches :obj:`sys.path` and :obj:`os.environ['PATH'] <os.environ>`
          for the image file.

    Returns
    -------
    :obj:`QIcon`
        The input object converted to a :obj:`QIcon`.

    Raises
    ------
    :obj:`FileNotFoundError`
        If `obj` is of type :obj:`str` and the file cannot be found.
    :obj:`TypeError`
        If the data type of `obj` is not supported.
    """
    if isinstance(obj, QtGui.QIcon):
        return obj
    elif isinstance(obj, str):
        if os.path.isfile(obj):
            return QtGui.QIcon(obj)
        search_paths = sys.path + os.environ['PATH'].split(os.pathsep)
        for path in search_paths:
            full_path = os.path.join(path, obj)
            if os.path.isfile(full_path):
                return QtGui.QIcon(full_path)
        raise FileNotFoundError("icon(obj): Cannot find '{}'".format(obj))
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        return QtGui.QIcon(application().style().standardIcon(obj))
    elif isinstance(obj, QtGui.QPixmap):
        return QtGui.QIcon(obj)
    elif isinstance(obj, (bytes, bytearray, QtCore.QByteArray)):
        img = QtGui.QImage()
        if not isinstance(obj, QtCore.QByteArray):
            img.loadFromData(QtCore.QByteArray.fromBase64(obj))
        else:
            img.loadFromData(obj)
        return QtGui.QIcon(QtGui.QPixmap.fromImage(img))
    else:
        raise TypeError("icon(obj): argument has unexpected type '{}'".format(type(obj).__name__))


def image_to_bytes(image, size=None, mode=QtCore.Qt.KeepAspectRatio, fmt='PNG'):
    """Return the byte representation of an image.

    This function is useful if you wanted to save images in a database or if you
    wanted to use images in your GUI and rather than loading the images from a
    file on the hard disk you define your images in a Python module as :obj:`bytes`
    objects. Loading the images from the hard disk means that you must also distribute
    the images with your Python code if you share your code.

    Parameters
    ----------
    image : :obj:`object`
        An image with a data type that is handled by :func:`icon`.
    size : :obj:`int`, :obj:`tuple` of :obj:`int` or :obj:`QSize`
        Rescale the image to the specified `size` before converting it to :obj:`bytes`.
        If :obj:`None` then do not rescale the image. If a :obj:`tuple` then the
        (width, height) values.
    mode : :obj:`Qt.AspectRatioMode`
        How to maintain the aspect ratio if rescaling. Allowed values are
        :obj:`Qt.IgnoreAspectRatio`, :obj:`Qt.KeepAspectRatio` or
        :obj:`Qt.KeepAspectRatioByExpanding`. The default mode is :obj:`Qt.KeepAspectRatio`.
    fmt : :obj:`str`
        The image format to use when converting.

    Returns
    -------
    :obj:`bytes`
        The byte representation of the image.
    """
    icon_ = icon(image)
    default_size = icon_.availableSizes()[0]
    if size is None:
        size = default_size
    elif isinstance(size, (int, float)):
        size = QtCore.QSize(size, size)
    elif isinstance(size, (list, tuple)):
        if len(size) == 0:
            size = default_size
        elif len(size) == 1:
            size = QtCore.QSize(size[0], size[0])
        else:
            size = QtCore.QSize(size[0], size[1])
    pixmap = icon_.pixmap(default_size).scaled(size, aspectRatioMode=mode)
    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, fmt)
    buffer.close()
    return bytes(array.toBase64())


from .loop_until_abort import LoopUntilAbort
