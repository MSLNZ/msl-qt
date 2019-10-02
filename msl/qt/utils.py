"""
General helper functions.
"""
from . import QtGui


def to_qfont(font):
    """Convert the input argument into a :class:`QtGui.QFont` object.

    Parameters
    ----------
    font : :class:`int`, :class:`float`, :class:`str` or :class:`tuple`
        The value to convert to a :class:`QtGui.QFont`.

        * If :class:`int` or :class:`float` then the point size.
        * If :class:`str` then the font family name.
        * If :class:`tuple` then (family name, point size).

    Returns
    -------
    :class:`QtGui.QFont`
        The input `value` converted to a :class:`QtGui.QFont` object.
    """
    if isinstance(font, QtGui.QFont):
        return font
    elif isinstance(font, int):
        f = QtGui.QFont()
        f.setPointSize(font)
        return f
    elif isinstance(font, float):
        f = QtGui.QFont()
        f.setPointSizeF(font)
        return f
    elif isinstance(font, str):
        return QtGui.QFont(font)
    elif isinstance(font, (tuple, list)):
        if len(font) < 2:
            raise ValueError('The font must be a (family name, point size) tuple')
        return QtGui.QFont(font[0], pointSize=int(font[1]))
    else:
        raise TypeError('Must specify a QFont object')
