"""
General helper functions.
"""
import logging
from math import (
    isinf,
    isnan,
    floor,
    log10,
    fabs,
)

from .constants import SI_PREFIX_MAP
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


def number_to_si(number):
    """Convert a number to be represented with an SI prefix.

    The hecto (h), deka (da), deci (d) and centi (c) prefixes are not used.

    Parameters
    ----------
    number : :class:`int` or :class:`float`
        The number to convert.

    Returns
    -------
    :class:`float`
        The number rescaled.
    :class:`str`
        The SI prefix.

    Examples
    --------
    >>> number_to_si(0.0123)
    (12.3, 'm')
    >>> number_to_si(123456.789)
    (123.456789, 'k')
    >>> number_to_si(712.123e14)
    (71.2123, 'P')
    >>> number_to_si(1.23e-13)
    (123.0, 'f')
    """
    if isnan(number) or isinf(number) or number == 0:
        return number, ''
    n = int(floor(log10(fabs(number)) / 3))
    if n == 0:
        return number, ''
    if n > 8 or n < -8:
        raise ValueError('The number {} cannot be expressed with an SI prefix'.format(number))
    return number * 10 ** (-3 * n), SI_PREFIX_MAP[n]


def si_to_number(string):
    """Convert a string with an SI prefix to a number.

    Parameters
    ----------
    string : :class:`str`
        The string to convert.

    Returns
    -------
    :class:`float`
        The number.

    Examples
    --------
    >>> si_to_number('12.3m')
    0.0123
    >>> si_to_number('123.456789k')
    123456.789
    >>> si_to_number('71.2123P')
    7.12123e+16
    >>> si_to_number('123f')
    1.23e-13
    """
    string_ = string.strip()
    if not string_ or string_ == 'nan' or string_.endswith('inf'):
        # let the builtin implementation handle an empty string
        # nan would be mistaken for the nano (n) SI prefix
        # +/-inf would be mistaken for the femto (f) SI prefix
        return float(string_)

    prefix = string_[-1]
    if prefix == 'u':
        prefix = '\u00b5'
    for n, value in SI_PREFIX_MAP.items():
        if prefix == value:
            return float(string_[:-1]) * 10 ** (3 * n)

    return float(string_)
