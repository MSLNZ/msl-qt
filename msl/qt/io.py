"""
I/O helper functions.
"""
import os
import sys
import fnmatch

from . import QtWidgets, QtGui, QtCore, application, prompt

__all__ = (
    'get_drag_enter_paths',
    'get_icon',
    'icon_to_base64',
    'rescale_icon'
)


def get_icon(obj, size=None, mode=QtCore.Qt.KeepAspectRatio):
    """Convert the input object to a :class:`QtGui.QIcon`.

    Parameters
    ----------
    obj : :class:`object`
        The object to be converted to a :class:`QtGui.QIcon`. The data type of `obj` can be one of:

        * :class:`QtGui.QIcon`
        * :class:`QtGui.QPixmap`
        * :class:`QtGui.QImage`
        * `QtWidgets.QStyle.StandardPixmap <http://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum>`_:
          One of the built-in Qt pixmaps. Example::

              get_icon(QtWidgets.QStyle.SP_TitleBarMenuButton)
              get_icon(14)  # the QtWidgets.QStyle.SP_TrashIcon enum value

        * :class:`QtCore.QByteArray`: A `Base64 <https://en.wikipedia.org/wiki/Base64>`_
          representation of an encoded icon.

          See :func:`icon_to_base64`.

        * :class:`str`: The path to an icon file or an icon embedded in a DLL or EXE file.

          If `obj` is a path to an icon file and only the filename is specified then the
          directories in :obj:`sys.path` and :obj:`os.environ['PATH'] <os.environ>` are also
          used to search for the icon file. If `obj` refers to an icon in a Windows DLL/EXE
          file then `obj` is the path to the DLL/EXE file and the icon index separated by the
          ``|`` character.

          The following examples illustrate the various ways to request an icon by passing
          in a :class:`str` argument::

              # provide the full path to the icon file
              get_icon('D:/code/resources/icons/msl.png')
              get_icon('D:/code/resources/icons/photon.png')

              # insert the folder where the icons are located in to sys.path
              sys.path.insert(0, 'D:/code/resources/icons/')
              # so now only the filename needs to be specified to load the icon
              get_icon('msl.png')
              get_icon('photon.png')

              # load icon 23 from the Windows shell32.dll file
              get_icon('C:/Windows/System32/shell32.dll|23')

              # load icon 0 from the Windows explorer.exe file
              get_icon('C:/Windows/explorer.exe|0')

              # it is assumed that the DLL/EXE file is located in a default directory:
              #   - a DLL file in C:/Windows/System32/
              #   - an EXE file in C:/Windows/
              # so the following is a simplified way to load an icon in a DLL file
              get_icon('shell32|23')
              get_icon('imageres|1')
              get_icon('compstui|51')
              # and the following is a simplified way to load an icon in an EXE file
              get_icon('explorer|0')

    size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`, optional
        Rescale the icon to the specified `size`.
        If the value is :obj:`None` then do not rescale the icon.
        If an :class:`int` then set the width and the height to be the `size` value.
        If a :class:`float` then a scaling factor.
        If a :class:`tuple` then the (width, height) values.
    mode : `QtCore.Qt.AspectRatioMode <https://doc.qt.io/qt-5/qt.html#AspectRatioMode-enum>`_, optional
        How to maintain the aspect ratio if rescaling. The default mode is to keep the aspect ratio.

    Returns
    -------
    :class:`QtGui.QIcon`
        The input object converted to a :class:`QtGui.QIcon`.

    Raises
    ------
    :exc:`IOError`
        If the icon cannot be found.
    :exc:`TypeError`
        If the data type of `obj` or `size` is not supported.

    Example
    -------
    To view the standard icons that come with Qt and that come with Windows run:

    >>> from msl.examples.qt import ShowStandardIcons
    >>> ShowStandardIcons() # doctest: +SKIP
    """
    _icon = None
    if isinstance(obj, QtGui.QIcon):
        _icon = obj
    elif isinstance(obj, str):
        if '|' in obj:  # then loading an icon from a Windows DLL/EXE file
            _icon = get_icon(icon_to_base64(obj))
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
                raise IOError("Cannot find icon file '{}'".format(obj))
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        app = application()
        _icon = QtGui.QIcon(app.style().standardIcon(obj))
    elif isinstance(obj, int):
        std_icons = [value for name, value in vars(QtWidgets.QStyle).items() if name.startswith('SP_')]
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
    return QtGui.QIcon(rescale_icon(_icon, size, mode))


