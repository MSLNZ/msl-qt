"""
Functions to convert objects.
"""
import os
import sys
import textwrap
from math import (
    isinf,
    isnan,
    floor,
    log10,
    fabs,
)

from .constants import SI_PREFIX_MAP
from . import (
    Qt,
    QtGui,
    QtCore,
    QtWidgets,
    application,
    binding,
)

__all__ = (
    'icon_to_base64',
    'rescale_icon',
    'number_to_si',
    'print_base64',
    'si_to_number',
    'to_qcolor',
    'to_qfont',
    'to_qicon',
)


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


def to_qicon(obj, *, size=None, aspect_mode=Qt.KeepAspectRatio):
    """Convert the input object to a :class:`QtGui.QIcon`.

    Parameters
    ----------
    obj
        The object to be converted to a :class:`QtGui.QIcon`. The data type of `obj` can be one of:

        * :class:`QtGui.QIcon`
        * :class:`QtGui.QPixmap`
        * :class:`QtGui.QImage`
        * `QtWidgets.QStyle.StandardPixmap <http://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum>`_:
          One of the built-in Qt pixmaps. Example::

              to_qicon(QtWidgets.QStyle.SP_TitleBarMenuButton)
              to_qicon(14)  # the QtWidgets.QStyle.SP_TrashIcon enum value

        * :class:`QtCore.QByteArray`: A `Base64 <https://en.wikipedia.org/wiki/Base64>`_
          representation of an encoded icon.

          See :func:`icon_to_base64`.

        * :class:`str`: The path to an icon file or an icon embedded in a DLL or EXE file.

          If `obj` is a path to an icon file and only the filename is specified then the
          directories in :data:`sys.path` and :data:`os.environ['PATH'] <os.environ>` are also
          used to search for the icon file. If `obj` refers to an icon in a Windows DLL/EXE
          file then `obj` is the path to the DLL/EXE file and the icon index separated by the
          ``|`` character.

          The following examples illustrate the various ways to request an icon by passing
          in a :class:`str` argument::

              # provide the full path to the icon file
              to_qicon('D:/code/resources/icons/msl.png')
              to_qicon('D:/code/resources/icons/photon.png')

              # insert the folder where the icons are located in to sys.path
              sys.path.insert(0, 'D:/code/resources/icons/')
              # so now only the filename needs to be specified to load the icon
              to_qicon('msl.png')
              to_qicon('photon.png')

              # load icon 23 from the Windows shell32.dll file
              to_qicon('C:/Windows/System32/shell32.dll|23')

              # load icon 0 from the Windows explorer.exe file
              to_qicon('C:/Windows/explorer.exe|0')

              # it is assumed that the DLL/EXE file is located in a default directory:
              #   - a DLL file in C:/Windows/System32/
              #   - an EXE file in C:/Windows/
              # so the following is a simplified way to load an icon in a DLL file
              to_qicon('shell32|23')
              to_qicon('imageres|1')
              to_qicon('compstui|51')
              # and the following is a simplified way to load an icon in an EXE file
              to_qicon('explorer|0')

    size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`, optional
        Rescale the icon to the specified `size`.
        If the value is :data:`None` then do not rescale the icon.
        If an :class:`int` then set the width and the height to be the `size` value.
        If a :class:`float` then a scaling factor.
        If a :class:`tuple` then the (width, height) values.
    aspect_mode : :attr:`QtCore.Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio if rescaling. The default mode is to keep the aspect ratio.

    Returns
    -------
    :class:`QtGui.QIcon`
        The input object converted to a :class:`QtGui.QIcon`.

    Raises
    ------
    IOError
        If the icon cannot be found.
    TypeError
        If the data type of `obj` or `size` is not supported.

    Example
    -------
    To view the standard icons that come with Qt and that come with Windows run::

    >>> from msl.examples.qt import ShowStandardIcons  # doctest: +SKIP
    >>> ShowStandardIcons()  # doctest: +SKIP
    """
    app = application()  # make sure that a QApplication exists
    _icon = None
    if isinstance(obj, QtGui.QIcon):
        _icon = obj
    elif isinstance(obj, str):
        if '|' in obj:  # then loading an icon from a Windows DLL/EXE file
            _icon = to_qicon(icon_to_base64(obj))
        elif os.path.isfile(obj):
            _icon = QtGui.QIcon(obj)
        else:
            search_paths = sys.path + os.environ['PATH'].split(os.pathsep)
            for path in search_paths:
                full_path = os.path.join(path, obj)
                if os.path.isfile(full_path):
                    _icon = QtGui.QIcon(full_path)
                    break
            if _icon is None:
                raise IOError('Cannot find icon file {!r}'.format(obj))
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        app = application()
        _icon = QtGui.QIcon(app.style().standardIcon(obj))
    elif isinstance(obj, int):
        std_icons = [value for name, value in vars(QtWidgets.QStyle).items() if name.startswith('SP_')]
        if binding.name == 'PyQt6':
            std_icons = [i.value for i in std_icons]
        if obj in std_icons:
            app = application()
            _icon = QtGui.QIcon(app.style().standardIcon(QtWidgets.QStyle.StandardPixmap(obj)))
        else:
            raise IOError('Invalid QStyle.StandardPixmap enum value of {}'.format(obj))
    elif isinstance(obj, QtGui.QPixmap):
        _icon = QtGui.QIcon(obj)
    elif isinstance(obj, QtGui.QImage):
        _icon = QtGui.QIcon(QtGui.QPixmap.fromImage(obj))
    elif isinstance(obj, (bytes, bytearray, QtCore.QByteArray)):
        img = QtGui.QImage()
        img.loadFromData(QtCore.QByteArray.fromBase64(obj))
        _icon = QtGui.QIcon(QtGui.QPixmap.fromImage(img))

    if _icon is None:
        raise TypeError('Icon object has unsupported data type {}'.format(type(obj)))

    if size is None:
        return _icon

    return QtGui.QIcon(rescale_icon(_icon, size, aspect_mode=aspect_mode))


