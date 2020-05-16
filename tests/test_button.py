import pytest

from msl.qt import io, Button, QtWidgets, QtCore, Qt

int_val = QtWidgets.QStyle.SP_DriveNetIcon
icon = io.get_icon(int_val)
largest_icon_size = icon.availableSizes()[-1]


def test_text():
    b = Button(text='hello')
    assert b.text() == 'hello'
    assert b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextOnly


def test_icon_size():

    #
    # specify the size to the get_icon function
    #

    b = Button(icon=io.get_icon(int_val))
    assert b.text() == ''
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly
    assert b.iconSize() == largest_icon_size

    b = Button(icon=io.get_icon(int_val, size=789))
    assert b.iconSize() == QtCore.QSize(789, 789)

    b = Button(icon=io.get_icon(int_val, size=3.0))
    assert b.iconSize() == QtCore.QSize(3*largest_icon_size.width(), 3*largest_icon_size.height())

    b = Button(icon=io.get_icon(int_val, size=QtCore.QSize(50, 50)))
    assert b.iconSize() == QtCore.QSize(50, 50)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(ValueError, match='(width, height)'):
            Button(icon=io.get_icon(int_val, size=size))

    #
    # use the icon_size kwarg
    #

    b = Button(icon=io.get_icon(int_val), icon_size=1234)
    assert b.iconSize() == QtCore.QSize(1234, 1234)

    b = Button(icon=io.get_icon(int_val), icon_size=3.0)
    assert b.iconSize() == QtCore.QSize(3*largest_icon_size.width(), 3*largest_icon_size.height())

    b = Button(icon=io.get_icon(int_val), icon_size=(312, 312))
    assert b.iconSize() == QtCore.QSize(312, 312)

    b = Button(icon=io.get_icon(int_val), icon_size=QtCore.QSize(500, 500))
    assert b.iconSize() == QtCore.QSize(500, 500)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(ValueError, match='(width, height)'):
            Button(icon=io.get_icon(int_val), icon_size=size)


def test_text_and_icon():
    b = Button(text='hello', icon=icon)
    assert b.text() == 'hello'
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextUnderIcon

    b = Button(text='world', icon=icon, is_text_under_icon=False)
    assert b.text() == 'world'
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextBesideIcon


def test_tooltip():
    b = Button(tooltip='hello')
    assert b.text() == ''
    assert b.icon().isNull()
    assert b.toolTip() == 'hello'
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly
