MSL-Qt
======

|docs| |travis| |appveyor|

This package provides custom Qt_ components that can be used for the graphical user interface.

Install
-------

To install **MSL-Qt** run

.. code-block:: console

   pip install https://github.com/MSLNZ/msl-qt/archive/main.zip

Alternatively, using the `MSL Package Manager`_

.. code-block:: console

   msl install qt

Dependencies
------------
* Python 3.6+
* PySide6_, PyQt6_, PySide2_ or PyQt5_ -- you can chose which Python binding you want to use

You can automatically install one of these Python bindings for the Qt framework when
**MSL-Qt** is installed. For example, to install PySide6_

.. code-block:: console

   msl install qt[PySide6]

or to install PyQt6_

.. code-block:: console

   msl install qt[PyQt6]

Optional Dependencies
+++++++++++++++++++++
* pythonnet_ -- only required if you want to load icons from DLL/EXE files on Windows

.. |docs| image:: https://readthedocs.org/projects/msl-qt/badge/?version=latest
   :target: http://msl-qt.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :scale: 100%

.. |travis| image:: https://img.shields.io/travis/MSLNZ/msl-qt/main.svg?label=Travis-CI
   :target: https://travis-ci.org/MSLNZ/msl-qt

.. |appveyor| image:: https://img.shields.io/appveyor/ci/jborbely/msl-qt/main.svg?label=AppVeyor
   :target: https://ci.appveyor.com/project/jborbely/msl-qt/branch/main

.. _Qt: https://www.qt.io/
.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/stable/
.. _PySide6: https://pypi.org/project/PySide6/
.. _PyQt6: https://pypi.org/project/PyQt6/
.. _PySide2: https://pypi.org/project/PySide2/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _pythonnet: https://pypi.org/project/pythonnet/
