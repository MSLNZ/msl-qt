# cSpell: ignore IAAAAAADY bcdeghijlostvwxABCDFHIJKLNOSUVWX qryzafpnu MGTPEZYRQ
from __future__ import annotations

import math
import sys
from io import StringIO
from pathlib import Path

import pytest

from msl.qt import Qt, QtCore, QtGui, QtWidgets, convert, unicode


def test_to_qicon() -> None:
    assert isinstance(convert.to_qicon(QtGui.QIcon()), QtGui.QIcon)
    assert isinstance(convert.to_qicon(QtGui.QPixmap()), QtGui.QIcon)
    assert isinstance(convert.to_qicon(QtGui.QImage()), QtGui.QIcon)
    assert isinstance(convert.to_qicon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton), QtGui.QIcon)
    assert isinstance(convert.to_qicon(14), QtGui.QIcon)

    base64 = (
        b"iVBORw0KGgoAAAANSUhEUgAAACgAAABCCAYAAAAlkZRRAAAACXBIWXMAAAsTAAALEwEAmpwYAAABpElEQVR"
        b"oge2ZT07CQBSHf29kLXKOsnApBEx7DAl3sT2BZzAx6C1ahYBLFzRxyQ1Q12SeiwoSQonjzMiLmW9Fh+nMlz"
        b"ft/HkFhEOuGnofRLz+3RyVztpVrhryhXjBhu8OlsN2DADQ/NYalS+m93sXVJpzACBGASAxvt+1kGuCoC3On"
        b"kGXc9824iMYBG0JgrZ4X0lMWe+KtKKkdTcvQgT3sRy2Y6URr6+bo3laV/cogpUcX28VpbV1vdtY4iyCYcsv"
        b"lSBoi7j94G474iMoXjDMg7YEQVvEC4rPDxq/xctBdH7CuAGA0/vSOBlkivk0o+iMNcfuVWq6+6uOfot4wdo"
        b"h/riKcqbqYOMrMfQTxEdQvKC4/eAu4iMYBG0RL9gAthd6yg4lco6B+AiKFzSfB1erBVQj8+CyF2PB1sPrAg"
        b"fyea4RP8TiBb+GmDIA0ArF5h/CLUCPx5AKuISAsJJYIV4w8O8hAOj2O9VbTJRNn6YpAHT6nZxQnYun49nmQ"
        b"NTrXcSaKN8t37RRU85AMRvPEgDoXnZT8Pe3un31FXMymTzL/xwrXlA8n2MHdwPYAbB5AAAAAElFTkSuQmCC"
    )

    assert isinstance(convert.to_qicon(base64), QtGui.QIcon)
    assert isinstance(convert.to_qicon(QtCore.QByteArray(base64)), QtGui.QIcon)
    assert isinstance(convert.to_qicon(bytearray(base64)), QtGui.QIcon)

    with pytest.raises(ValueError, match=r"Cannot load image data from base64 bytes"):
        _ = convert.to_qicon(b"abc123")

    default_size = convert.to_qicon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton).availableSizes()[-1]
    assert isinstance(default_size, QtCore.QSize)

    with pytest.raises(TypeError):
        _ = convert.to_qicon(None)

    assert convert.to_qicon(99999).isNull()

    with pytest.raises(OSError, match=r"Cannot find"):
        _ = convert.to_qicon("this is not an icon")

    assert isinstance(convert.to_qicon(Path(__file__).parent / "gamma.png"), QtGui.QIcon)

    # insert this directory into sys.path and check again
    sys.path.insert(0, str(Path(__file__).parent))
    assert isinstance(convert.to_qicon("gamma.png"), QtGui.QIcon)

    icon_1 = convert.to_qicon("gamma.png").availableSizes()[0]
    icon_2 = convert.to_qicon("gamma.png", size=0.5).availableSizes()[0]
    assert int(icon_1.width() * 0.5) == icon_2.width()
    assert int(icon_1.height() * 0.5) == icon_2.height()


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows")
def test_to_qicon_dll_exe() -> None:
    assert isinstance(convert.to_qicon("C:/Windows/System32/shell32.dll|0"), QtGui.QIcon)
    assert isinstance(convert.to_qicon("shell32.dll|0"), QtGui.QIcon)
    assert isinstance(convert.to_qicon("shell32|0"), QtGui.QIcon)
    with pytest.raises(OSError, match=r"Cannot find"):
        _ = convert.to_qicon("/shell32|0")  # fails because it appears as though a full path is being specified
    assert isinstance(convert.to_qicon("C:/Windows/explorer.exe|0"), QtGui.QIcon)
    assert isinstance(convert.to_qicon("explorer.exe|0"), QtGui.QIcon)
    assert isinstance(convert.to_qicon("explorer|0"), QtGui.QIcon)
    if sys.maxsize > 2**32:
        # the exe is located at 'C:/Windows/explorer.exe'
        with pytest.raises(OSError, match=r"Cannot find"):
            _ = convert.to_qicon("C:/Windows/System32/explorer.exe|0")
    else:
        assert isinstance(convert.to_qicon("C:/Windows/System32/explorer.exe|0"), QtGui.QIcon)
    with pytest.raises(OSError, match=r"Requested icon 9999"):
        _ = convert.to_qicon("shell32|9999")  # the maximum icon index should be much less than 9999


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows")
def test_icon_to_base64_exe() -> None:
    assert isinstance(convert.icon_to_base64("explorer|0"), QtCore.QByteArray)

    # index number is < 0
    with pytest.raises(OSError, match=r"icon index must be >= 0"):
        _ = convert.icon_to_base64("explorer|-1")

    # the filename not a DLL in C:/Windows/System32/ nor an EXE in C:/Windows/
    with pytest.raises(OSError, match=r"Cannot find"):
        _ = convert.icon_to_base64("unknown_default|1")


