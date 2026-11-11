"""Functions to convert objects."""

from __future__ import annotations

import ctypes
import os
import sys
import textwrap
from math import fabs, floor, isfinite, log10
from pathlib import Path
from typing import TYPE_CHECKING

from ._qt import QtCore, QtGui, QtWidgets, application
from .characters import MICRO
from .constants import SI_PREFIX_MAP

if TYPE_CHECKING:
    from typing import Literal

    from .typing import Color, Font, Size, SupportsWrite

__all__: list[str] = [
    "icon_to_base64",
    "number_to_si",
    "print_base64",
    "rescale_icon",
    "si_to_number",
    "to_qcolor",
    "to_qfont",
    "to_qicon",
]


def to_qfont(obj: Font | None) -> QtGui.QFont:  # noqa: C901, PLR0912
    """Convert an object into a [QFont][QtGui.QFont].

    Args:
        obj: The object to convert.

    Returns:
        A [QFont][QtGui.QFont].
    """
    if obj is None:
        return QtGui.QFont()

    if isinstance(obj, QtGui.QFont):
        return QtGui.QFont(obj)

    if isinstance(obj, int):
        f = QtGui.QFont()
        f.setPointSize(obj)
        return f

    if isinstance(obj, float):
        f = QtGui.QFont()
        f.setPointSizeF(obj)
        return f

    if isinstance(obj, str):
        f = QtGui.QFont()
        f.setFamily(obj)
        return f

    families: list[str] = []
    point_size, weight, italic, point_size_f = -1, -1, False, -1.0
    for arg in obj:
        if isinstance(arg, float):
            point_size = int(arg)
            point_size_f = arg
        elif isinstance(arg, str):
            families.append(arg)
        elif isinstance(arg, QtGui.QFont.Weight):
            weight = arg
        elif isinstance(arg, bool):
            italic = arg
        elif isinstance(arg, int):
            if point_size == -1:
                point_size = arg
            else:
                weight = arg
        else:
            families.extend(arg)

    font = QtGui.QFont(families, point_size, weight, italic)
    if point_size_f > 0:
        font.setPointSizeF(point_size_f)
    return font


def to_qcolor(obj: Color) -> QtGui.QColor:
    """Convert an object into a [QColor][QtGui.QColor].

    Args:
        obj: The object to convert.

    Returns:
        A [QColor][QtGui.QColor].
    """
    if isinstance(obj, (list, tuple)):
        return QtGui.QColor(*obj)
    return QtGui.QColor(obj)


def number_to_si(number: float, *, unicode: bool = True) -> tuple[float, str]:
    """Convert a number to be representable with an SI prefix.

    The hecto (h), deka (da), deci (d) and centi (c) prefixes are not used.

    ```pycon
    >>> from msl.qt import number_to_si
    >>> number_to_si(0.0123)
    (12.3, 'm')
    >>> number_to_si(123456.789)
    (123.456789, 'k')
    >>> number_to_si(712.123e14)
    (71.2123, 'P')
    >>> number_to_si(1.23e-13)
    (123.0, 'f')

    ```

    Args:
        number: The number to convert.
        unicode: Whether to use the unicode \u00b5 symbol for micro.

    Returns:
        The number rescaled and the SI prefix.
    """
    if number == 0 or not isfinite(number):
        return number, ""

    n = floor(log10(fabs(number)) / 3)
    if n == 0:
        return number, ""

    if unicode and n == -2:  # noqa: PLR2004
        si = MICRO
    else:
        try:
            si = SI_PREFIX_MAP[n]
        except KeyError:
            si, n = ("q", -10) if n < 0 else ("Q", 10)

    return number * 10 ** (-3 * n), si


