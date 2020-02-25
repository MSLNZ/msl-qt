"""
General helper functions.
"""
import logging

from . import (
    QtGui,
    Qt,
    QtWidgets,
    application,
)

logger = logging.getLogger(__package__)


def to_qfont(*args):
    """Convert the input argument(s) into a :class:`QtGui.QFont`.

    Parameters
    ----------
    args
        The argument(s) to convert to a :class:`QtGui.QFont`.

        * If :class:`int` or :class:`float` then the point size.
        * If :class:`str` then the font family name.
        * If :class:`QtGui.QFont` then returns a copy.
        * If multiple arguments then

          - family name, point size

          - family name, point size, weight

          - family name, point size, weight, is italic

    Returns
    -------
    :class:`QtGui.QFont`
        The input argument(s) converted to a :class:`QtGui.QFont`.

    Examples
    --------
    >>> font = to_qfont(48)
    >>> font = to_qfont(23.4)
    >>> font = to_qfont('Papyrus')
    >>> font = to_qfont('Ariel', 16)
    >>> font = to_qfont('Ariel', 16, QtGui.QFont.Bold)
    >>> font = to_qfont('Ariel', 16, 50, True)
    """

    def parse_tuple(a):
        if not isinstance(a[0], str):
            raise TypeError('The first argument must be the family name (as a string)')

        if len(a) == 1:
            return QtGui.QFont(a[0])
        elif len(a) == 2:
            return QtGui.QFont(a[0], pointSize=int(a[1]))
        elif len(a) == 3:
            return QtGui.QFont(a[0], pointSize=int(a[1]), weight=int(a[2]))
        else:
            return QtGui.QFont(a[0], pointSize=int(a[1]), weight=int(a[2]), italic=bool(a[3]))

    if not args:
        return QtGui.QFont()
    elif len(args) == 1:
        value = args[0]
        if isinstance(value, QtGui.QFont):
            return QtGui.QFont(value)
        elif isinstance(value, int):
            f = QtGui.QFont()
            f.setPointSize(value)
            return f
        elif isinstance(value, float):
            f = QtGui.QFont()
            f.setPointSizeF(value)
            return f
        elif isinstance(value, str):
            return QtGui.QFont(value)
        elif isinstance(value, (list, tuple)):
            return parse_tuple(value)
        else:
            raise TypeError('Cannot create a QFont from {!r}'.format(value))
    else:
        return parse_tuple(args)


def to_qcolor(*args):
    """Convert the input argument(s) into a :class:`QtGui.QColor`.

    Parameters
    ----------
    args
        The argument(s) to convert to a :class:`QtGui.QColor`.

        * R, G, B, [A] :math:`\\rightarrow` values can be :class:`int` 0-255 or :class:`float` 0.0-1.0
        * (R, G, B, [A]) :math:`\\rightarrow` :class:`tuple` of :class:`int` 0-255 or :class:`float` 0.0-1.0
        * :class:`int` or :obj:`QtCore.Qt.GlobalColor` :math:`\\rightarrow` a pre-defined enum value
        * :class:`float` :math:`\\rightarrow` a greyscale value between 0.0-1.0
        * :class:`QtGui.QColor` :math:`\\rightarrow` returns a copy
        * :class:`str` :math:`\\rightarrow` see `here <https://doc.qt.io/qt-5/qcolor.html#setNamedColor>`_ for examples

    Returns
    -------
    :class:`QtGui.QColor`
        The input argument(s) converted to a :class:`QtGui.QColor`.

    Examples
    --------
    >>> color = to_qcolor(48, 127, 69)
    >>> color = to_qcolor((48, 127, 69))
    >>> color = to_qcolor(0.5)  # greyscale -> (127, 127, 127, 255)
    >>> color = to_qcolor(0.2, 0.45, 0.3, 0.5)
    >>> color = to_qcolor('red')
    >>> color = to_qcolor(Qt.darkBlue)
    >>> color = to_qcolor(15)  # 15 == Qt.darkBlue
    """
    if not args:
        return QtGui.QColor()

    def ensure_255(value):
        # ensure that a value is between 0 and 255
        if value <= 1 and isinstance(value, float):
            value = int(value * 255)
        return min(max(value, 0), 255)

    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, str):
            return QtGui.QColor(arg)
        elif isinstance(arg, QtGui.QColor):
            return QtGui.QColor(arg)
        elif isinstance(arg, (list, tuple)):
            return QtGui.QColor(*tuple(ensure_255(v) for v in arg))
        elif isinstance(arg, float):
            val = ensure_255(arg)
            return QtGui.QColor(val, val, val)
        elif isinstance(arg, (int, Qt.GlobalColor)):
            return QtGui.QColor(Qt.GlobalColor(arg))
        else:
            raise TypeError('Cannot convert {!r} to a QColor'.format(args))
    else:
        return QtGui.QColor(*tuple(ensure_255(v) for v in args))


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
