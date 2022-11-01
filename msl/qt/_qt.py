"""
A wrapper for different Python bindings for Qt.
"""
import os
import importlib
from collections import namedtuple

# the order in the tuple represents the search order when importing the package
packages = ('PySide6', 'PyQt6', 'PySide2', 'PyQt5')

# one can create a QT_API environment variable to select which Qt API to use
qt_api = os.getenv('QT_API')
if qt_api:
    if qt_api not in packages:
        raise ValueError(f'Invalid QT_API environment variable {qt_api!r}')
else:
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            continue
        else:
            qt_api = package
            break

if not qt_api:
    raise ImportError('One of the following Qt packages must be installed: ' + ', '.join(packages))

Binding = namedtuple('Binding', ['name', 'version', 'qt_version', 'version_info', 'qt_version_info'])

# do not use, for example, QtGui = importlib.import_module(qt_api + '.QtGui')
# for the following because this does not allow for IDE's to use autocompletion
if qt_api == 'PyQt5':
    import PyQt5 as api
    from PyQt5 import QtGui
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
    from PyQt5 import QtSvg
elif qt_api == 'PySide2':
    import PySide2 as api
    from PySide2 import QtGui
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtSvg
elif qt_api == 'PyQt6':
    import PyQt6 as api
    from PyQt6 import QtGui
    from PyQt6 import QtCore
    from PyQt6 import QtWidgets
    from PyQt6 import QtSvg
else:
    import PySide6 as api
    from PySide6 import QtGui
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtSvg

Qt = QtCore.Qt

if qt_api.startswith('PyQt'):
    def to_version_info(version):
        major = (version >> 16) & 0xff
        minor = (version >> 8) & 0xff
        patch = version & 0xff
        return major, minor, patch

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    binding = Binding(
        name=api.__name__,
        version=QtCore.PYQT_VERSION_STR,
        qt_version=QtCore.QT_VERSION_STR,
        version_info=to_version_info(QtCore.PYQT_VERSION),
        qt_version_info=to_version_info(QtCore.QT_VERSION),
    )
else:
    Signal = QtCore.Signal
    Slot = QtCore.Slot
    binding = Binding(
        name=api.__name__,
        version=api.__version__,
        qt_version=QtCore.__version__,
        version_info=api.__version_info__,
        qt_version_info=QtCore.__version_info__,
    )

if not hasattr(QtWidgets.QApplication, 'exec'):
    QtWidgets.QApplication.exec = QtWidgets.QApplication.exec_

if not hasattr(QtWidgets.QDialog, 'exec'):
    QtWidgets.QDialog.exec = QtWidgets.QDialog.exec_

# PyQt6 uses scoped enums. Want to support unscoped enums to be
# consistent with PySide6 (<6.4), PySide2 and PyQt5.
# Starting from PySide 6.4, enums also became scope. Although, the
# Qt for Python developers introduced something called a "forgiveness mode",
# this "mode" was found to not be 100% reliable
if qt_api == 'PyQt6' or binding.version_info[:2] >= (6, 4):
    from enum import EnumMeta
    from inspect import getmembers, isclass

    def isenum(obj):
        return isinstance(obj, EnumMeta)

    for qt in (QtCore, QtWidgets, QtGui, QtSvg):
        for _, cls in getmembers(qt, isclass):
            for _, enum in getmembers(cls, isenum):
                for item in enum:
                    setattr(cls, item.name, item)

# make Qt5 to be compatible with Qt6
if qt_api in ('PySide2', 'PyQt5'):

    # QAction and QActionGroup were moved from QtWidgets (Qt5) to QtGui (Qt6)
    QtGui.QAction = QtWidgets.QAction
    QtGui.QActionGroup = QtWidgets.QActionGroup


__all__ = (
    'Qt',
    'QtGui',
    'QtWidgets',
    'QtCore',
    'QtSvg',
    'Signal',
    'Slot',
    'binding',
)