def si_to_number(string: str) -> float:
    """Convert a string with an SI prefix to a number.

    ```pycon
    >>> from msl.qt import si_to_number
    >>> si_to_number("12.3m")
    0.0123
    >>> si_to_number("123.456789k")
    123456.789
    >>> si_to_number("71.2123P")
    7.12123e+16
    >>> si_to_number("123f")
    1.23e-13

    ```

    Args:
        string: The string to convert.

    Returns:
        The number.
    """
    stripped = string.strip()
    if (not stripped) or stripped == "nan" or stripped.endswith("inf"):
        # let the builtin implementation handle an empty string
        # nan would be mistaken for the nano (n) SI prefix
        # +/-inf would be mistaken for the femto (f) SI prefix
        return float(stripped)

    prefix = stripped[-1]
    if prefix == MICRO:
        prefix = "u"

    for n, value in SI_PREFIX_MAP.items():
        if prefix == value:
            return float(stripped[:-1]) * (10.0 ** (3 * n))

    return float(stripped)


def to_qicon(  # noqa: C901, PLR0912
    obj: object,
    *,
    size: int | float | QtCore.QSize | tuple[int, int] | None = None,  # noqa: PYI041
    aspect_mode: QtCore.Qt.AspectRatioMode = QtCore.Qt.AspectRatioMode.KeepAspectRatio,
) -> QtGui.QIcon:
    """Convert the input object to a [QIcon][QtGui.QIcon].

    To view the standard icons that come with Qt and that come with Windows run

    ```console
    python -c 'from msl.examples.qt import show; show("StandardIcons")'
    ```

    Args:
        obj: The object to be converted. The data type of `obj` can be one of

            * [QIcon][QtGui.QIcon]
            * [QPixmap][QtGui.QPixmap]
            * [QImage][QtGui.QImage]
            * [StandardPixmap][QtWidgets.QStyle.StandardPixmap]
            * [QByteArray][QtCore.QByteArray] &mdash; [base64](https://en.wikipedia.org/wiki/Base64)
              representation of an encoded icon (see [icon_to_base64][..icon_to_base64]).
            * [str][] | [Path][pathlib.Path] &mdash; The path to an icon file or an icon embedded in a DLL or EXE file.
                If `obj` is a path to an icon file and only the filename is specified then the
                directories in [sys.path][] and the `PATH` environment variable are also
                used to search for the icon file. If `obj` refers to an icon in a Windows DLL/EXE
                file then `obj` is the path to the DLL/EXE file and the icon index separated by the
                `|` character.

                The following examples illustrate the various ways to request an icon by passing in a [str][] argument.

                ```python
                # provide the path to the image file
                to_qicon("resources/icons/msl.png')

                # load icon 23 from the Windows shell32.dll file
                to_qicon("shell32|23")

                # load icon 0 from the Windows explorer.exe file
                to_qicon("explorer|0")
                ```

        size: Rescale the icon to the specified `size`.
            If the value is `None` then do not rescale the icon.
            If an [int][] then set the width and the height to be the `size` value.
            If a [float][] then a scaling factor.
            If a [tuple][] then the (width, height) values.
        aspect_mode: How to maintain the aspect ratio if rescaling. The default mode
            is to keep the aspect ratio.

    Returns:
        The input object converted to a [QIcon][QtGui.QIcon].
    """
    _ = application()
    _icon = None
    if isinstance(obj, QtGui.QIcon):
        _icon = obj
    elif isinstance(obj, (str, Path)):
        obj = str(obj)
        if "|" in obj:  # then loading an icon from a Windows DLL/EXE file
            _icon = to_qicon(icon_to_base64(obj))
        elif os.path.isfile(obj):  # noqa: PTH113
            _icon = QtGui.QIcon(obj)
        else:
            search_paths = sys.path + os.environ["PATH"].split(os.pathsep)
            for path in search_paths:
                full_path = os.path.join(path, obj)  # noqa: PTH118
                if os.path.isfile(full_path):  # noqa: PTH113
                    _icon = QtGui.QIcon(full_path)
                    break
            if _icon is None:
                msg = f"Cannot find icon file {obj!r}"
                raise OSError(msg)
    elif isinstance(obj, QtWidgets.QStyle.StandardPixmap):
        app = application()
        _icon = QtGui.QIcon(app.style().standardIcon(obj))
    elif isinstance(obj, int):
        app = application()
        _icon = QtGui.QIcon(app.style().standardIcon(QtWidgets.QStyle.StandardPixmap(obj)))
    elif isinstance(obj, QtGui.QPixmap):
        _icon = QtGui.QIcon(obj)
    elif isinstance(obj, QtGui.QImage):
        _icon = QtGui.QIcon(QtGui.QPixmap.fromImage(obj))
    elif isinstance(obj, (bytes, bytearray, QtCore.QByteArray)):
        img = QtGui.QImage()
        if not img.loadFromData(QtCore.QByteArray.fromBase64(obj)):
            msg = "Cannot load image data from base64 bytes"
            raise ValueError(msg)
        _icon = QtGui.QIcon(QtGui.QPixmap.fromImage(img))

    if _icon is None:
        msg = f"Icon object has unsupported data type {type(obj)}"
        raise TypeError(msg)

    if size is None:
        return _icon

    return QtGui.QIcon(rescale_icon(_icon, size, aspect_mode=aspect_mode))


