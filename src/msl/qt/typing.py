"""Custom type annotations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, TypeVar

from ._qt import QtCore, QtGui

Family = str | Sequence[str]
"""[QFont][QtGui.QFont] family name(s).

The family name may also include a foundry name, e.g., `"Helvetica [Cronyx]"`.
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
* If a [QtGui.QFont][], then the instance is used.
* If a [tuple][], then one of:
    - (family-name, point-size)
    - (family-name, point-size, weight)
    - (family-name, point-size, weight, italic)
"""

Filter = str | Sequence[str] | Mapping[str, str] | Mapping[str, Sequence[str]] | Mapping[str, str | Sequence[str]]
"""Apply filters to select or save a file.

Examples,

```python
"Images (*.png *.xpm *.jpg)"
"Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
["Images (*.png *.xpm *.jpg)", "Text files (*.txt)", "XML files (*.xml)"]
{"Images": ("*.png", "*.xpm", "*.jpg"), "Text files": "*.txt"}
```
"""

Color = (
    str | int | tuple[int, int, int] | tuple[int, int, int, int] | QtCore.Qt.GlobalColor | QtGui.QRgba64 | QtGui.QColor
)
"""Values that can be converted to a [QColor][QtGui.QColor]."""

Size = int | float | tuple[int, int] | QtCore.QSize
"""The size of a [QIcon][QtGui.QIcon]."""

_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsWrite(Protocol[_T_contra]):
    """A [file-like object][] that supports a `write` method."""

    def write(self, s: _T_contra, /) -> int:
        """Write to the stream."""
        ...