def icon_to_base64(icon, *, fmt='png'):
    """Convert an icon to a :class:`QtCore.QByteArray` encoded as Base64_.

    This function is useful if you want to save icons in a database, use it in a
    data URI scheme_, or if you want to use icons in your GUI and rather than loading
    icons from a file on the hard disk you define your icons in a Python module as
    Base64_ variables. Loading the icons from the hard disk means that you must also
    distribute the icons with your Python code if you share your code.

    .. _Base64: https://en.wikipedia.org/wiki/Base64
    .. _scheme: https://en.wikipedia.org/wiki/Data_URI_scheme

    Parameters
    ----------
    icon
        An icon with a data type that is handled by :func:`to_qicon`.
    fmt : :class:`str`, optional
        The icon format to use when converting. The supported values are: ``BMP``,
        ``JPG``, ``JPEG`` and ``PNG``.

    Returns
    -------
    :class:`QtCore.QByteArray`
        The Base64_ representation of the icon.

    Raises
    ------
    IOError
        If the icon file cannot be found.
    ValueError
        If the icon format, `fmt`, to use for converting is not supported.
    """
    fmt = fmt.upper()
    if fmt not in ['BMP', 'JPG', 'JPEG', 'PNG']:
        raise ValueError('Invalid format {!r}. Must be one of: BMP, JPG, JPEG, PNG'.format(fmt))

    if isinstance(icon, str) and '|' in icon:
        # extract an icon from a Windows DLL/EXE file
        # uses ctypes and the .NET Framework to convert the icon to base64
        # import here in case pythonnet is not installed
        try:
            import clr
        except ImportError:
            raise ImportError('requires pythonnet, run: pip install pythonnet') from None
        import ctypes

        clr.AddReference('System.Drawing')
        from System.Drawing.Imaging import ImageFormat

        shell32 = ctypes.windll.shell32

        img_fmts = {
            'BMP':  ImageFormat.Bmp,
            'JPG':  ImageFormat.Jpeg,
            'JPEG': ImageFormat.Jpeg,
            'PNG':  ImageFormat.Png,
        }

        s = icon.split('|')
        path = s[0]
        icon_index = int(s[1])
        if icon_index < 0:
            raise IOError('The icon index must be >= 0')

        if not os.path.isfile(path):
            err_msg = 'Cannot find DLL/EXE file {!r}'.format(s[0])
            if os.path.split(path)[0]:  # then it wasn't just the filename that was specified
                raise IOError(err_msg)

            filename = os.path.splitext(os.path.basename(path))[0]
            path = 'C:/Windows/System32/{}.dll'.format(filename)
            if not os.path.isfile(path):
                path = 'C:/Windows/{}.exe'.format(filename)
                if not os.path.isfile(path):
                    raise IOError(err_msg)

        # extract the handle to the "large" icon
        path_ptr = ctypes.c_char_p(path.encode())
        handle_large = ctypes.c_int()
        res = shell32.ExtractIconExA(path_ptr, icon_index, ctypes.byref(handle_large), ctypes.c_void_p(), 1)
        if res != 1:
            max_index = shell32.ExtractIconExA(path_ptr, -1, ctypes.c_void_p(), ctypes.c_void_p(), 0) - 1
            raise IOError('Requested icon {}, the maximum icon index allowed is {}'.format(icon_index, max_index))

        # get the icon bitmap and convert it to base64
        handle = clr.System.Int32(handle_large.value)
        handle_ptr = clr.System.IntPtr.op_Explicit(handle)
        bmp = clr.System.Drawing.Bitmap.FromHicon(handle_ptr)
        stream = clr.System.IO.MemoryStream()
        bmp.Save(stream, img_fmts[fmt])
        base = QtCore.QByteArray(clr.System.Convert.ToBase64String(stream.GetBuffer()).encode())

        # clean up
        ctypes.windll.user32.DestroyIcon(handle_large)
        stream.Dispose()
        return base

    icon = to_qicon(icon)
    try:
        size = icon.availableSizes()[-1]  # use the largest size as the default size
    except IndexError:
        raise ValueError('Cannot determine a size of the QIcon.') from None

    pixmap = icon.pixmap(size)
    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, fmt)
    buffer.close()
    return array.toBase64()


