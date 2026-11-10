"""Support different Python bindings for Qt."""

# cSpell: ignore PYSIDE mkdocstrings
# pyright: reportUnreachable=false
from __future__ import annotations

import importlib
import os
import sys
from base64 import b64decode
from typing import NamedTuple, cast

__all__: list[str] = [
    "Qt",
    "QtCore",
    "QtGui",
    "QtSvg",
    "QtWidgets",
    "Signal",
    "Slot",
    "application",
    "binding",
]

# the order in the tuple represents the search order when importing the package
packages = ["PySide6", "PyQt6"]

# one can create a QT_API environment variable to select which Qt API to use
qt_api = os.getenv("QT_API")
if qt_api:
    if qt_api not in packages:
        msg = f"Invalid environment variable QT_API={qt_api} (the value must be {' or '.join(packages)})"
        raise ValueError(msg)
else:
    for package in packages:
        try:
            _ = importlib.import_module(package)
        except ImportError:  # noqa: PERF203
            continue
        else:
            qt_api = package
            break


class Binding(NamedTuple):
    """The Python binding for the Qt framework."""

    name: str
    """Name of the Python package that binds the Qt framework."""

    version: str
    """Binding package version."""

    qt_version: str
    """Qt version."""

    version_info: tuple[int, int, float, str, str]
    """Binding package version information."""

    qt_version_info: tuple[int, int, int]
    """Qt version information."""


PYQT6 = qt_api == "PyQt6"
PYSIDE6 = qt_api == "PySide6"

if PYQT6:
    from PyQt6 import QtCore, QtGui, QtSvg, QtWidgets

    def to_version_info(version: int) -> tuple[int, int, int]:
        major = (version >> 16) & 0xFF
        minor = (version >> 8) & 0xFF
        patch = version & 0xFF
        return major, minor, patch

    Signal = QtCore.pyqtSignal
    SignalInstance = QtCore.pyqtBoundSignal
    Slot = QtCore.pyqtSlot
    binding = Binding(
        name="PyQt6",
        version=QtCore.PYQT_VERSION_STR,
        qt_version=QtCore.QT_VERSION_STR,
        version_info=(*to_version_info(QtCore.PYQT_VERSION), "", ""),
        qt_version_info=to_version_info(QtCore.QT_VERSION),
    )

elif PYSIDE6:  # must come after PYQT6 for mkdocstrings-python to use it
    from PySide6 import QtCore, QtGui, QtSvg, QtWidgets, __version__, __version_info__

    Signal = QtCore.Signal
    SignalInstance = QtCore.SignalInstance
    Slot = QtCore.Slot
    binding = Binding(
        name="PySide6",
        version=__version__,
        qt_version=QtCore.__version__,  # type: ignore[attr-defined]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        version_info=__version_info__,
        qt_version_info=QtCore.__version_info__,  # type: ignore[attr-defined]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
    )

else:
    msg = f"Either {' or '.join(packages)} must be installed"
    raise ImportError(msg)


Qt = QtCore.Qt

# PyQt6 uses scoped enums. Support unscoped enums to be consistent with PySide6.
if PYQT6:
    from enum import EnumMeta
    from inspect import getmembers, isclass

    def is_enum(obj: object) -> bool:
        return isinstance(obj, EnumMeta)

    for obj in (QtCore, QtWidgets, QtGui, QtSvg):
        for _, cls in getmembers(obj, isclass):
            for _, enum in getmembers(cls, is_enum):
                for name, value in enum.__members__.items():
                    setattr(cls, name, value)


def application(*args: str) -> QtWidgets.QApplication:
    """Returns the Qt application instance (creating one if necessary).

    Args:
        args: Arguments to initialize the application. If not specified, [sys.argv][] is used.

    Returns:
        The application instance.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(list(args) if args else sys.argv)

        # use a default MSL logo as the app icon
        logo = (
            b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHR"
            b"Db21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAAx9JREFUWIXNlk9oXFUYxX/fnZmmmQ6aVt+rBCsEgo"
            b"UWLBNjRUg0sxA3ihsHEwKiGxcWQ1ZunYIrt0IpuunKRKYgal0I2j47qIsmThTqQvy3i2m0pqmkSX3vHhfJj"
            b"KWT1OmbNPSs3rvvnu+e+/19RkosjhZ7ZRwHCsHB+rhV8GnsuLQC4gw9gpcFo1wsW1o72bRExSacdOPawljx"
            b"ayCWceKB9+vTd1TAFngCwMGn7RJSC1jrvufX/NryoCnJWLWapLWTWkDfqWgV+D4tv4HUSbhd2O4cuCUWx4p"
            b"PeXgbyIRx/+NWrSZ3VMDv4wPPmudJpF/2T9dPSgQYR9fVLBp04IFL5cMFsl1DHnL7p749Y6CWTdLTwATGN8"
            b"BJWeue9I3IdR0Q+sjQx5TLm9oxEW88/rOVndQCHHEG2HU7HMlaPJ46BNe69/2UX1s+4rxl2+0DXbv9Z/F1N"
            b"4iXEUVJRwIKq1f2JaZJ71xBFUbbGUZ7T80tAbM3rnU0jAx7CVTuZBilFqDYBJvfWo3cMHVtvOe3stN2CObH"
            b"i4dMPGLSajjfc2ae5ZY94fy9OQBGIg8QPjw3QTQySRAI6p0JcJ4XgONgSwsHLj/I9VaqRdF62UUb7xU8RLf"
            b"MjU0FCGxhdGASU58T58Pp+ul2hd4utswBM/+iwesyK232PUeSAH8A1zhcbe2CbSJ1GQYffPcj0JuW30DTAw"
            b"ITpC6ntGh64NJY8SqwtIBeYWru8x0XAOwB9gi3+3848ku51DG/GW03ovBg/a0w7s+GcX/Q+8nsynYJuDkJP"
            b"W5jZsuEgSQPjZqubte5dw+aWb8wVvwNuOJgIpiqf7lTApohEDprxkqS+D936vC7As0QlIYefddgRXLvnfvq"
            b"wg+l4cFJPH1ynI9qM6dLwwPPIPecsKvBXytvXi4U9vpc8oaMfFSbeQ1QaeixEyCP2Yfnahe+KA0PPm9SCeP"
            b"ns7XZd0pDR49A8qrM3Eht5lgF/H9lKAuFC5KM1me5V48ZAVgBwJTNgwLD3/f3Q2sm57LA/SbCSuMiUggKpK"
            b"QbQN4KwgXy9AA4r13gAhPhxfL6T8y/FrQlyIjl7wYAAAAASUVORK5CYII="
        )

        pixmap = QtGui.QPixmap()
        if pixmap.loadFromData(b64decode(logo)):
            app.setWindowIcon(QtGui.QIcon(pixmap))

    return cast("QtWidgets.QApplication", app)