def test_icon_to_base64() -> None:
    # reading from a standard Qt icon does not raise any errors
    assert isinstance(convert.icon_to_base64(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton), QtCore.QByteArray)

    # reading from a file does not raise any errors
    icon = convert.to_qicon("gamma.png")
    assert isinstance(convert.icon_to_base64(icon), QtCore.QByteArray)
    assert convert.icon_to_base64(icon).startsWith(b"iVBORw0KGgoAAAA")
    assert convert.icon_to_base64(icon, fmt="png").startsWith(b"iVBORw0KGgoAAAA")
    assert convert.icon_to_base64(icon, fmt="bmp").startsWith(b"Qk32jgIAAAAAADY")
    assert convert.icon_to_base64(icon, fmt="jpg").startsWith(b"/9j/4AAQSkZJRgA")
    assert convert.icon_to_base64(icon, fmt="jpeg").startsWith(b"/9j/4AAQSkZJRgA")

    # GIF is not supported
    with pytest.raises(ValueError, match=r"format 'gif'"):
        _ = convert.icon_to_base64(icon, fmt="gif")  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]

    # the size of 'gamma.png'
    size = QtCore.QSize(191, 291)

    # convert back to a QIcon and check each pixel
    original = icon.pixmap(size).toImage()
    converted = convert.to_qicon(convert.icon_to_base64(icon)).pixmap(size).toImage()
    for x in range(size.width()):
        for y in range(size.height()):
            rgb_original = original.pixel(x, y)
            rgb_converted = converted.pixel(x, y)
            assert QtGui.QColor(rgb_original).getRgb() == QtGui.QColor(rgb_converted).getRgb()


def test_rescale_icon() -> None:
    # the actual size of 'gamma.png'
    size = QtCore.QSize(191, 291)

    icon = convert.to_qicon("gamma.png")
    sizes = icon.availableSizes()
    assert len(sizes) == 1
    assert sizes[0].width() == size.width()
    assert sizes[0].height() == size.height()

    new_size = convert.rescale_icon(icon, 2.6).size()
    assert new_size.width() == int(size.width() * 2.6)
    assert new_size.height() == int(size.height() * 2.6)

    new_size = convert.rescale_icon(icon, 150).size()
    assert new_size.width() == int((150.0 / float(size.height())) * size.width())
    assert new_size.height() == 150

    new_size = convert.rescale_icon(icon, 300, aspect_mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding).size()
    assert new_size.width() == 300
    assert new_size.height() == int((300.0 / float(size.width())) * size.height())

    size2 = (150, 200)
    new_size = convert.rescale_icon(icon, size2, aspect_mode=Qt.AspectRatioMode.IgnoreAspectRatio).size()
    assert new_size.width() == size2[0]
    assert new_size.height() == size2[1]
    new_size = convert.rescale_icon(icon, size2).size()
    assert new_size.width() == int(size2[1] * size.width() / float(size.height()))
    assert new_size.height() == size2[1]

    # passing different objects does not raise an error
    if sys.platform == "win32":
        assert isinstance(convert.rescale_icon("explorer|0", 1.0), QtGui.QPixmap)
    assert isinstance(convert.rescale_icon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton, 1.0), QtGui.QPixmap)
    assert isinstance(convert.rescale_icon(25, 1.0), QtGui.QPixmap)
    assert isinstance(convert.rescale_icon(icon.pixmap(size), 1.0), QtGui.QPixmap)
    assert isinstance(convert.rescale_icon(icon.pixmap(size).toImage(), 1.0), QtGui.QPixmap)

    if sys.platform == "win32":
        with pytest.raises(TypeError, match=r'Unsupported "size"'):
            _ = convert.rescale_icon("explorer|0", None)

    # if a list/tuple then must contain 2 elements
    for item in [(256,), [256], (256, 256, 256), [256, 256, 256]]:
        with pytest.raises(TypeError, match=r"QSize"):
            _ = convert.rescale_icon(icon, item)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]


