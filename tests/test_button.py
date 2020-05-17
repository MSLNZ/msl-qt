import os
import sys

import pytest

from msl.qt import convert, Button, QtWidgets, QtCore, Qt


def test_text():
    b = Button(text='hello')
    assert b.text() == 'hello'
    assert b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextOnly


def test_icon():
    path = os.path.dirname(__file__) + '/gamma.png'
    gamma_size = QtCore.QSize(191, 291)

    int_val = QtWidgets.QStyle.SP_DriveNetIcon
    icon = convert.to_qicon(int_val)
    sizes = icon.availableSizes()
    if sys.platform == 'win32':
        assert len(sizes) > 1

    b = Button(icon=int_val)
    assert b.text() == ''
    assert not b.icon().isNull()
    assert b.iconSize() == sizes[0]
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly

    b = Button(icon=path)
    assert b.text() == ''
    assert not b.icon().isNull()
    assert b.iconSize() == gamma_size
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly

    b = Button(icon=convert.icon_to_base64(convert.to_qicon(path)))
    assert b.text() == ''
    assert not b.icon().isNull()
    assert b.iconSize() == gamma_size
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly


def test_icon_size():
    int_val = QtWidgets.QStyle.SP_DriveNetIcon
    icon = convert.to_qicon(int_val)
    sizes = icon.availableSizes()
    if sys.platform == 'win32':
        assert len(sizes) > 1

    #
    # specify the size to the get_icon function
    #

    b = Button(icon=convert.to_qicon(int_val))
    assert b.text() == ''
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly
    assert b.iconSize() == sizes[0]

    b = Button(icon=convert.to_qicon(int_val, size=789))
    assert b.iconSize() == QtCore.QSize(789, 789)

    b = Button(icon=convert.to_qicon(int_val, size=3.0))
    # specifying a scale factor will use the largest available size
    assert b.iconSize() == QtCore.QSize(3*sizes[-1].width(), 3*sizes[-1].height())

    b = Button(icon=convert.to_qicon(int_val, size=QtCore.QSize(50, 50)))
    assert b.iconSize() == QtCore.QSize(50, 50)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(ValueError, match='(width, height)'):
            Button(icon=convert.to_qicon(int_val, size=size))

    #
    # use the icon_size kwarg
    #

    b = Button(icon=convert.to_qicon(int_val), icon_size=1234)
    assert b.iconSize() == QtCore.QSize(1234, 1234)

    b = Button(icon=convert.to_qicon(int_val), icon_size=3.0)
    # specifying a scale factor will use the largest available size
    assert b.iconSize() == QtCore.QSize(3*sizes[-1].width(), 3*sizes[-1].height())

    b = Button(icon=convert.to_qicon(int_val), icon_size=(312, 312))
    assert b.iconSize() == QtCore.QSize(312, 312)

    b = Button(icon=convert.to_qicon(int_val), icon_size=QtCore.QSize(500, 500))
    assert b.iconSize() == QtCore.QSize(500, 500)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(ValueError, match='(width, height)'):
            Button(icon=convert.to_qicon(int_val), icon_size=size)


def test_text_and_icon():
    b = Button(text='hello', icon=QtWidgets.QStyle.SP_DriveNetIcon)
    assert b.text() == 'hello'
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextUnderIcon

    b = Button(text='world', icon=QtWidgets.QStyle.SP_DriveNetIcon, is_text_under_icon=False)
    assert b.text() == 'world'
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonTextBesideIcon


def test_tooltip():
    b = Button(tooltip='hello')
    assert b.text() == ''
    assert b.icon().isNull()
    assert b.toolTip() == 'hello'
    assert b.toolButtonStyle() == Qt.ToolButtonIconOnly
