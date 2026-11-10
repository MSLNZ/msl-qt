from __future__ import annotations

import sys
from pathlib import Path

import pytest

from msl.qt import Button, Qt, QtCore, QtWidgets, convert


def test_text() -> None:
    b = Button(text="hello")
    assert b.text() == "hello"
    assert b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextOnly


def test_icon() -> None:
    path = Path(__file__).parent / "gamma.png"
    gamma_size = QtCore.QSize(191, 291)

    standard_pixmap = QtWidgets.QStyle.StandardPixmap.SP_DriveNetIcon

    icon = convert.to_qicon(standard_pixmap)
    sizes = icon.availableSizes()
    if sys.platform == "win32":
        assert len(sizes) > 1

    b = Button(icon=standard_pixmap)
    assert b.text() == ""
    assert not b.icon().isNull()
    assert b.iconSize() == sizes[0]
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    b = Button(icon=int(standard_pixmap))
    assert b.text() == ""
    assert not b.icon().isNull()
    assert b.iconSize() == sizes[0]
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    b = Button(icon=path)
    assert b.text() == ""
    assert not b.icon().isNull()
    assert b.iconSize() == gamma_size
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    b = Button(icon=convert.icon_to_base64(convert.to_qicon(path)))
    assert b.text() == ""
    assert not b.icon().isNull()
    assert b.iconSize() == gamma_size
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly


def test_icon_size() -> None:
    standard_pixmap = QtWidgets.QStyle.StandardPixmap.SP_DriveNetIcon

    icon = convert.to_qicon(standard_pixmap)
    sizes = icon.availableSizes()
    if sys.platform == "win32":
        assert len(sizes) > 1

    #
    # specify the size to the to_qicon() function
    #

    b = Button(icon=convert.to_qicon(standard_pixmap))
    assert b.text() == ""
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert b.iconSize() == sizes[0]

    b = Button(icon=convert.to_qicon(standard_pixmap, size=789))
    assert b.iconSize() == QtCore.QSize(789, 789)

    b = Button(icon=convert.to_qicon(standard_pixmap, size=3.0))
    # specifying a scale factor will use the largest available size
    assert b.iconSize() == QtCore.QSize(3 * sizes[-1].width(), 3 * sizes[-1].height())

    b = Button(icon=convert.to_qicon(standard_pixmap, size=QtCore.QSize(50, 50)))
    assert b.iconSize() == QtCore.QSize(50, 50)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(TypeError, match=r"QSize"):
            _ = Button(icon=convert.to_qicon(standard_pixmap, size=size))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]

    #
    # use the icon_size kwarg
    #

    b = Button(icon=convert.to_qicon(standard_pixmap), icon_size=1234)
    assert b.iconSize() == QtCore.QSize(1234, 1234)

    b = Button(icon=15, icon_size=1234)
    assert b.iconSize() == QtCore.QSize(1234, 1234)

    b = Button(icon=convert.to_qicon(standard_pixmap), icon_size=3.0)
    # specifying a scale factor will use the largest available size
    assert b.iconSize() == QtCore.QSize(3 * sizes[-1].width(), 3 * sizes[-1].height())

    b = Button(icon=convert.to_qicon(standard_pixmap), icon_size=(312, 312))
    assert b.iconSize() == QtCore.QSize(312, 312)

    b = Button(icon=convert.to_qicon(standard_pixmap), icon_size=QtCore.QSize(500, 500))
    assert b.iconSize() == QtCore.QSize(500, 500)

    for size in [(256,), (256, 256, 256)]:
        with pytest.raises(TypeError, match=r"QSize"):
            _ = Button(icon=convert.to_qicon(standard_pixmap), icon_size=size)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]


def test_text_and_icon() -> None:
    b = Button(text="hello", icon=QtWidgets.QStyle.StandardPixmap.SP_DriveNetIcon)
    assert b.text() == "hello"
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextUnderIcon

    b = Button(text="world", icon=QtWidgets.QStyle.StandardPixmap.SP_DriveNetIcon, is_text_under_icon=False)
    assert b.text() == "world"
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    b = Button(text="world", icon=14, is_text_under_icon=True)
    assert b.text() == "world"
    assert not b.icon().isNull()
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextUnderIcon


def test_tooltip() -> None:
    b = Button(tooltip="hello")
    assert b.text() == ""
    assert b.icon().isNull()
    assert b.toolTip() == "hello"
    assert b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
