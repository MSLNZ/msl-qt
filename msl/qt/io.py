"""
I/O helper functions.
"""
import os
import sys
import base64
import fnmatch

from PyQt5 import QtWidgets, QtGui, QtCore

from msl.qt import application, prompt

__all__ = ['get_icon', 'get_drag_enter_paths', 'image_to_base64']


def get_icon(obj):
    """Convert the input object to a :obj:`QIcon`.

    Parameters
    ----------
    obj : :obj:`object`
        The object to be converted to a :obj:`QIcon`. The data type of `obj` can be one of:

        * :obj:`QIcon`
        * :obj:`QPixmap`
        * :obj:`QStyle.StandardPixmap`:
          See `StandardPixmap <http://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum>`_
          for the possible enum values. Example::

              get_icon(PyQt5.QtWidgets.QStyle.SP_TitleBarMenuButton)

        * :obj:`bytes`: A `Base64 <https://en.wikipedia.org/wiki/Base64>`_ representation
          of an encoded image.

          See :func:`image_to_base64`.

        * :obj:`str`: The path to an image file or an icon embedded in a Windows DLL/EXE file.

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

    Example
    -------
    To view the standard icons that come with Qt and that come with Windows run:

    >>> from msl.examples.qt import ShowStandardIcons
    >>> ShowStandardIcons() # doctest: +SKIP
    """
    if isinstance(obj, QtGui.QIcon):
        return obj
    elif isinstance(obj, str):
        if '|' in obj:  # then loading an icon from a Windows DLL/EXE file
            return get_icon(image_to_base64(obj))
        # otherwise loading an icon from an image file
        if os.path.isfile(obj):
            return QtGui.QIcon(obj)
        search_paths = sys.path + os.environ['PATH'].split(os.pathsep)
        for path in search_paths:
            full_path = os.path.join(path, obj)
            if os.path.isfile(full_path):
                return QtGui.QIcon(full_path)
        raise FileNotFoundError("Cannot find image file '{}'".format(obj))
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        return QtGui.QIcon(application().style().standardIcon(obj))
    elif isinstance(obj, QtGui.QPixmap):
        return QtGui.QIcon(obj)
    elif isinstance(obj, bytes):
        img = QtGui.QImage()
        img.loadFromData(QtCore.QByteArray.fromBase64(obj))
        return QtGui.QIcon(QtGui.QPixmap.fromImage(img))
    else:
        raise TypeError("Argument has unexpected type '{}'".format(type(obj).__name__))


def image_to_base64(image=None, size=None, mode=QtCore.Qt.KeepAspectRatio, fmt='PNG'):
    """Encode the image using Base64_ and return the encoded :obj:`bytes`.

    This function is useful if you want to save images in a database or if you
    want to use images in your GUI and rather than loading images from a
    file on the hard disk you define your images in a Python module as a Base64_
    :obj:`bytes` variable. Loading the images from the hard disk means that you
    must also distribute the images with your Python code if you share your code.

    .. _Base64: https://en.wikipedia.org/wiki/Base64

    Parameters
    ----------
    image : :obj:`object`, optional
        An image with a data type that is handled by :func:`get_icon`. If :obj:`None` then
        a dialog window is created to allow the user to select an image file.
    size : :obj:`float`, :obj:`tuple` of :obj:`int` or :obj:`QSize`, optional
        Rescale the image to the specified `size` before converting it to Base64_.
        If :obj:`None` then do not rescale the image. If a :obj:`float` then a scaling
        factor, if a :obj:`tuple` then the (width, height) values.
    mode : :obj:`Qt.AspectRatioMode`, optional
        How to maintain the aspect ratio if rescaling. Allowed values are
        :obj:`Qt.IgnoreAspectRatio`, :obj:`Qt.KeepAspectRatio` or
        :obj:`Qt.KeepAspectRatioByExpanding`. The default mode is :obj:`Qt.KeepAspectRatio`.
    fmt : :obj:`str`, optional
        The image format to use when converting. The supported values are: ``BMP``,
        ``JPG``, ``JPEG`` and ``PNG``.

    Returns
    -------
    :obj:`bytes`
        The Base64_ representation of the image encoded as :obj:`bytes`.

    Raises
    ------
    :obj:`FileNotFoundError`
        If the image file cannot be found.
    :obj:`ValueError`
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
            raise ValueError('The icon index must be >= 0')

        if not os.path.isfile(path):
            err_msg = "Cannot find DLL/EXE file '{}'".format(s[0])
            if os.path.split(path)[0]:  # then it wasn't just the filename that was specified
                raise FileNotFoundError(err_msg)

            filename = os.path.splitext(os.path.basename(path))[0]
            path = 'C:/Windows/System32/{}.dll'.format(filename)
            if not os.path.isfile(path):
                path = 'C:/Windows/{}.exe'.format(filename)
                if not os.path.isfile(path):
                    raise FileNotFoundError(err_msg)

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
        stream = clr.System.IO.MemoryStream()
        bmp = clr.System.Drawing.Icon.FromHandle(handle_ptr).ToBitmap()
        bmp.Save(stream, img_fmts[fmt])
        base = base64.b64encode(bytes(stream.GetBuffer()))

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
            return b''

    icon = get_icon(image)
    try:
        default_size = icon.availableSizes()[-1]  # use the largest size as the default size
    except IndexError:
        prompt.critical('Invalid image file.')
        return b''
    pixmap = icon.pixmap(default_size)

    if size is None:
        size = default_size
    elif isinstance(size, int):
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

    if (size.width() != default_size.width()) or (size.height() != default_size.height()):
        pixmap = pixmap.scaled(size, aspectRatioMode=mode)

    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, fmt)
    buffer.close()
    return bytes(array.toBase64())


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
