"""Custom [Qt](https://www.qt.io/) components for the graphical user interface."""

from __future__ import annotations

from . import convert, prompt, utils
from ._qt import (
    Qt,
    QtCore,
    QtGui,
    QtSvg,
    QtWidgets,
    Signal,
    Slot,
    application,
    binding,
)
from .characters import (
    DEGREE,
    DEGREE_C,
    DEGREE_F,
    GREEK,
    INFINITY,
    MICRO,
    PLUS_MINUS,
)
from .convert import (
    icon_to_base64,
    number_to_si,
    print_base64,
    rescale_icon,
    si_to_number,
    to_qcolor,
    to_qfont,
    to_qicon,
)
from .exceptions import excepthook
from .loop_until_abort import LoopUntilAbort
from .sleep import Sleep
from .threading import Thread, Worker
from .widgets import LED, Button, CheckBox, ComboBox, DoubleSpinBox, LineEdit, Logger, SpinBox, ToggleSwitch

__all__: list[str] = [
    "DEGREE",
    "DEGREE_C",
    "DEGREE_F",
    "GREEK",
    "INFINITY",
    "LED",
    "MICRO",
    "PLUS_MINUS",
    "Button",
    "CheckBox",
    "ComboBox",
    "DoubleSpinBox",
    "LineEdit",
    "Logger",
    "LoopUntilAbort",
    "Qt",
    "QtCore",
    "QtGui",
    "QtSvg",
    "QtWidgets",
    "Signal",
    "Sleep",
    "Slot",
    "SpinBox",
    "Thread",
    "ToggleSwitch",
    "Worker",
    "application",
    "binding",
    "convert",
    "excepthook",
    "icon_to_base64",
    "number_to_si",
    "print_base64",
    "prompt",
    "rescale_icon",
    "si_to_number",
    "to_qcolor",
    "to_qfont",
    "to_qicon",
    "utils",
]