def icon_to_base64(icon=None, size=None, mode=QtCore.Qt.KeepAspectRatio, fmt='PNG'):
    """Convert the icon to a :class:`QtCore.QByteArray` encoded as Base64_.

    This function is useful if you want to save icons in a database, use it in a
    data URI scheme_, or if you want to use icons in your GUI and rather than loading
    icons from a file on the hard disk you define your icons in a Python module as
    Base64_ variables. Loading the icons from the hard disk means that you must also
    distribute the icons with your Python code if you share your code.

    .. _Base64: https://en.wikipedia.org/wiki/Base64
    .. _scheme: https://en.wikipedia.org/wiki/Data_URI_scheme

    Parameters
    ----------
    icon : :class:`object`, optional
        An icon with a data type that is handled by :func:`get_icon`. If :obj:`None`
        then a dialog window is created to allow the user to select an icon file
        that is saved in a folder.
    size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`, optional
        Rescale the icon to the specified `size` before converting it to Base64_.
        If the value is :obj:`None` then do not rescale the icon.
        If an :class:`int` then set the width and the height to be the `size` value.
        If a :class:`float` then a scaling factor.
        If a :class:`tuple` then the (width, height) values.
    mode : QtCore.Qt.AspectRatioMode_, optional
        How to maintain the aspect ratio if rescaling. The default mode is to keep the aspect ratio.
    fmt : :class:`str`, optional
        The icon format to use when converting. The supported values are: ``BMP``,
        ``JPG``, ``JPEG`` and ``PNG``.

    Returns
    -------
    :class:`QtCore.QByteArray`
        The Base64_ representation of the icon.

    Raises
    ------
    :exc:`IOError`
        If the icon file cannot be found.
    :exc:`ValueError`
        If the icon format, `fmt`, to use for converting is not supported.
    """
    fmt = fmt.upper()
    ALLOWED_FORMATS = ['BMP', 'JPG', 'JPEG', 'PNG']
    if fmt not in ALLOWED_FORMATS:
        raise ValueError('Invalid format {}. Must be one of: {}'.format(fmt, ', '.join(ALLOWED_FORMATS)))

    if isinstance(icon, str) and '|' in icon:
        # extract an icon from a Windows DLL/EXE file
        # uses ctypes and the .NET Framework to convert the icon to base64
        # import here in case pythonnet is not installed
        import clr
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
            err_msg = "Cannot find DLL/EXE file '{}'".format(s[0])
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
            # Check if the icon index is valid
            max_index = shell32.ExtractIconExA(path_ptr, -1, ctypes.c_void_p(), ctypes.c_void_p(), 0) - 1
            if icon_index > max_index:
                msg = 'Requested icon {}, the maximum icon index allowed is {}'.format(icon_index, max_index)
            else:
                msg = "ExtractIconExA: Cannot extract icon {} from '{}'".format(icon_index, path)
            raise IOError(msg)

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

    # ensure that a QApplication exists in order to access Qt classes
    app = application()

    if icon is None:
        title = 'Select an icon file to convert to Base64'
        filters = {'Images': ('bmp', 'jpg', 'jpeg', 'png'), 'All files': '*'}
        icon = prompt.filename(title=title, filters=filters)
        if icon is None:
            return QtCore.QByteArray()
        icon = str(icon)

    icon = get_icon(icon)
    try:
        default_size = icon.availableSizes()[-1]  # use the largest size as the default size
    except IndexError:
        prompt.critical('Invalid icon file.')
        return QtCore.QByteArray()

    pixmap = icon.pixmap(default_size)
    if size is not None:
        pixmap = rescale_icon(pixmap, size, mode)

    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, fmt)
    buffer.close()
    return array.toBase64()


def get_drag_enter_paths(event, pattern=None):
    """Returns the list of file paths from a :class:`QtGui.QDragEnterEvent`.

    Parameters
    ----------
    event : :class:`QtGui.QDragEnterEvent`
        A drag-enter event.
    pattern : :class:`str`, optional
        Include only the file paths that match the `pattern`.

        See :func:`fnmatch.fnmatch`.

    Returns
    -------
    :class:`list` of :class:`str`
        The list of file paths.
    """
    if event.mimeData().hasUrls():
        urls = event.mimeData().urls()
        paths = [str(url.toLocalFile()) for url in urls if url.isValid() and url.scheme() == 'file']
        if pattern is None:
            return paths
        return fnmatch.filter(paths, pattern)
    return []


def rescale_icon(icon, size, mode=QtCore.Qt.KeepAspectRatio):
    """Rescale an icon.

    Parameters
    ----------
    icon : :class:`object`
        Any object that is supported by :func:`~msl.qt.io.get_icon`.
    size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`
        Rescale the icon to the specified `size`.
        If the value is :obj:`None` then do not rescale the icon.
        If an :class:`int` then set the width and the height to be the `size` value.
        If a :class:`float` then a scaling factor.
        If a :class:`tuple` then the (width, height) values.
    mode : QtCore.Qt.AspectRatioMode_, optional
        How to maintain the aspect ratio if rescaling. The default mode is to keep the aspect ratio.

    Returns
    -------
    :class:`QtGui.QPixmap`
        The rescaled icon.
    """
    if isinstance(icon, QtGui.QIcon):
        try:
            max_size = icon.availableSizes()[-1]
        except IndexError:
            max_size = QtCore.QSize(16, 16)
        pixmap = icon.pixmap(max_size)
    elif isinstance(icon, QtGui.QPixmap):
        pixmap = icon
    else:
        return rescale_icon(get_icon(icon), size, mode)

    if size is None:
        return pixmap

    default_size = pixmap.size()
    if isinstance(size, int):
        size = QtCore.QSize(size, size)
    elif isinstance(size, float):
        size = QtCore.QSize(int(default_size.width()*size), int(default_size.height()*size))
    elif isinstance(size, (list, tuple)):
        if len(size) == 0:
            size = default_size
        elif len(size) == 1:
            size = QtCore.QSize(size[0], size[0])
        else:
            size = QtCore.QSize(size[0], size[1])
    elif not isinstance(size, QtCore.QSize):
        raise TypeError('Unsupported "size" data type of "{}"'.format(type(size)))

    if (size.width() != default_size.width()) or (size.height() != default_size.height()):
        pixmap = pixmap.scaled(size, aspectRatioMode=mode)

    return pixmap
