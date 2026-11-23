# Qt Abstraction

Whether you use [PySide6] or [PyQt6] as the [binding][] to the [Qt] Framework, the following [Qt] modules and classes are importable from the top level.

```python
from msl.qt import (
    Property,
    Qt,
    QtCore,
    QtGui,
    QtSvg,
    QtWidgets,
    Signal,
    Slot,
)
```

## PyQt6 Compatibility

If you are using [PyQt6] as the [binding][], the following aliases should be used instead.

| PyQt6                 | Alias                               |
| --------------------- | ----------------------------------- |
| `QtCore.pyqtProperty` | [Property][msl.qt.binding.Property] |
| `QtCore.pyqtSignal`   | [Signal][msl.qt.binding.Signal]     |
| `QtCore.pyqtSlot`     | [Slot][msl.qt.binding.Slot]         |

Unscoped enum access is supported for the `QtCore`, `QtWidgets`, `QtGui`, `QtSvg` modules. For example,

```pycon
>>> from msl.qt import Qt
>>> assert Qt.AlignmentFlag.AlignLeft == Qt.AlignLeft

```

## Qt Application

You can create, or get the instance of, the [QApplication][PySide6.QtWidgets.QApplication] by calling the [application][msl.qt.binding.application] function.

```pycon
>>> from msl.qt import application
>>> app = application()
>>> assert app is application()

```

## Qt Binding

You can access information about which [binding][] is used,

```pycon
>>> from msl.qt import binding

```

which is an instance of [Binding][msl.qt.binding.Binding].

<!--
>>> from msl.qt.binding import Binding
>>> binding = Binding(name='PySide6', version='', qt_version='6.12.0', version_info=(), qt_version_info=())

-->

```pycon
>>> binding.name
'PySide6'
>>> binding.qt_version
'6.12.0'

```

[Qt]: https://www.qt.io/
[PySide6]: https://doc.qt.io/qtforpython-6/
[PyQt6]: https://www.riverbankcomputing.com/software/pyqt/
