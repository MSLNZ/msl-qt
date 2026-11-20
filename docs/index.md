# Overview

Custom [Qt] components for the graphical user interface.

## Install
`msl-qt` is available at the [Python Package Index](https://pypi.org/project/msl-qt/). It can be installed using a variety of package managers

=== "pip"
    ```console
    pip install msl-qt
    ```

=== "uv"
    ```console
    uv add msl-qt
    ```

=== "poetry"
    ```console
    poetry add msl-qt
    ```

=== "pdm"
    ```console
    pdm add msl-qt
    ```

### Dependencies
* Python 3.8+
* [PySide6] or [PyQt6] &mdash; you can chose which Python binding you want to use

You can install one of these Python bindings for the Qt Framework when `msl-qt` is installed.

For [PySide6],

=== "pip"
    ```console
    pip install msl-qt[PySide6]
    ```

=== "uv"
    ```console
    uv add msl-qt[PySide6]
    ```

=== "poetry"
    ```console
    poetry add msl-qt[PySide6]
    ```

=== "pdm"
    ```console
    pdm add msl-qt[PySide6]
    ```

or for [PyQt6]

=== "pip"
    ```console
    pip install msl-qt[PyQt6]
    ```

=== "uv"
    ```console
    uv add msl-qt[PyQt6]
    ```

=== "poetry"
    ```console
    poetry add msl-qt[PyQt6]
    ```

=== "pdm"
    ```console
    pdm add msl-qt[PyQt6]
    ```

!!! note
    The `msl-qt` package is not meant to be used as an general purpose abstraction layer for PyQt5, PySide2, PyQt6 and PySide6.
    You may want to consider using [qtpy](https://github.com/spyder-ide/qtpy) if that is what you are looking for.
    Only some [Qt] modules and classes are abstracted (for PyQt6/PySide6) to provide a uniform interface (see [API](api/index.md)).


## Type Checker Integration

If you are using [mypy] or [pyright]/[pylance] to check your code for type annotations, you can configure these tools to use the particular binding ([PySide6] or [PyQt6]) that you are using. Two constants are defined in the `msl-qt` package: `PYSIDE6` and `PYQT6` (of type [bool][]). You configure these tools by defining one constant as `true` and the other as `false`.

### mypy

For the mypy configuration example we show `PYQT6` as `true`, but enable the binding you are using.

=== "mypy.ini"
    ```ini
    [mypy]
    always_true = PYQT6
    always_false = PYSIDE6
    ```

=== "pyproject.toml"
    ```toml
    [tool.mypy]
    always_true = ["PYQT6"]
    always_false = ["PYSIDE6"]
    ```

=== "cli"
    ```console
    mypy --always-true=PYQT6 --always-false=PYSIDE6 ...
    ```

### pyright

For the pyright configuration example we show `PYSIDE6` as `true`, but enable the binding you are using.

=== "pyrightconfig.json"
    ```json
    {
        "defineConstant": {
            "PYQT6": false,
            "PYSIDE6": true
        }
    }
    ```

=== "pyproject.toml"
    ```toml
    [tool.pyright]
    defineConstant = { PYQT6 = false, PYSIDE6 = true }
    ```

[Qt]: https://www.qt.io/
[PySide6]: https://doc.qt.io/qtforpython-6/
[PyQt6]: https://www.riverbankcomputing.com/software/pyqt/
[mypy]: https://mypy.readthedocs.io/en/stable/index.html
[pyright]: https://microsoft.github.io/pyright
[pylance]: https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