def test_to_qfont() -> None:
    font = QtGui.QFont()
    assert convert.to_qfont(font) is not font
    assert convert.to_qfont(font).isCopyOf(font)
    assert convert.to_qfont(100).pointSize() == 100
    assert convert.to_qfont(12.3).pointSizeF() == 12.3
    assert convert.to_qfont("Papyrus").family() == "Papyrus"

    f = convert.to_qfont("Ariel")
    assert f.family() == "Ariel"
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48, QtGui.QFont.Weight.Bold))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48, QtGui.QFont.Weight.Bold, True))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert f.italic()

    f = convert.to_qfont(["Ariel"])
    assert f.family() == "Ariel"
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48, QtGui.QFont.Weight.Bold))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert not f.italic()

    f = convert.to_qfont(("Ariel", 48, QtGui.QFont.Weight.Bold, True))
    assert f.family() == "Ariel"
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert f.italic()

    f = convert.to_qfont(("Comic Sans MS", 36.6))
    assert f.family() == "Comic Sans MS"
    assert f.pointSize() == 37
    assert f.pointSizeF() == 36.6
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()


def test_to_qfont_families() -> None:
    f = convert.to_qfont(["Papyrus", "Ariel"])
    assert f.family() == "Papyrus"
    assert f.families() == ["Papyrus", "Ariel"]

    f = convert.to_qfont((["Ariel", "Papyrus"], 48))
    assert f.family() == "Ariel"
    assert f.families() == ["Ariel", "Papyrus"]
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Normal
    assert not f.italic()

    # family names can occur in any position
    f = convert.to_qfont(("Papyrus", 48, "Ariel", QtGui.QFont.Weight.Bold))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    assert f.family() == "Papyrus"
    assert f.families() == ["Papyrus", "Ariel"]
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert not f.italic()

    f = convert.to_qfont((48, "Helvetica [Cronyx]", QtGui.QFont.Weight.Bold, True, "Papyrus", "Ariel"))  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]
    assert f.family() == "Helvetica [Cronyx]"
    assert f.families() == ["Helvetica [Cronyx]", "Papyrus", "Ariel"]
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Weight.Bold
    assert f.italic()

    f = convert.to_qfont(["Papyrus", "Ariel", "Helvetica [Cronyx]"])
    assert f.family() == "Papyrus"
    assert f.families() == ["Papyrus", "Ariel", "Helvetica [Cronyx]"]


def test_to_qcolor() -> None:

    def assert_rgba(c: QtGui.QColor, r: int, g: int, b: int, a: int) -> None:
        assert c.red() == r
        assert c.green() == g
        assert c.blue() == b
        assert c.alpha() == a

    # QtGui.QColor
    color = QtGui.QColor(127, 127, 127)
    assert convert.to_qcolor(color) is not color
    assert convert.to_qcolor(color) == color

    # int or Qt.GlobalColor
    assert_rgba(convert.to_qcolor(7), 0, 0, 7, 255)  # 000007
    assert_rgba(convert.to_qcolor(Qt.GlobalColor.red), 255, 0, 0, 255)

    # string
    assert_rgba(convert.to_qcolor("red"), 255, 0, 0, 255)
    assert_rgba(convert.to_qcolor("#00FF00"), 0, 255, 0, 255)
    assert_rgba(convert.to_qcolor("#080000FF"), 0, 0, 255, 8)

    # tuple (can mix int 0-255 and float 0.0-1.0)
    assert_rgba(convert.to_qcolor((34, 58, 129)), 34, 58, 129, 255)
    assert_rgba(convert.to_qcolor((34, 58, 129, 50)), 34, 58, 129, 50)

    # wrong number of arguments (get fatal crash with PySide6 during tests)
    for obj in [(1, 2), (1, 2, 3, 4, 5, 6, 7)]:
        with pytest.raises(TypeError):
            _ = convert.to_qcolor(obj)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]


