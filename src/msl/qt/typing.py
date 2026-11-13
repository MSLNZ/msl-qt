"""Custom type annotations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, TypeVar

from ._qt import QtCore, QtGui

Family = str | Sequence[str]
"""[QFont][QtGui.QFont] family name(s).

The family name may also include a foundry name, e.g., `#!py "Helvetica [Cronyx]"`.
"""

PointSize = int | float
"""[QFont][QtGui.QFont] point size."""

Weight = int | QtGui.QFont.Weight
"""[QFont][QtGui.QFont] weighting scale (from 1 to 1000).

A weight of 1 is thin, 400 is normal and 1000 is thick.
"""

Font = (
    PointSize
    | Family
    | QtGui.QFont
    | tuple[Family, PointSize]
    | tuple[Family, PointSize, Weight]
    | tuple[Family, PointSize, Weight, bool]
)
"""Values that can be converted to a [QFont][QtGui.QFont].

* If an [int][], then the point size.
* If a [str][], then the font family name.
* If a [QtGui.QFont][], then a copy is returned.
* If a [tuple][], then one of:
    - (family-name, point-size)
    - (family-name, point-size, weight)
    - (family-name, point-size, weight, italic)
"""

Filter = str | Sequence[str] | Mapping[str, str] | Mapping[str, Sequence[str]] | Mapping[str, str | Sequence[str]]
"""Apply filters to select or save a file.

Examples,

* [str][] &mdash; `#!py "Images (*.bmp *.jpg *.png)"`
* [str][] &mdash; `#!py "Images (*.bmp *.jpg *.png);;Text files (*.txt)"`
* [list][] &mdash; `#!py ["Images (*.bmp *.jpg *.png)", "Text files (*.txt)"]`
* [dict][] &mdash; `#!py {"Images": ("*.bmp", "*.jpg", "*.png"), "Text files": "*.txt"}`
"""

Color = (
    str | int | tuple[int, int, int] | tuple[int, int, int, int] | QtCore.Qt.GlobalColor | QtGui.QRgba64 | QtGui.QColor
)
"""Values that can be converted to a [QColor][QtGui.QColor].

See [here][PySide6.QtGui.QColor.fromString] for supported [str][] values.

If a single [int][], then the 0xRRGGBB hex value, e.g, `#!py 0xFF8800` &rarr; Red:255, Green:136, Blue:0

If a [tuple][], then either (Red, Green, Blue) or (Red, Green, Blue, Alpha) values in the range [0, 255].
"""

Size = int | float | tuple[int, int] | QtCore.QSize
"""The size of a [QIcon][QtGui.QIcon].

If an [int][], then the width and the height are set to this value.

If a [float][], then a scaling factor to apply to the default icon size.

If a [tuple][], then the `(width, height)`.
"""

_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsWrite(Protocol[_T_contra]):
    """A [file-like object][] that supports a `write` method."""

    def write(self, s: _T_contra, /) -> int:
        """Write to the stream."""
        ...