def icon_to_base64(  # noqa: C901, PLR0912, PLR0915
    icon: object, *, fmt: Literal["bmp", "jpg", "jpeg", "png"] = "png", dpm: int = 3780
) -> QtCore.QByteArray:
    """Convert an icon to a [QByteArray][QtCore.QByteArray] encoded as base64.

    Args:
        icon: Any object that is supported by [to_qicon][..to_qicon].
        fmt: The icon format to use when converting.
        dpm: The number of pixels that fit in a physical meter (dots-per-meter).

    Returns:
        The base64 representation of the icon.
    """
    if isinstance(icon, str) and "|" in icon:
        if sys.platform != "win32":
            msg = "Loading an icon from a DLL/EXE is only supported on Windows"  # pyright: ignore[reportUnreachable]
            raise OSError(msg)

        # extract an icon from a Windows DLL/EXE file
        shell32 = ctypes.windll.shell32
        s = icon.split("|")
        path = Path(s[0])
        icon_index = int(s[1])
        if icon_index < 0:
            msg = "The icon index must be >= 0"
            raise OSError(msg)

        if not path.is_file():
            err_msg = f"Cannot find DLL/EXE file '{path}'"
            if len(path.parts) > 1:  # then it wasn't just the filename that was specified
                raise OSError(err_msg)

            filename = path.stem
            path = Path(f"C:/Windows/System32/{filename}.dll")
            if not path.is_file():
                path = Path(f"C:/Windows/{filename}.exe")
                if not path.is_file():
                    raise OSError(err_msg)

        # extract the handle to the "large" icon
        path_ptr = ctypes.c_char_p(str(path).encode())
        h_icon = ctypes.c_int()
        res = shell32.ExtractIconExA(path_ptr, icon_index, ctypes.byref(h_icon), ctypes.c_void_p(), 1)
        if res == 0 or not h_icon.value:
            max_index = shell32.ExtractIconExA(path_ptr, -1, ctypes.c_void_p(), ctypes.c_void_p(), 0) - 1
            msg = f"Requested icon {icon_index}, the maximum icon index allowed is {max_index}"
            raise OSError(msg)

        # The `QImage.fromHICON` function is not included in the stubs on unix.
        # Using getattr keeps mypy and pyright happy, but upsets ruff which is okay.
        image: QtGui.QImage = getattr(QtGui.QImage, "fromHICON")(h_icon.value)  # noqa: B009
        ctypes.windll.user32.DestroyIcon(h_icon)
        if image.isNull():
            msg = "Qt failed to convert the HICON handle to a QImage"
            raise OSError(msg)

    else:
        icon = to_qicon(icon)
        try:
            size = icon.availableSizes()[-1]  # use the largest size as the default size
        except IndexError:
            msg = "Cannot determine a size of the QIcon"
            raise ValueError(msg) from None
        else:
            image = icon.pixmap(size).toImage()

    image.setDotsPerMeterX(dpm)
    image.setDotsPerMeterY(dpm)

    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)
    if not buffer.open(QtCore.QIODevice.OpenModeFlag.WriteOnly):
        msg = "Cannot open the QBuffer"
        raise ValueError(msg)
    if not image.save(buffer, fmt):  # type: ignore[call-overload] # pyright: ignore[reportCallIssue, reportArgumentType]
        msg = f"Cannot save the QImage to the QBuffer for format {fmt!r}"
        raise ValueError(msg)
    buffer.close()
    return array.toBase64(QtCore.QByteArray.Base64Option.Base64Encoding)


