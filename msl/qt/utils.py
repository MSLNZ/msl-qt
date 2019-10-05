"""
General helper functions.
"""
from . import QtGui


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