def test_number_to_si() -> None:  # noqa: PLR0915
    def check(args: tuple[float, str], number: float, string: str) -> None:
        value, prefix = args
        if math.isnan(number):
            assert math.isnan(value)
            assert prefix == ""
        elif math.isinf(number):
            assert math.isinf(value)
            assert prefix == ""
        else:
            assert number == pytest.approx(value, rel=1e-12)
            assert prefix == string

    check(convert.number_to_si(math.nan), math.nan, "")
    check(convert.number_to_si(math.inf), math.inf, "")
    check(convert.number_to_si(-math.inf), -math.inf, "")

    check(convert.number_to_si(1e-34), 0.0001, "q")
    check(convert.number_to_si(2.202e-31), 0.2202, "q")
    check(convert.number_to_si(3.1e-30), 3.1, "q")
    check(convert.number_to_si(2.21e-29), 22.1, "q")
    check(convert.number_to_si(2.21e-28), 221.0, "q")
    check(convert.number_to_si(5.311e-27), 5.311, "r")
    check(convert.number_to_si(6.5e-26), 65.0, "r")
    check(convert.number_to_si(-1.234e-25), -123.4, "r")
    check(convert.number_to_si(-1.234e-24), -1.234, "y")
    check(convert.number_to_si(1.2e-23), 12.0, "y")
    check(convert.number_to_si(1.2e-22), 120.0, "y")
    check(convert.number_to_si(-4.2345e-21), -4.2345, "z")
    check(convert.number_to_si(0.123e-20), 1.23, "z")
    check(convert.number_to_si(-123456e-23), -1.23456, "a")
    check(convert.number_to_si(1.23e-13), 123.0, "f")
    check(convert.number_to_si(-1.23e-12), -1.23, "p")
    check(convert.number_to_si(123.0e-12), 123.0, "p")
    check(convert.number_to_si(-12.3e-10), -1.23, "n")
    check(convert.number_to_si(1.23e-8), 12.3, "n")
    check(convert.number_to_si(-0.123e-7), -12.3, "n")
    check(convert.number_to_si(0.123e-5), 1.23, unicode.MICRO)
    check(convert.number_to_si(0.123e-5, unicode=False), 1.23, "u")
    check(convert.number_to_si(-0.0123), -12.3, "m")
    check(convert.number_to_si(123.4), 123.4, "")
    check(convert.number_to_si(0), 0, "")
    check(convert.number_to_si(-123456.789), -123.456789, "k")
    check(convert.number_to_si(1.23e8), 123.0, "M")
    check(convert.number_to_si(-0.123e10), -1.23, "G")
    check(convert.number_to_si(1.23e14), 123.0, "T")
    check(convert.number_to_si(-1.23e12), -1.23, "T")
    check(convert.number_to_si(12.3e15), 12.3, "P")
    check(convert.number_to_si(-712.123e14), -71.2123, "P")
    check(convert.number_to_si(1234.56e16), 12.3456, "E")
    check(convert.number_to_si(-12.3e18), -12.3, "E")
    check(convert.number_to_si(0.123e20), 12.3, "E")
    check(convert.number_to_si(-12.3e20), -1.23, "Z")
    check(convert.number_to_si(-1.754e21), -1.754, "Z")
    check(convert.number_to_si(123.456e20), 12.3456, "Z")
    check(convert.number_to_si(123.456e21), 123.456, "Z")
    check(convert.number_to_si(-0.42e24), -420.0, "Z")
    check(convert.number_to_si(1.234e24), 1.234, "Y")
    check(convert.number_to_si(12.678e24), 12.678, "Y")
    check(convert.number_to_si(12345.678e22), 123.45678, "Y")
    check(convert.number_to_si(1.0001e27), 1.0001, "R")
    check(convert.number_to_si(6.221e28), 62.21, "R")
    check(convert.number_to_si(7.1341e29), 713.41, "R")
    check(convert.number_to_si(9.12e30), 9.12, "Q")
    check(convert.number_to_si(8.0614e31), 80.614, "Q")
    check(convert.number_to_si(1e32), 100.0, "Q")
    check(convert.number_to_si(1.03e33), 1030.0, "Q")
    check(convert.number_to_si(1.2345e35), 123450.0, "Q")

    check(convert.number_to_si(-0), 0.0, "")
    check(convert.number_to_si(0), 0.0, "")
    check(convert.number_to_si(1), 1.0, "")
    check(convert.number_to_si(-1), -1.0, "")
    check(convert.number_to_si(12), 12.0, "")
    check(convert.number_to_si(123), 123.0, "")
    check(convert.number_to_si(1234), 1.234, "k")
    check(convert.number_to_si(12345), 12.345, "k")
    check(convert.number_to_si(123456), 123.456, "k")
    check(convert.number_to_si(1234567), 1.234567, "M")
    check(convert.number_to_si(12345678), 12.345678, "M")
    check(convert.number_to_si(123456789), 123.456789, "M")
    check(convert.number_to_si(-123456789), -123.456789, "M")
    check(convert.number_to_si(1234567890), 1.234567890, "G")
    check(convert.number_to_si(12345678901), 12.345678901, "G")
    check(convert.number_to_si(123456789012), 123.456789012, "G")
    check(convert.number_to_si(1234567890123), 1.234567890123, "T")
    check(convert.number_to_si(12345678901234), 12.345678901234, "T")
    check(convert.number_to_si(123456789012345), 123.456789012345, "T")
    check(convert.number_to_si(1234567890123456), 1.234567890123456, "P")
    check(convert.number_to_si(-1234567890123456), -1.234567890123456, "P")
    check(convert.number_to_si(12345678901234567), 12.345678901234567, "P")
    check(convert.number_to_si(123456789012345678), 123.456789012345678, "P")
    check(convert.number_to_si(1234567890123456789), 1.234567890123456789, "E")
    check(convert.number_to_si(12345678901234567890), 12.345678901234567890, "E")
    check(convert.number_to_si(123456789012345678901), 123.456789012345678901, "E")
    check(convert.number_to_si(1234567890123456789012), 1.234567890123456789012, "Z")
    check(convert.number_to_si(12345678901234567890123), 12.345678901234567890123, "Z")
    check(convert.number_to_si(123456789012345678901234), 123.456789012345678901234, "Z")
    check(convert.number_to_si(1234567890123456789012345), 1.234567890123456789012345, "Y")
    check(convert.number_to_si(12345678901234567890123456), 12.345678901234567890123456, "Y")
    check(convert.number_to_si(123456789012345678901234567), 123.456789012345678901234567, "Y")
    check(convert.number_to_si(-123456789012345678901234567), -123.456789012345678901234567, "Y")
    check(convert.number_to_si(1234567890123456789012345678), 1.234567890123456789012345678, "R")
    check(convert.number_to_si(-12345678901234567890123456789), -12.345678901234567890123456789, "R")
    check(convert.number_to_si(123456789012345678901234567890), 123.456789012345678901234567890, "R")
    check(convert.number_to_si(1234567890123456789012345678901), 1.234567890123456789012345678901, "Q")
    check(convert.number_to_si(-12345678901234567890123456789012), -12.345678901234567890123456789012, "Q")
    check(convert.number_to_si(123456789012345678901234567890123), 123.456789012345678901234567890123, "Q")
    check(convert.number_to_si(1234567890123456789012345678901234), 1234.567890123456789012345678901234, "Q")


