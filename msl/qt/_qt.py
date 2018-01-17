"""
A wrapper over different Python Qt bindings (e.g., PyQt4_, PyQt5_, PySide_, PySide2_).

Currently only PyQt5_ is implemented.

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
from PyQt5 import Qt, QtWidgets, QtCore, QtGui
