"""
A wrapper over different Python Qt bindings (e.g., PyQt4_, PyQt5_, PySide_, PySide2_).

Currently only PyQt5_ and PySide2_ are supported.

Example repositories which unify the syntax for PyQt4_, PyQt5_, PySide_ and PySide2_:

* https://github.com/mottosso/Qt.py
* https://github.com/jupyter/qtconsole/blob/master/qtconsole/qt_loaders.py
* https://github.com/spyder-ide/qtpy
* https://github.com/pyQode/pyqode.qt
* https://github.com/silx-kit/silx/blob/master/silx/gui/qt/_qt.py

.. _PyQt4: http://pyqt.sourceforge.net/Docs/PyQt4/
.. _PyQt5: http://pyqt.sourceforge.net/Docs/PyQt5/
.. _PySide: https://wiki.qt.io/PySide
.. _PySide2: https://wiki.qt.io/PySide2
"""
import os
import sys

# Qt for Python (PySide2) is the project that provides the official
# set of Python bindings to Qt, see https://www.qt.io/qt-for-python
try:
    import PySide2
    has_pyside = True
    use_pyside = True
except ImportError:
    use_pyside = False
    has_pyside = False

try:
    import PyQt5
    has_pyqt = True
except ImportError:
    has_pyqt = False

# One can create a QT_API environment variable to select which Qt API is used.
# For example,
#   QT_API = 'PySide'
#   QT_API = 'PyQt'
# the value is case insensitive and independent of the version number at the end,
# for example, the following are equivalent to the above
#   QT_API = 'pyside2'
#   QT_API = 'pyqt5'
QT_API = os.getenv('QT_API', 'pyside').lower()
if QT_API.startswith('pyside'):
    use_pyside = has_pyside
elif QT_API.startswith('pyqt'):
    use_pyside = not has_pyqt
else:
    raise ValueError('Invalid environment variable QT_API -> {!r}'.format(QT_API))

# PySide2/PyQt5 is not required if building the documentation
# since the package gets mocked, see docs/conf.py
building_docs = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
if not building_docs and not (has_pyside or has_pyqt):
    raise ImportError('Either PySide2 or PyQt5 must be installed')

if building_docs and not has_pyside and not has_pyqt:
    raise ImportError(
        'To build the docs you must either install PySide2 or PyQt5.\n'
        'Alternatively, you can temporarily enable mocking in conf.py using\n'
        '  if on_rtd or True:\n'
        'WARNING!!! do not commit this temporary change to the conf.py file'
    )

if use_pyside:
    from PySide2 import QtGui
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtSvg
    Qt = QtCore.Qt
    Signal = QtCore.Signal
    Slot = QtCore.Slot
    if not hasattr(QtWidgets, 'QWIDGETSIZE_MAX'):
        QtWidgets.QWIDGETSIZE_MAX = (1 << 24) - 1
else:
    from PyQt5 import QtGui
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
    from PyQt5 import QtSvg
    Qt = QtCore.Qt
    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot


__all__ = (
    'Qt',
    'QtGui',
    'QtWidgets',
    'QtCore',
    'QtSvg',
    'Signal',
    'Slot',
)
