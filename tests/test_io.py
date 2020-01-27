import os
import sys

import pytest
from msl.qt import application, io, QtWidgets, QtCore, QtGui, Qt

app = application()


def has_pythonnet():
    try:
        import clr
    except ImportError:
        return False
    else:
        return True


def test_get_icon():

    assert isinstance(io.get_icon(QtGui.QIcon()), QtGui.QIcon)
    assert isinstance(io.get_icon(QtGui.QPixmap()), QtGui.QIcon)
    assert isinstance(io.get_icon(QtGui.QImage()), QtGui.QIcon)
    assert isinstance(io.get_icon(QtWidgets.QStyle.SP_TitleBarMenuButton), QtGui.QIcon)
    assert isinstance(io.get_icon(14), QtGui.QIcon)

    base64 = 'iVBORw0KGgoAAAANSUhEUgAAACgAAABCCAYAAAAlkZRRAAAACXBIWXMAAAsTAAALEwEAmpwYAAABpElEQVR' \
             'oge2ZT07CQBSHf29kLXKOsnApBEx7DAl3sT2BZzAx6C1ahYBLFzRxyQ1Q12SeiwoSQonjzMiLmW9Fh+nMlz' \
             'ft/HkFhEOuGnofRLz+3RyVztpVrhryhXjBhu8OlsN2DADQ/NYalS+m93sXVJpzACBGASAxvt+1kGuCoC3On' \
             'kGXc9824iMYBG0JgrZ4X0lMWe+KtKKkdTcvQgT3sRy2Y6URr6+bo3laV/cogpUcX28VpbV1vdtY4iyCYcsv' \
             'lSBoi7j94G474iMoXjDMg7YEQVvEC4rPDxq/xctBdH7CuAGA0/vSOBlkivk0o+iMNcfuVWq6+6uOfot4wdo' \
             'h/riKcqbqYOMrMfQTxEdQvKC4/eAu4iMYBG0RL9gAthd6yg4lco6B+AiKFzSfB1erBVQj8+CyF2PB1sPrAg' \
             'fyea4RP8TiBb+GmDIA0ArF5h/CLUCPx5AKuISAsJJYIV4w8O8hAOj2O9VbTJRNn6YpAHT6nZxQnYun49nmQ' \
             'NTrXcSaKN8t37RRU85AMRvPEgDoXnZT8Pe3un31FXMymTzL/xwrXlA8n2MHdwPYAbB5AAAAAElFTkSuQmCC'

    assert isinstance(io.get_icon(QtCore.QByteArray(base64.encode())), QtGui.QIcon)
    assert isinstance(io.get_icon(bytearray(base64.encode())), QtGui.QIcon)

    default_size = io.get_icon(QtWidgets.QStyle.SP_TitleBarMenuButton).availableSizes()[-1]
    assert isinstance(default_size, QtCore.QSize)

    with pytest.raises(TypeError):
        io.get_icon(None)

    with pytest.raises(IOError):
        io.get_icon(99999)  # not a valid QStyle.StandardPixmap enum value

    with pytest.raises(IOError):
        io.get_icon('this is not an icon')

    assert isinstance(io.get_icon(os.path.join(os.path.dirname(__file__), 'gamma.png')), QtGui.QIcon)

    # insert this directory into sys.path and check again
    sys.path.insert(0, os.path.dirname(__file__))
    assert isinstance(io.get_icon('gamma.png'), QtGui.QIcon)

    icon_1 = io.get_icon('gamma.png').availableSizes()[0]
    icon_2 = io.get_icon('gamma.png', size=0.5).availableSizes()[0]
    assert int(icon_1.width() * 0.5) == icon_2.width()
    assert int(icon_1.height() * 0.5) == icon_2.height()


@pytest.mark.skipif(not (has_pythonnet() and sys.platform == 'win32'), reason='requires pythonnet and win32')
def test_get_icon_dll_exe():
    assert isinstance(io.get_icon('C:/Windows/System32/shell32.dll|0'), QtGui.QIcon)
    assert isinstance(io.get_icon('shell32.dll|0'), QtGui.QIcon)
    assert isinstance(io.get_icon('shell32|0'), QtGui.QIcon)
    with pytest.raises(IOError):
        io.get_icon('/shell32|0')  # fails because it appears as though a full path is being specified
    assert isinstance(io.get_icon('C:/Windows/explorer.exe|0'), QtGui.QIcon)
    assert isinstance(io.get_icon('explorer.exe|0'), QtGui.QIcon)
    assert isinstance(io.get_icon('explorer|0'), QtGui.QIcon)
    if sys.maxsize > 2**32:
        # the exe is located at 'C:/Windows/explorer.exe'
        with pytest.raises(IOError):
            io.get_icon('C:/Windows/System32/explorer.exe|0')
    else:
        assert isinstance(io.get_icon('C:/Windows/System32/explorer.exe|0'), QtGui.QIcon)
    with pytest.raises(IOError) as err:
        io.get_icon('shell32|9999')  # the maximum icon index should be much less than 9999
    assert str(err.value).startswith('Requested icon 9999')