def test_si_to_number() -> None:  # noqa: PLR0915
    def check(string: str, value: float) -> None:
        assert convert.si_to_number(string) == pytest.approx(value)

    check("12.3m", 0.0123)
    check("123.456789k", 123456.789)
    check("71.2123P", 712.123e14)
    check("123f", 1.23e-13)

    check("0.00321Q", 3.21e27)
    check("0.12Q", 1.2e29)
    check("1.2Q", 1.2e30)
    check("33.3Q", 33.3e30)
    check("-123.4Q", -1.234e32)
    check("-1234567Q", -1.234567e36)
    check("0.12R", 1.2e26)
    check("1.2R", 1.2e27)
    check("33.3R", 33.3e27)
    check("-123.4R", -1.234e29)
    check("-1234R", -1.234e30)
    check("0.12Y", 1.2e23)
    check("1.2Y", 1.2e24)
    check("-123.4Y", -1.234e26)
    check("0.12Z", 1.2e20)
    check("-1.2Z", -1.2e21)
    check("-123.4Z", -1.234e23)
    check("-0.12E", -1.2e17)
    check("1.2E", 1.2e18)
    check("123.4E", 1.234e20)
    check("-0.12P", -1.2e14)
    check("1.2P", 1.2e15)
    check("123.4P", 1.234e17)
    check("0.12T", 1.2e11)
    check("-1.2T", -1.2e12)
    check("123.4T", 1.234e14)
    check("-0.12G", -1.2e8)
    check("1.2G", 1.2e9)
    check("123.4G", 1.234e11)
    check("0.12M", 1.2e5)
    check("1.2M", 1.2e6)
    check("-123.4M", -1.234e8)
    check("-0.12k", -1.2e2)
    check("1.2k", 1.2e3)
    check("123.4k", 1.234e5)
    check("-0.12", -0.12)
    check("0", 0)
    check("123456789", 123456789.0)
    check("1.2", 1.2)
    check("1e8", 1e8)
    check("-1.e8", -1.0e8)
    check("1.234e13", 1.234e13)
    check("123.4", 123.4)
    check("0.12m", 1.2e-4)
    check("-1.2m", -1.2e-3)
    check("123.4m", 1.234e-1)
    check("-0.12\u00b5", -1.2e-7)
    check("1.2\u00b5", 1.2e-6)
    check("123.4\u00b5", 1.234e-4)
    check("-0.12u", -1.2e-7)
    check("1.2u", 1.2e-6)
    check("123.4u", 1.234e-4)
    check("0.12n", 1.2e-10)
    check("1.2n", 1.2e-9)
    check("-123.4n", -1.234e-7)
    check("0.12p", 1.2e-13)
    check("1.2p", 1.2e-12)
    check("-123.4p", -1.234e-10)
    check("0.12f", 1.2e-16)
    check("-1.2f", -1.2e-15)
    check("123.4f", 1.234e-13)
    check("0.12a", 1.2e-19)
    check("-1.2a", -1.2e-18)
    check("123.4a", 1.234e-16)
    check("-0.12z", -1.2e-22)
    check("-1.2z", -1.2e-21)
    check("123.4z", 1.234e-19)
    check("0.12y", 1.2e-25)
    check("1.2y", 1.2e-24)
    check("-123.4y", -1.234e-22)
    check("0.3134r", 3.134e-28)
    check("1.02r", 1.02e-27)
    check("42.463r", 4.2463e-26)
    check("-123.4r", -1.234e-25)
    check("4321r", 4.321e-24)
    check("0.000001q", 1.0e-36)
    check("0.3134q", 3.134e-31)
    check("1.02q", 1.02e-30)
    check("42.463q", 4.2463e-29)
    check("-123.4q", -1.234e-28)
    check("4321q", 4.321e-27)

    # spaces
    check("123.4 m", 1.234e-1)
    check("123.4   m    ", 1.234e-1)
    check("  123.4   m    ", 1.234e-1)
    for item in ["", "    ", "\t", " \t  "]:
        with pytest.raises(ValueError, match=r"could not convert"):
            _ = convert.si_to_number(item)

    # nan, +/-inf
    assert math.isnan(convert.si_to_number("nan"))
    value = convert.si_to_number("inf")
    assert math.isinf(value)
    assert value > 0
    value = convert.si_to_number("+inf")
    assert math.isinf(value)
    assert value > 0
    value = convert.si_to_number("-inf")
    assert math.isinf(value)
    assert value < 0

    for c in "bcdeghijlostvwxABCDFHIJKLNOSUVWX":
        with pytest.raises(ValueError, match=r"could not convert"):
            _ = convert.si_to_number("1.2" + c)

        for prefix in "qryzafpnu\u00b5mkMGTPEZYRQ":
            with pytest.raises(ValueError, match=r"could not convert"):
                _ = convert.si_to_number("1.2" + c + prefix)


