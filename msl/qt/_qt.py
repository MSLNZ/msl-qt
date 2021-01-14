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
        raise ValueError('Invalid QT_API environment variable {!r}'.format(qt_api))
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

Binding = namedtuple('Binding', ['name', 'version', 'qt_version'])

api = importlib.import_module(qt_api)
QtGui = importlib.import_module(qt_api + '.QtGui')
QtCore = importlib.import_module(qt_api + '.QtCore')
QtWidgets = importlib.import_module(qt_api + '.QtWidgets')
QtSvg = importlib.import_module(qt_api + '.QtSvg')
Qt = QtCore.Qt

if qt_api.startswith('PySide'):
    Signal = QtCore.Signal
    Slot = QtCore.Slot
    binding = Binding(name=api.__name__, version=api.__version__, qt_version=QtCore.__version__)
else:
    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    binding = Binding(name=api.__name__, version=QtCore.PYQT_VERSION_STR, qt_version=QtCore.QT_VERSION_STR)

if not hasattr(QtWidgets.QApplication, 'exec'):
    QtWidgets.QApplication.exec = QtWidgets.QApplication.exec_

if not hasattr(QtWidgets.QDialog, 'exec'):
    QtWidgets.QDialog.exec = QtWidgets.QDialog.exec_

# PyQt6 uses scoped enums. Want to support unscoped enums to be
# consistent with PySide6, PySide2 and PyQt5
if qt_api == 'PyQt6':
    from enum import EnumMeta
    from inspect import getmembers, isclass

    def isenum(obj):
        return isinstance(obj, EnumMeta)

    for qt in (QtCore, QtWidgets, QtGui):
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
