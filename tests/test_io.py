import os
import sys

import pytest
from msl.qt import application, io, QtWidgets, QtCore, QtGui

app = application()


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

    try:
        # make sure that the directory where the test_init.py file is not already in sys.path
        # otherwise the qt.get_icon('gamma.png') test below will not raise the expected exception
        sys.path.pop(sys.path.index(os.path.dirname(__file__)))
    except ValueError:
        pass

    # expect IOError provided that os.path.dirname(__file__) is not in sys.path
    with pytest.raises(IOError):
        io.get_icon('gamma.png')

    # insert this directory back into sys.path and check again
    sys.path.insert(0, os.path.dirname(__file__))
    assert isinstance(io.get_icon('gamma.png'), QtGui.QIcon)

    if sys.platform == 'win32':
        assert isinstance(io.get_icon('C:/Windows/System32/shell32.dll|0'), QtGui.QIcon)
        assert isinstance(io.get_icon('shell32.dll|0'), QtGui.QIcon)
        assert isinstance(io.get_icon('shell32|0'), QtGui.QIcon)
        with pytest.raises(IOError):
            io.get_icon('/shell32|0')  # fails because it appears as though a full path is being specified
        assert isinstance(io.get_icon('C:/Windows/explorer.exe|0'), QtGui.QIcon)
        assert isinstance(io.get_icon('explorer.exe|0'), QtGui.QIcon)
        assert isinstance(io.get_icon('explorer|0'), QtGui.QIcon)
        with pytest.raises(IOError):
            io.get_icon('C:/Windows/System32/explorer.exe|0')  # the exe is located at 'C:/Windows/explorer.exe'
        with pytest.raises(IOError):
            io.get_icon('shell32|9999')  # the maximum icon index should be much less than 9999


def test_icon_to_base64():
    assert isinstance(io.icon_to_base64('explorer|0'), QtCore.QByteArray)
    assert isinstance(io.icon_to_base64(QtWidgets.QStyle.SP_TitleBarMenuButton), QtCore.QByteArray)

    icon = io.get_icon('gamma.png')
    default_size = QtCore.QSize(191, 291)
    assert default_size.width() == 191
    assert default_size.height() == 291

    assert isinstance(io.icon_to_base64(icon), QtCore.QByteArray)

    new_size = io.get_icon(io.icon_to_base64(icon)).availableSizes()[0]
    assert new_size.width() == default_size.width()
    assert new_size.height() == default_size.height()

    factor = 2.6
    new_size = io.get_icon(io.icon_to_base64(icon, size=factor)).availableSizes()[0]
    assert new_size.width() == int(default_size.width()*factor)
    assert new_size.height() == int(default_size.height()*factor)

    y = 150
    new_size = io.get_icon(io.icon_to_base64(icon, size=y)).availableSizes()[0]
    assert new_size.width() == int(y*191./291.)
    assert new_size.height() == y

    x = 300
    new_size = io.get_icon(io.icon_to_base64(icon, size=x, mode=QtCore.Qt.KeepAspectRatioByExpanding)).availableSizes()[0]
    assert new_size.width() == x
    assert new_size.height() == int(x*291./191.)

    size = (150, 200)
    new_size = io.get_icon(io.icon_to_base64(icon, size=size, mode=QtCore.Qt.IgnoreAspectRatio)).availableSizes()[0]
    assert new_size.width() == size[0]
    assert new_size.height() == size[1]

    new_size = io.get_icon(io.icon_to_base64(icon, size=size)).availableSizes()[0]
    assert new_size.width() == int(size[1]*191./291.)
    assert new_size.height() == size[1]

    for fmt in ['BMP', 'JPG', 'JPEG', 'PNG']:
        io.icon_to_base64(icon, fmt=fmt)

    with pytest.raises(ValueError):
        io.icon_to_base64(icon, fmt='GIF')
