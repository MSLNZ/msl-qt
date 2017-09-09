"""
I/O helper functions.
"""
import os
import sys
import fnmatch

from PyQt5 import QtWidgets, QtGui, QtCore

from msl.qt import application, prompt

__all__ = ['get_drag_enter_paths', 'get_icon', 'image_to_base64', 'rescale_image']


def get_icon(obj, size=None, mode=QtCore.Qt.KeepAspectRatio):
    """Convert the input object to a :obj:`~QtGui.QIcon`.

    Parameters
    ----------
    obj : :obj:`object`
        The object to be converted to a :obj:`~QtGui.QIcon`. The data type of `obj` can be one of:

        * :obj:`~QtGui.QIcon`
        * :obj:`~QtGui.QPixmap`
        * :obj:`~QtGui.QImage`
        * :obj:`QStyle.StandardPixmap` or :obj:`int`:
          See `StandardPixmap <http://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum>`_
          for the possible enum values. Example::

              get_icon(QStyle.SP_TitleBarMenuButton)
              get_icon(14)  # the QStyle.SP_TrashIcon enum value

        * :class:`~QtCore.QByteArray`: A `Base64 <https://en.wikipedia.org/wiki/Base64>`_
          representation of an encoded image.

          See :func:`image_to_base64`.

        * :obj:`str`: The path to an image file or an icon embedded in a DLL or EXE file.

          If `obj` is a path to an image file and only the filename is specified then the
          directories in :obj:`sys.path` and :obj:`os.environ['PATH'] <os.environ>` are also
          used to search for the image file. If `obj` refers to an icon in a Windows DLL/EXE
          file then `obj` is the path to the DLL/EXE file and the icon index separated by the
          ``|`` character.

          The following examples illustrate the various ways to request an icon by passing
          in a :obj:`str` argument::

              # provide the full path to image files
              get_icon('D:/code/resources/icons/msl.png')
              get_icon('D:/code/resources/icons/photon.png')

              # insert the folder where the icons are located into sys.path
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

    size : :obj:`int`, :obj:`float`, :obj:`tuple` of :obj:`int` or :obj:`~QtCore.QSize`
        Rescale the icon to the specified `size`.
        If the value is :obj:`None` then do not rescale the icon.
        If an :obj:`int` then set the width and the height to be the `size` value.
        If a :obj:`float` then a scaling factor.
        If a :obj:`tuple` then the (width, height) values.
    mode : :obj:`Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio if rescaling. Allowed values are
        :obj:`Qt.IgnoreAspectRatio`, :obj:`Qt.KeepAspectRatio` or
        :obj:`Qt.KeepAspectRatioByExpanding`. The default mode is to keep the
        aspect ratio.

    Returns
    -------
    :obj:`~QtGui.QIcon`
        The input object converted to a :obj:`~QtGui.QIcon`.

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
            _icon = get_icon(image_to_base64(obj))
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
                raise IOError("Cannot find image file '{}'".format(obj))
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        _icon = QtGui.QIcon(application().style().standardIcon(obj))
    elif isinstance(obj, int):
        std_icons = [value for name, value in vars(QtWidgets.QStyle).items() if name.startswith('SP_')]
        if obj in std_icons:
            _icon = QtGui.QIcon(application().style().standardIcon(obj))
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
    return QtGui.QIcon(rescale_image(_icon, size, mode))


def image_to_base64(image=None, size=None, mode=QtCore.Qt.KeepAspectRatio, fmt='PNG'):
    """Convert the image to a :class:`~QtCore.QByteArray` encoded as Base64_.

    This function is useful if you want to save images in a database, use it in a
    data URI scheme_, or if you want to use images in your GUI and rather than loading
    images from a file on the hard disk you define your images in a Python module as
    Base64_ variables. Loading the images from the hard disk means that you must also
    distribute the images with your Python code if you share your code.

    .. _Base64: https://en.wikipedia.org/wiki/Base64
    .. _scheme: https://en.wikipedia.org/wiki/Data_URI_scheme

    Parameters
    ----------
    image : :obj:`object`, optional
        An image with a data type that is handled by :func:`get_icon`. If :obj:`None`
        then a dialog window is created to allow the user to select an image file
        that is saved in a folder.
    size : :obj:`int`, :obj:`float`, :obj:`tuple` of :obj:`int` or :obj:`~QtCore.QSize`
        Rescale the image to the specified `size` before converting it to Base64_.
        If the value is :obj:`None` then do not rescale the image.
        If an :obj:`int` then set the width and the height to be the `size` value.
        If a :obj:`float` then a scaling factor.
        If a :obj:`tuple` then the (width, height) values.
    mode : :obj:`Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio if rescaling. Allowed values are
        :obj:`Qt.IgnoreAspectRatio`, :obj:`Qt.KeepAspectRatio` or
        :obj:`Qt.KeepAspectRatioByExpanding`. The default mode is to keep the
        aspect ratio.
    fmt : :obj:`str`, optional
        The image format to use when converting. The supported values are: ``BMP``,
        ``JPG``, ``JPEG`` and ``PNG``.

    Returns
    -------
    :class:`~QtCore.QByteArray`
        The Base64_ representation of the image.

    Raises
    ------
    :exc:`IOError`
        If the image file cannot be found.
    :exc:`ValueError`
        If the image format, `fmt`, to use for converting is not supported.
    """
    fmt = fmt.upper()
    ALLOWED_FORMATS = ['BMP', 'JPG', 'JPEG', 'PNG']
    if fmt not in ALLOWED_FORMATS:
        raise ValueError('Invalid format {}. Must be one of: {}'.format(fmt, ', '.join(ALLOWED_FORMATS)))

    if isinstance(image, str) and '|' in image:
        # extract an icon from a Windows DLL/EXE file
        # uses ctypes and the .NET Framework to convert the icon to base64
        # import here in case pythonnet is not installed
        import clr
        import ctypes

        shell32 = ctypes.windll.shell32

        img_fmts = {
            'BMP':  clr.System.Drawing.Imaging.ImageFormat.Bmp,
            'JPG':  clr.System.Drawing.Imaging.ImageFormat.Jpeg,
            'JPEG': clr.System.Drawing.Imaging.ImageFormat.Jpeg,
            'PNG':  clr.System.Drawing.Imaging.ImageFormat.Png,
        }

        s = image.split('|')
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

    if image is None:
        title = 'Select an image file to convert to Base64'
        filters = {'Images': ('bmp', 'jpg', 'jpeg', 'png'), 'All files': '*'}
        image = prompt.filename(title=title, filters=filters)
        if image is None:
            return QtCore.QByteArray()
        image = str(image)

    icon = get_icon(image)
    try:
        default_size = icon.availableSizes()[-1]  # use the largest size as the default size
    except IndexError:
        prompt.critical('Invalid image file.')
        return QtCore.QByteArray()

    pixmap = icon.pixmap(default_size)
    if size is not None:
        pixmap = rescale_image(pixmap, size, mode)

    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, fmt)
    buffer.close()
    return array.toBase64()


def get_drag_enter_paths(event, pattern=None):
    """Returns the list of file paths from a :obj:`QDragEnterEvent`.

    Parameters
    ----------
    event : :obj:`QDragEnterEvent`
        A drag-enter event.
    pattern : :obj:`str`, optional
        Include only the file paths that match the `pattern`.

        See :func:`fnmatch.fnmatch`.

    Returns
    -------
    :obj:`list` of :obj:`str`
        The list of file paths.
    """
    if event.mimeData().hasUrls():
        urls = event.mimeData().urls()
        paths = [str(url.toLocalFile()) for url in urls if url.isValid() and url.scheme() == 'file']
        if pattern is None:
            return paths
        return fnmatch.filter(paths, pattern)
    return []


def rescale_image(image, size, mode=QtCore.Qt.KeepAspectRatio):
    """Rescale an image.

    Parameters
    ----------
    image : :obj:`object`
        Any object that is supported by :func:`~msl.qt.io.get_icon`.
    size : :obj:`int`, :obj:`float`, :obj:`tuple` of :obj:`int` or :obj:`~QtCore.QSize`
        Rescale the image to the specified `size`.
        If the value is :obj:`None` then do not rescale the image.
        If an :obj:`int` then set the width and the height to be the `size` value.
        If a :obj:`float` then a scaling factor.
        If a :obj:`tuple` then the (width, height) values.
    mode : :obj:`Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio when rescaling. Allowed values are
        :obj:`Qt.IgnoreAspectRatio`, :obj:`Qt.KeepAspectRatio` or
        :obj:`Qt.KeepAspectRatioByExpanding`. The default mode is to keep the
        aspect ratio.

    Returns
    -------
    :class:`~QtGui.QPixmap`
        The rescaled image.
    """
    if isinstance(image, QtGui.QIcon):
        try:
            max_size = image.availableSizes()[-1]
        except IndexError:
            max_size = QtCore.QSize(16, 16)
        pixmap = image.pixmap(max_size)
    elif isinstance(image, QtGui.QPixmap):
        pixmap = image
    else:
        return rescale_image(get_icon(image), size, mode)

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