def rescale_icon(
    icon: object,
    size: Size | None,
    *,
    aspect_mode: QtCore.Qt.AspectRatioMode = QtCore.Qt.AspectRatioMode.KeepAspectRatio,
) -> QtGui.QPixmap:
    """Rescale an icon.

    Args:
        icon: Any object that is supported by [to_qicon][..to_qicon].
        size: Rescale the icon to the specified `size`.
            If an [int][] then set the width and the height to be the `size` value.
            If a [float][] then a scaling factor.
            If a [tuple][] then the `(width, height)` values.
        aspect_mode: How to maintain the aspect ratio if rescaling.
            The default mode is to keep the aspect ratio.

    Returns:
        A [QPixmap][QtGui.QPixmap] of the rescaled icon.
    """
    if isinstance(icon, QtGui.QIcon):
        try:
            pixmap = icon.pixmap(icon.availableSizes()[-1])
        except IndexError:
            msg = "Cannot automatically determine a size from the QIcon"
            raise ValueError(msg) from None
    elif isinstance(icon, QtGui.QPixmap):
        pixmap = icon
    else:
        return rescale_icon(to_qicon(icon), size, aspect_mode=aspect_mode)

    default_size = pixmap.size()
    if isinstance(size, int):
        size = QtCore.QSize(size, size)
    elif isinstance(size, float):
        size = QtCore.QSize(int(default_size.width() * size), int(default_size.height() * size))
    elif isinstance(size, (list, tuple)):
        size = QtCore.QSize(*size)
    elif not isinstance(size, QtCore.QSize):
        msg = f'Unsupported "size" type of {type(size)!r}'
        raise TypeError(msg)

    if (size.width() != default_size.width()) or (size.height() != default_size.height()):
        # PyQt uses aspectRatioMode as a kwarg (this is what the Qt docs indicate) however
        # PySide uses aspectMode. Therefore, don't specify a kwarg but use a positional
        # argument since both APIs have the aspect ratio mode as the second argument if
        # the first argument is a QSize
        pixmap = pixmap.scaled(size, aspect_mode)

    return pixmap


# cSpell: ignore AAAABJRU Jggg
def print_base64(
    icon: object,
    *,
    dpm: int = 3780,
    file: SupportsWrite[str] | None = None,
    line_width: int = 80,
    name: str = "icon",
    size: Size | None = None,
) -> None:
    """Print the base64 representation of an icon.

    Args:
        icon: Passed to [to_qicon][..to_qicon].
        dpm: The number of pixels that fit in a physical meter (dots-per-meter).
        file: Where to print the output. Default is [sys.stdout][].
        line_width: The maximum number of characters in a line.
        name: The variable name to assign to the icon.
        size: Passed to [to_qicon][..to_qicon].

    ```pycon
    >>> from msl.qt import print_base64
    >>> print_base64("docs/assets/images/favicon.ico", name="my_favicon", size=16)
    my_favicon = (
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

    ```
    """
    _ = application()
    b64 = bytes(icon_to_base64(to_qicon(icon, size=size), dpm=dpm).data())

    # 7 comes from the additional characters that are printed: <space><space><space><space>b""
    lines = textwrap.wrap(b64.decode(), width=line_width - 7)
    print(f"{name} = (", file=file)
    for line in lines:
        print(f'    b"{line}"', file=file)
    print(")", file=file)
