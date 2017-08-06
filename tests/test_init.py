import pytest
from PyQt5 import QtWidgets, QtCore, QtGui

from msl import qt

app = qt.application()


def test_icon():
    assert isinstance(qt.icon(QtGui.QIcon()), QtGui.QIcon)
    assert isinstance(qt.icon(QtGui.QPixmap()), QtGui.QIcon)
    assert isinstance(qt.icon(QtWidgets.QStyle.SP_TitleBarMenuButton), QtGui.QIcon)

    logo = b'iVBORw0KGgoAAAANSUhEUgAAACgAAABCCAYAAAAlkZRRAAAACXBIWXMAAAsTAAALEwEAmpwYAAABpElEQVR' \
           b'oge2ZT07CQBSHf29kLXKOsnApBEx7DAl3sT2BZzAx6C1ahYBLFzRxyQ1Q12SeiwoSQonjzMiLmW9Fh+nMlz' \
           b'ft/HkFhEOuGnofRLz+3RyVztpVrhryhXjBhu8OlsN2DADQ/NYalS+m93sXVJpzACBGASAxvt+1kGuCoC3On' \
           b'kGXc9824iMYBG0JgrZ4X0lMWe+KtKKkdTcvQgT3sRy2Y6URr6+bo3laV/cogpUcX28VpbV1vdtY4iyCYcsv' \
           b'lSBoi7j94G474iMoXjDMg7YEQVvEC4rPDxq/xctBdH7CuAGA0/vSOBlkivk0o+iMNcfuVWq6+6uOfot4wdo' \
           b'h/riKcqbqYOMrMfQTxEdQvKC4/eAu4iMYBG0RL9gAthd6yg4lco6B+AiKFzSfB1erBVQj8+CyF2PB1sPrAg' \
           b'fyea4RP8TiBb+GmDIA0ArF5h/CLUCPx5AKuISAsJJYIV4w8O8hAOj2O9VbTJRNn6YpAHT6nZxQnYun49nmQ' \
           b'NTrXcSaKN8t37RRU85AMRvPEgDoXnZT8Pe3un31FXMymTzL/xwrXlA8n2MHdwPYAbB5AAAAAElFTkSuQmCC'
    assert isinstance(qt.icon(logo), QtGui.QIcon)
    assert isinstance(qt.icon(bytearray(logo)), QtGui.QIcon)
    assert isinstance(qt.icon(QtCore.QByteArray(logo)), QtGui.QIcon)

    with pytest.raises(TypeError):
        qt.icon(None)

    with pytest.raises(TypeError):
        qt.icon(99999)

    with pytest.raises(FileNotFoundError):
        qt.icon('cannot find this image')


def test_image_to_bytes():

    image = QtWidgets.QStyle.SP_TitleBarMenuButton
    default_size = qt.icon(image).availableSizes()[-1]  # the default size is chosen as the largest QSize
    assert default_size.width() == 64
    assert default_size.height() == 64

    assert isinstance(qt.image_to_bytes(image), bytes)

    new_size = qt.icon( qt.image_to_bytes(image) ).availableSizes()[0]
    assert new_size.width() == default_size.width()
    assert new_size.height() == default_size.height()

    factor = 2.6
    new_size = qt.icon( qt.image_to_bytes(image, size=factor) ).availableSizes()[0]
    assert new_size.width() == int(default_size.width()*factor)
    assert new_size.height() == int(default_size.height()*factor)

    width = 150
    new_size = qt.icon( qt.image_to_bytes(image, size=width) ).availableSizes()[0]
    assert new_size.width() == width
    assert new_size.height() == width

    size = (150, 200)
    new_size = qt.icon( qt.image_to_bytes(image, size=size) ).availableSizes()[0]
    assert new_size.width() == size[0]
    assert new_size.height() == size[0]

    new_size = qt.icon( qt.image_to_bytes(image, size=size, mode=QtCore.Qt.IgnoreAspectRatio) ).availableSizes()[0]
    assert new_size.width() == size[0]
    assert new_size.height() == size[1]

    new_size = qt.icon( qt.image_to_bytes(image, size=size, mode=QtCore.Qt.KeepAspectRatioByExpanding) ).availableSizes()[0]
    assert new_size.width() == size[1]
    assert new_size.height() == size[1]
