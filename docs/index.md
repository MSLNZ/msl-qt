# Overview

Custom [Qt] components for the graphical user interface (GUI).

## Prompt User

The [prompt][] module provides functions to create a window to either notify the user of an event that happened or to request input from the user. The functions are also convenient in scripts, not just in a GUI application.

```python
from msl.qt import DEGREE, prompt

angle = prompt.number(f"Enter an angle [{DEGREE}]", minimum=0, maximum=360)
```

<table>
  <colgroup>
    <col style="width: 20%;">
    <col style="width: 50%;">
    <col style="width: 30%;">
  </colgroup>
  <thead>
    <tr>
      <th>Prompt</th>
      <th>Description</th>
      <th>Example</th>
    </tr>
  </thead>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.comment">comment</a></td>
    <td>Prompt the user for a comment.</td>
    <td>
      <a href="assets/images/comment.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/comment.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.critical">critical</a></td>
    <td>Display a message in a dialog window using a <i>critical</i> alert icon.</td>
    <td>
      <a href="assets/images/critical.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/critical.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.file">file</a></td>
    <td>Select a file.</td>
    <td>
      <a href="assets/images/file.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/file.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.files">files</a></td>
    <td>Select multiple files.</td>
    <td>
      <a href="assets/images/files.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/files.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.folder">folder</a></td>
    <td>Select a folder.</td>
    <td>
      <a href="assets/images/folder.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/folder.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.information">information</a></td>
    <td>Display a message in a dialog window using an <i>information</i> alert icon.</td>
    <td>
      <a href="assets/images/information.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/information.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.integer">integer</a></td>
    <td>Prompt for an integer value.</td>
    <td>
      <a href="assets/images/integer.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/integer.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.item">item</a></td>
    <td>Prompt for an item from a sequence of items.</td>
    <td>
      <a href="assets/images/item.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/item.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.number">number</a></td>
    <td>Prompt for a floating-point number.</td>
    <td>
      <a href="assets/images/number.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/number.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.ok_cancel">ok_cancel</a></td>
    <td>Prompt for a response to a message where the logical options are <i>Ok</i> or <i>Cancel</i>.</td>
    <td>
      <a href="assets/images/ok_cancel.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/ok_cancel.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.password">password</a></td>
    <td>Prompt for a password.</td>
    <td>
      <a href="assets/images/password.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/password.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.save">save</a></td>
    <td>Select where to save a file.</td>
    <td>
      <a href="assets/images/save.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/save.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.text">text</a></td>
    <td>Prompt for text (a string).</td>
    <td>
      <a href="assets/images/text.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/text.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.warning">warning</a></td>
    <td>Display a message in a dialog window using a <i>warning</i> alert icon.</td>
    <td>
      <a href="assets/images/warning.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/warning.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.yes_no">yes_no</a></td>
    <td>Prompt for a response to a message where the logical options are <i>Yes</i> or <i>No</i>.</td>
    <td>
      <a href="assets/images/yes_no.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/yes_no.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/prompt/#msl.qt.prompt.yes_no_cancel">yes_no_cancel</a></td>
    <td>Prompt for a response to a message where the logical options are <i>Yes</i>, <i>No</i> or <i>Cancel</i>.</td>
    <td>
      <a href="assets/images/yes_no_cancel.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/yes_no_cancel.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
</table>

## Custom Widgets

The following widgets are provided, plus all of the [widget classes](https://doc.qt.io/qt-6/widget-classes.html) from [Qt] are available.

<table>
  <colgroup>
    <col style="width: 20%;">
    <col style="width: 50%;">
    <col style="width: 30%;">
  </colgroup>
  <thead>
    <tr>
      <th>Widget</th>
      <th>Description</th>
      <th>Example</th>
    </tr>
  </thead>
  <tr>
    <td><a href="api/widgets/button">Button</a></td>
    <td>A button to display text, an icon and a menu. The button supports a left-click and a right-click event.</td>
    <td>
      <a href="assets/images/button.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/button.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/checkbox">CheckBox</a></td>
    <td>A checkbox with a text label. A checkbox can be in either the checked, unchecked or partially-checked state.</td>
    <td>
      <a href="assets/images/checkbox.png" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/checkbox.png" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/combobox">ComboBox</a></td>
    <td>A combobox to select an item from a list of items. An item can include text, an icon and user data.</td>
    <td>
      <a href="assets/images/combobox.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/combobox.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/double_spinbox">DoubleSpinBox</a></td>
    <td>Enter a floating-point value using increment/decrement buttons, arrow keys, or direct text entry.</td>
    <td>
      <a href="assets/images/double_spinbox.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/double_spinbox.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/led">LED</a></td>
    <td>An LED (i.e., light-emitting diode) to signify two states &mdash; <i>on</i> and <i>off</i>.</td>
    <td>
      <a href="assets/images/led.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/led.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/line_edit">LineEdit</a></td>
    <td>A single line of editable text that can rescale the font size based on the widget size.</td>
    <td>
      <a href="assets/images/line_edit.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/line_edit.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/logger">Logger</a></td>
    <td>Display <a href="https://docs.python.org/3/library/logging.html#module-logging">logging</a> records.</td>
    <td>
      <a href="assets/images/logger.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/logger.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/spinbox">SpinBox</a></td>
    <td>Enter an integer value using increment/decrement buttons, arrow keys, or direct text entry.</td>
    <td>
      <a href="assets/images/spinbox.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/spinbox.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="api/widgets/toggle_switch">ToggleSwitch</a></td>
    <td>A toggle switch to signify two states &mdash; <i>on</i> and <i>off</i>.</td>
    <td>
      <a href="assets/images/toggle_switch.gif" target="_blank" rel="noopener noreferrer">
        <img src="assets/images/toggle_switch.gif" style="width: 100%; height: auto;">
      </a>
    </td>
  </tr>
</table>


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