@pytest.mark.skipif(not (has_pythonnet() and sys.platform == 'win32'), reason='requires pythonnet and win32')
def test_icon_to_base64_exe():
    assert isinstance(io.icon_to_base64('explorer|0'), QtCore.QByteArray)

    # index number is < 0
    with pytest.raises(IOError):
        io.icon_to_base64('explorer|-1')

    # the filename not a DLL in C:/Windows/System32/ nor an EXE in C:/Windows/
    with pytest.raises(IOError):
        io.icon_to_base64('unknown_default|1')


def test_icon_to_base64():
    # reading from a standard Qt icon does not raise any errors
    assert isinstance(io.icon_to_base64(QtWidgets.QStyle.SP_TitleBarMenuButton), QtCore.QByteArray)

    # reading from a file does not raise any errors
    icon = io.get_icon('gamma.png')
    assert isinstance(io.icon_to_base64(icon), QtCore.QByteArray)
    assert io.icon_to_base64(icon).startsWith(b'iVBORw0KGgoAAAA')
    assert io.icon_to_base64(icon, fmt='PNG').startsWith(b'iVBORw0KGgoAAAA')
    assert io.icon_to_base64(icon, fmt='BMP').startsWith(b'Qk32jgIAAAAAADY')
    assert io.icon_to_base64(icon, fmt='JPG').startsWith(b'/9j/4AAQSkZJRgA')
    assert io.icon_to_base64(icon, fmt='JPEG').startsWith(b'/9j/4AAQSkZJRgA')

    # GIF is not supported
    with pytest.raises(ValueError):
        io.icon_to_base64(icon, fmt='GIF')

    # the size of 'gamma.png'
    size = QtCore.QSize(191, 291)

    # convert back to a QIcon and check each pixel
    original = icon.pixmap(size).toImage()
    converted = io.get_icon(io.icon_to_base64(icon)).pixmap(size).toImage()
    for x in range(0, size.width()):
        for y in range(0, size.height()):
            rgb_original = original.pixel(x, y)
            rgb_converted = converted.pixel(x, y)
            assert QtGui.QColor(rgb_original).getRgb() == QtGui.QColor(rgb_converted).getRgb()


def test_rescale_icon():
    # the actual size of 'gamma.png'
    size = QtCore.QSize(191, 291)

    icon = io.get_icon('gamma.png')
    sizes = icon.availableSizes()
    assert len(sizes) == 1
    assert sizes[0].width() == size.width()
    assert sizes[0].height() == size.height()

    new_size = io.rescale_icon(icon, 2.6).size()
    assert new_size.width() == int(size.width() * 2.6)
    assert new_size.height() == int(size.height() * 2.6)

    new_size = io.rescale_icon(icon, 150).size()
    assert new_size.width() == int((150. / float(size.height())) * size.width())
    assert new_size.height() == 150

    new_size = io.rescale_icon(icon, 300, aspect_mode=Qt.KeepAspectRatioByExpanding).size()
    assert new_size.width() == 300
    assert new_size.height() == int((300. / float(size.width())) * size.height())

    size2 = (150, 200)
    new_size = io.rescale_icon(icon, size2, aspect_mode=Qt.IgnoreAspectRatio).size()
    assert new_size.width() == size2[0]
    assert new_size.height() == size2[1]
    new_size = io.rescale_icon(icon, size2).size()
    assert new_size.width() == int(size2[1] * size.width() / float(size.height()))
    assert new_size.height() == size2[1]

    # passing different objects does not raise an error
    if sys.platform == 'win32':
        assert isinstance(io.rescale_icon('explorer|0', 1.0), QtGui.QPixmap)
    assert isinstance(io.rescale_icon(QtWidgets.QStyle.SP_TitleBarMenuButton, 1.0), QtGui.QPixmap)
    assert isinstance(io.rescale_icon(25, 1.0), QtGui.QPixmap)
    assert isinstance(io.rescale_icon(icon.pixmap(size), 1.0), QtGui.QPixmap)
    assert isinstance(io.rescale_icon(icon.pixmap(size).toImage(), 1.0), QtGui.QPixmap)

    with pytest.raises(TypeError) as err:
        io.rescale_icon('explorer|0', None)
    assert str(err.value).startswith('Unsupported "size"')

    # if a list/tuple then must contain 2 elements
    for item in [(), [], (256,), [256,], (256, 256, 256), [256, 256, 256]]:
        with pytest.raises(ValueError) as err:
            io.rescale_icon(icon, (1,))
        assert str(err.value) == 'The size must be in the form (width, height)'


def test_drag_enter_paths():
    mime = QtCore.QMimeData()

    event = QtGui.QDragEnterEvent(QtCore.QPoint(0, 0), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)
    paths = io.get_drag_enter_paths(event)
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

    paths = io.get_drag_enter_paths(event)
    assert len(paths) == 3
    assert '/path/to/image.jpeg' in paths
    assert '/path/to/image.png' in paths
    assert '/path/to/image2.jpg' in paths

    paths = io.get_drag_enter_paths(event, pattern='*.jp*g')
    assert len(paths) == 2
    assert '/path/to/image.jpeg' in paths
    assert '/path/to/image2.jpg' in paths

    paths = io.get_drag_enter_paths(event, pattern='*.png')
    assert len(paths) == 1
    assert '/path/to/image.png' in paths