def rescale_icon(icon, size, *, aspect_mode=Qt.KeepAspectRatio):
    """Rescale an icon.

    Parameters
    ----------
    icon
        Any object that is supported by :func:`to_qicon`.
    size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`
        Rescale the icon to the specified `size`.
        If an :class:`int` then set the width and the height to be the `size` value.
        If a :class:`float` then a scaling factor.
        If a :class:`tuple` then the (width, height) values.
    aspect_mode : :attr:`QtCore.Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio if rescaling. The default mode is to keep the aspect ratio.

    Returns
    -------
    :class:`QtGui.QPixmap`
        The rescaled icon.
    """
    if isinstance(icon, QtGui.QIcon):
        try:
            pixmap = icon.pixmap(icon.availableSizes()[-1])
        except IndexError:
            raise ValueError('Cannot automatically determine a size from the QIcon. Specify the size.') from None
    elif isinstance(icon, QtGui.QPixmap):
        pixmap = icon
    else:
        return rescale_icon(to_qicon(icon), size, aspect_mode=aspect_mode)

    default_size = pixmap.size()
    if isinstance(size, int):
        size = QtCore.QSize(size, size)
    elif isinstance(size, float):
        size = QtCore.QSize(int(default_size.width()*size), int(default_size.height()*size))
    elif isinstance(size, (list, tuple)):
        if len(size) != 2:
            raise ValueError('The size must be in the form (width, height)')
        size = QtCore.QSize(size[0], size[1])
    elif not isinstance(size, QtCore.QSize):
        raise TypeError('Unsupported "size" type of {!r}'.format(type(size)))

    if (size.width() != default_size.width()) or (size.height() != default_size.height()):
        # PyQt uses aspectRatioMode as a kwarg (this is what the Qt docs indicate) however
        # PySide uses aspectMode. Therefore, don't specify a kwarg but use a positional
        # argument since both APIs have the aspect ratio mode as the second argument if
        # the first argument is a QSize
        pixmap = pixmap.scaled(size, aspect_mode)

    return pixmap