def test_print_base64() -> None:
    icon = "docs/assets/images/favicon.ico"

    with StringIO() as s:
        convert.print_base64(icon, size=16, file=s)
        _ = s.seek(0)
        actual = [line.rstrip() for line in s.readlines()]
        expected = r"""icon = (
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bA"
    b"AAAEnRFWHRfcV9pY29PcmlnRGVwdGgAMzLV4rjsAAACDUlEQVQ4jaWTz0tUURTHP+e+OzPPnB"
    b"ktdQQdTakWkbsmKNtEEARtIqKgoH+gdkGrti2C+g8kgtqEK7f9Adm2RVAgyZiIY4ZNzsx78+5"
    b"797RwTCkKrC8cOPecc79wfnzl7GxtAxgBtjkYCkBggVIvUPpL8R9h/uXTbwTas1386mf7Yvtz"
    b"ACYAVp1hPTUUBJzCUmKIFVpeWE4MjVRYc0KqsOIMHS9Y6RF898KjSszNsuNDYlBgbizmZMFTN"
    b"MrLasTidJu58ZiigSejMafCjK/ZDoOJFS4POB5XI7ZS4WIx42q1w1CgPKh0uVR2zDfzbKZCOV"
    b"BujXSZyHlauwQGWI0DEHg+EXFjMIHIknih4QwE8K5ruL1yiEYqkBpSFYzo3hAPW2V+M8+1Qce"
    b"6Myy3Ao4XPPfWQl58KfBsus3CVHunaQ9dhUjBA1aBUassO8OFpX4EeD3VoWyUfqPc+dxHPREe"
    b"Hu0w37IgUBDIeuswCoSiVKznbTtgIxWK1rPihLtHHDrT5P5wl/ff8rxpWRYjy9OxiPqJFjMFj"
    b"5w+V4tqfVnYSIVPSUBolDNhxsfEUDJwpeTYyoRXzTyNTJi0nusDjj5RFrZzyPnZWlR3JiwHyn"
    b"CgOIW6M4wECgJrTjBAxSpDgbKZQSM1CDCe89gMqOY8AEmvr8neG+BYfu/2YoWigWL+Zz75by1"
    b"YdmQccnA5F4HWD9Mi1v4ahSN+AAAAAElFTkSuQmCC"
)
""".splitlines()
        assert actual == expected

    with StringIO() as s:
        convert.print_base64(icon, size=16, name="my_favicon", file=s, line_width=60)
        _ = s.seek(0)
        actual = [line.rstrip() for line in s.readlines()]
        expected = r"""my_favicon = (
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIW"
    b"XMAAA7EAAAOxAGVKw4bAAAAEnRFWHRfcV9pY29PcmlnRGVwdGgAMz"
    b"LV4rjsAAACDUlEQVQ4jaWTz0tUURTHP+e+OzPPnBktdQQdTakWkbs"
    b"mKNtEEARtIqKgoH+gdkGrti2C+g8kgtqEK7f9Adm2RVAgyZiIY4ZN"
    b"zsx78+5797RwTCkKrC8cOPecc79wfnzl7GxtAxgBtjkYCkBggVIvU"
    b"PpL8R9h/uXTbwTas1386mf7YvtzACYAVp1hPTUUBJzCUmKIFVpeWE"
    b"4MjVRYc0KqsOIMHS9Y6RF898KjSszNsuNDYlBgbizmZMFTNMrLasT"
    b"idJu58ZiigSejMafCjK/ZDoOJFS4POB5XI7ZS4WIx42q1w1CgPKh0"
    b"uVR2zDfzbKZCOVBujXSZyHlauwQGWI0DEHg+EXFjMIHIknih4QwE8"
    b"K5ruL1yiEYqkBpSFYzo3hAPW2V+M8+1Qce6Myy3Ao4XPPfWQl58Kf"
    b"Bsus3CVHunaQ9dhUjBA1aBUassO8OFpX4EeD3VoWyUfqPc+dxHPRE"
    b"eHu0w37IgUBDIeuswCoSiVKznbTtgIxWK1rPihLtHHDrT5P5wl/ff"
    b"8rxpWRYjy9OxiPqJFjMFj5w+V4tqfVnYSIVPSUBolDNhxsfEUDJwp"
    b"eTYyoRXzTyNTJi0nusDjj5RFrZzyPnZWlR3JiwHynCgOIW6M4wECg"
    b"JrTjBAxSpDgbKZQSM1CDCe89gMqOY8AEmvr8neG+BYfu/2YoWigWL"
    b"+Zz75by1YdmQccnA5F4HWD9Mi1v4ahSN+AAAAAElFTkSuQmCC"
)
""".splitlines()
        assert actual == expected
