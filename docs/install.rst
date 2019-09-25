.. _qt-install:

=======
Install
=======

To install **MSL-Qt** run::

   pip install https://github.com/MSLNZ/msl-qt/archive/master.zip

Alternatively, using the `MSL Package Manager`_ run::

   msl install qt

Dependencies
------------
* Python 3.5+
* PyQt5_ or `Qt for Python`_ -- the Qt package that you want to use (you must install one, but the choice is yours)

You can automatically install one of these Qt packages when **MSL-Qt** is installed.

To also install PyQt5_::

   msl install qt[pyqt]

or, to also install `Qt for Python`_::

   msl install qt[pyside]

Optional Dependencies
+++++++++++++++++++++
* `Python for .NET`_ -- only required if you want to load icons from DLL/EXE files on Windows

.. _MSL Package Manager: http://msl-package-manager.readthedocs.io/en/latest/?badge=latest
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _Qt for Python: https://pypi.org/project/PySide2/
.. _Python for .NET: https://pypi.org/project/pythonnet/