def print_base64(icon, *, size=None, name='', line_width=80, file=None):
    """Print the Base64_ representation of an icon.

    Parameters
    ----------
    icon
        Passed to :func:`~msl.qt.convert.to_qicon`.
    size
        Passed to :func:`~msl.qt.convert.to_qicon`.
    name : :class:`str`, optional
        The name of the icon.
    line_width : :class:`int`, optional
        The maximum number of characters in a line.
    file : :term:`file-like object`
        Where to print the output. Default is :data:`sys.stdout`.

    Examples
    --------
    >>> print_base64(QtWidgets.QStyle.SP_MediaPlay, size=16)
    b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAk6AAAJOgHwZJJKAAA' \\
    b'AGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAJ9JREFUOI3djzEKwlAQRGcXO1' \\
    b'ERrIQw/i7gCTyOvZfyTtaBjaCVEH9n8V3bID/GpBKnnJ157AA/p6Io1kPy8m6QjCLyVFVWVXXvA' \\
    b'2jOdPdFSqkheRoFaGlL8hFCOHQFshMAzDLZCKA0s+uQD9qaA7iQPI8FAEBjZpsxgCgiOzNbAkjt' \\
    b'w6Sn6O5+rOt63xX4BLiZ2arvtdyEqaqW35T/RC/uTS/6P1rpJAAAAABJRU5ErkJggg=='

    >>> print_base64(QtWidgets.QStyle.SP_MediaPlay, name='my_play_icon')
    my_play_icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAk6' \\
                   b'AAAJOgHwZJJKAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48' \\
                   b'GgAAAaVJREFUWIXtlLFuE0EURc8bO8gyiiMhUYC8M2vHldPhz+AD6LDSp0FU' \\
                   b'QMsHUEJBAx+QjoKGKlIKhCihcDSzcYEsCylGXoTA+yhQUBSReLXebINPOzP3' \\
                   b'Hr0nDaxZs4Qoim5fZb657LDf718zxhw7595ba3cqF0jT1ABz4I4x5sBa+7zb' \\
                   b'7W5VJnAGUdUtERkuFoujOI53ASlD4NKQOI4bqjoBNs8dzYBj4H4I4cMqAnkn' \\
                   b'cJ4WsAO8s9a+arfbN6oW+CsiIvdqtdqo0+nsFckruoJ/8Q2YqOowSZKDvAKr' \\
                   b'TuAsm8C2iLxxzu07525VLXBKC7gLfHLOPR4MBhtVCwBsAC1VfTSdTo+iKNqu' \\
                   b'WgAAEVHglzEmu+hO/Yq6f/LnB30aQngGLKoUOAHe1uv1vdFoNFl2uUyBmYh8' \\
                   b'AYbe+8O8j8oQ+AGkIvLEe/8CuHDfZQsoMFPV/SzLHo7H469FQgoJiMgJEIBh' \\
                   b'COFjkYyiAt+BNMuyB0mSvF6l+JS8/4CKyAx42Wg0OmWVw5IJNJvNbD6fXwcO' \\
                   b'RWTXe/+5rOLc9Hq9m5WXrlnzX/EbbYB/8sxND3cAAAAASUVORK5CYII='
    """
    b64 = icon_to_base64(to_qicon(icon, size=size)).data()
    if name:
        name += ' = '
    indent = ' ' * len(name)
    # the 5 comes from the additional characters that are printed: b'' \
    lines = textwrap.wrap(b64.decode(), width=line_width - len(name) - 5)
    for i, line in enumerate(lines):
        line = line.encode()
        if i == 0:
            print('{}{} \\'.format(name, line), file=file)
        elif i == len(lines) - 1:
            print('{}{}'.format(indent, line), file=file)
        else:
            print('{}{} \\'.format(indent, line), file=file)
