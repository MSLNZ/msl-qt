"""Convenience functions to prompt the user.

The following functions create a dialog window to either notify the user of an
event that happened or to request input from the user.

The functions in this module are importable at the top level,

```pycon
>>> from msl.qt import comment, critical

```

or you can import the module.

```pycon
>>> from msl.qt import prompt

```
"""

from __future__ import annotations

import json
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .binding import Qt, QtGui, QtWidgets, Slot, application
from .utils import rescale_icon, screen_geometry, to_qfont, to_qicon

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from .typing import Filter, Font

__all__: list[str] = [
    "comment",
    "critical",
    "file",
    "files",
    "folder",
    "information",
    "integer",
    "item",
    "number",
    "ok_cancel",
    "password",
    "save",
    "text",
    "warning",
    "yes_no",
    "yes_no_cancel",
]


def critical(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using a _critical_ alert icon.

    !!! note "See also"
        [information][..information], [warning][..warning]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py 'A <span style="color:red"><i>critical</i></span> error occurred!'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    if font is None:
        mb.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    else:
        icon = _message_box_icon(mb, QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
        mb.setIconPixmap(icon)
    _ = mb.exec()


def number(
    message: str,
    *,
    title: str | None = None,
    font: Font | None = None,
    value: float = 0,
    minimum: float | None = None,
    maximum: float | None = None,
    step: float = 1,
    decimals: int = 2,
) -> float | None:
    """Prompt for a floating-point number.

    !!! note "See also"
        [integer][..integer]

    Args:
        message: The message that is shown to the user to describe what the value represents.
            The message can use HTML/CSS markup, e.g., `#!py "Enter an angle [<b>&deg;</b>]"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        value: The initial value.
        minimum: The minimum value that the user can enter.
        maximum: The maximum value that the user can enter.
        step: The step size by which the value can be increased and decreased
            (by pressing the arrow keys or clicking the arrow buttons).
        decimals: The number of digits that are displayed after the decimal point.

    Returns:
        The value or `None` if the dialog was cancelled.
    """
    info = sys.float_info
    mn = info.min if minimum is None else minimum
    mx = info.max if maximum is None else maximum
    _, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setInputMode(QtWidgets.QInputDialog.InputMode.DoubleInput)
    dialog.setDoubleRange(mn, mx)
    dialog.setDoubleStep(step)
    dialog.setDoubleDecimals(decimals)
    dialog.setDoubleValue(value)
    ok = dialog.exec()
    return dialog.doubleValue() if ok else None


def file(
    *,
    title: str | None = "Select File",
    directory: str | Path | None = None,
    filters: Filter | None = None,
) -> str:
    """Select a file.

    !!! note "See also"
        [files][..files], [folder][..folder], [save][..save]

    Args:
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        directory: The initial directory to start in.
        filters: Only files that match the specified `filters` are shown.

    Returns:
        The path of the file that was selected. Returns an empty string if the dialog was cancelled.
    """
    d = "" if directory is None else str(directory)
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    name, _ = QtWidgets.QFileDialog.getOpenFileName(app.activeWindow(), title, d, filters)
    return name


def files(
    *,
    title: str | None = "Select Files",
    directory: str | Path | None = None,
    filters: Filter | None = None,
) -> list[str]:
    """Select multiple files.

    !!! note "See also"
        [file][..file], [folder][..folder], [save][..save]

    Args:
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        directory: The initial directory to start in.
        filters: Only files that match the specified `filters` are shown.

    Returns:
        The paths of the files that were selected. Returns an empty list if the dialog was cancelled.
    """
    d = "" if directory is None else str(directory)
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    names, _ = QtWidgets.QFileDialog.getOpenFileNames(app.activeWindow(), title, d, filters)
    return names


def folder(*, title: str | None = "Select Folder", directory: str | Path | None = None) -> str:
    """Select a folder.

    !!! note "See also"
        [file][..file], [files][..files], [save][..save]

    Args:
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        directory: The initial directory to start in.

    Returns:
        The path of the selected folder. Returns an empty string if the dialog was cancelled.
    """
    d = "" if directory is None else str(directory)
    app, title = _get_app_and_title(title)
    return QtWidgets.QFileDialog.getExistingDirectory(app.activeWindow(), title, d)


def information(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using an _information_ alert icon.

    !!! note "See also"
        [critical][..critical], [warning][..warning]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py "<html>Laser is at 30.2&deg;C</html>"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    if font is None:
        mb.setIcon(QtWidgets.QMessageBox.Icon.Information)
    else:
        icon = _message_box_icon(mb, QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation)
        mb.setIconPixmap(icon)
    _ = mb.exec()


def integer(
    message: str,
    *,
    title: str | None = None,
    font: Font | None = None,
    value: int = 0,
    minimum: int | None = None,
    maximum: int | None = None,
    step: int = 1,
) -> int | None:
    """Prompt for an integer value.

    !!! note "See also"
        [number][..number]

    Args:
        message: The message that is shown to the user to describe what the value represents.
            The message can use HTML/CSS markup, e.g., `#!py "Enter a mass [<b>&mu;g</b>]"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        value: The initial value.
        minimum: The minimum value that the user can enter.
        maximum: The maximum value that the user can enter.
        step: The step size by which the value can be increased and decreased
            (by pressing the arrow keys or clicking the arrow buttons).

    Returns:
        The value or `None` if the dialog was cancelled.
    """
    mn = -0x80000000 if minimum is None else minimum
    mx = 0x7FFFFFFF if maximum is None else maximum
    _, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setInputMode(QtWidgets.QInputDialog.InputMode.IntInput)
    dialog.setIntRange(mn, mx)
    dialog.setIntStep(step)
    dialog.setIntValue(value)
    ok = dialog.exec()
    return dialog.intValue() if ok else None


def item(
    message: str,
    items: Sequence[Any],
    *,
    title: str | None = None,
    font: Font | None = None,
    index: int = 0,
) -> Any:  # noqa: ANN401
    """Prompt for an item from a sequence of items.

    Args:
        message: The message that is shown to the user to describe what the
            sequence of items represent. The message can use HTML/CSS markup, e.g.,
            `#!py "Choose a <i>gain</i> factor"`
        items: The items to choose from. The items can be of any data type,
            the string representation of each item is displayed in the dialog window.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        index: The index of the initial item that is selected.

    Returns:
        The selected item or `None` if the user cancelled the request.
            The data type of the selected item is preserved. For example, if
            `#!py items=[True, 1, 2.2, "hello"]` and the user selects `#!py 2.2`,
            then `#!py 2.2` as a [float][] data type is returned.
    """
    strings = [str(i) for i in items]
    _, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setComboBoxItems(strings)
    dialog.setTextValue(strings[index])
    dialog.setComboBoxEditable(False)
    dialog.setInputMethodHints(Qt.InputMethodHint.ImhNone)
    ok = dialog.exec()
    return items[strings.index(dialog.textValue())] if ok else None


def comment(*, path: str | Path | None = None, title: str | None = None) -> str:
    """Prompt the user for a comment.

    Opens a [QDialog][QtWidgets.QDialog] to allow a user to enter a comment about
    a task that they are performing. The dialog provides a table of all the previous
    comments that have been used. A comment that is in the table can be selected by
    double clicking a row. You can delete comments from the table by selecting the
    desired row(s) and then pressing the `Delete` key.

    This function is useful when acquiring data and you want to get a comment about
    how the data was/will be acquired. Using a prompt to get a comment forces you to
    enter a comment, or select and modify a previous comment, every time you acquire
    data rather than having the comment as a constant in your program, which you might
    forget to update before acquiring the next data run.

    !!! example "Run the example"
        ```console
        python -c "from msl.examples.qt import run; run('Comment')"
        ```

        ??? abstract "Click to view the example source code"
            ```python
            --8<-- "src/msl/examples/qt/comment.py"
            ```

    !!! note "See also"
        [password][..password], [text][..text]

    Args:
        path: The path to a [JSON](https://www.json.org/) file that contains the history
            of the comments that have been entered. If `None`, the default path is used.
            The file is created if it does not exist.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.

    Returns:
        The comment.
    """
    _, title = _get_app_and_title(title)
    p = Path(path) if path else (Path("~/.msl").expanduser() / "msl-qt-comments.json")
    c = _Comment(p)
    c.setWindowTitle(title)
    _ = c.exec()
    return c.text()


def save(
    *,
    title: str = "Save As",
    directory: str | Path | None = None,
    filters: Filter | None = None,
    options: QtWidgets.QFileDialog.Option | None = None,
) -> str:
    """Select where to save a file.

    !!! note "See also"
        [file][..file], [files][..files], [folder][..folder]

    Args:
        title: The text to display in the title bar of the dialog window.
        directory: The initial directory to start in.
        filters: Only files that match the specified `filters` are shown.
        options: Additional options on how to run the dialog.

    Returns:
        The file path. Returns an empty string if the dialog was cancelled.
    """
    d = "" if directory is None else str(directory)
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    if options is None:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, d, filters)
    else:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, d, filters, options=options)
    return name


def text(
    message: str,
    *,
    title: str | None = None,
    font: Font | None = None,
    value: str | None = None,
    multi_line: bool = False,
    echo: QtWidgets.QLineEdit.EchoMode = QtWidgets.QLineEdit.EchoMode.Normal,
) -> str:
    """Prompt for text (a string).

    !!! note "See also"
        [comment][..comment], [password][..password]

    Args:
        message: The message that is shown to the user. The message can use HTML/CSS markup, e.g.,
            `#!py "Enter a <i>hostname</i> or <i>IP address</i>"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        value: The initial value.
        multi_line: Whether the entered text can span multiple lines.
        echo: How the entered content should be displayed.

    Returns:
        The text that was entered.
    """
    _, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setTextValue(value or "")
    dialog.setInputMethodHints(Qt.InputMethodHint.ImhNone)
    dialog.setTextEchoMode(echo)
    if multi_line:
        dialog.setOption(QtWidgets.QInputDialog.InputDialogOption.UsePlainTextEditForTextInput)
    _ = dialog.exec()
    return dialog.textValue().strip()


def password(message: str, *, title: str | None = None, font: Font | None = None) -> str:
    """Prompt for a password.

    Replaces entered characters with a platform-specific mask symbol.

    !!! note "See also"
        [comment][..comment], [text][..text]

    Args:
        message: The message that is shown to the user. The message can use HTML/CSS markup, e.g.,
            `#!py "Enter <b>secure</b> password"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.

    Returns:
        The password.
    """
    return text(message, title=title, font=font, echo=QtWidgets.QLineEdit.EchoMode.Password)


def warning(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using a _warning_ alert icon.

    !!! note "See also"
        [critical][..critical], [information][..information]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py 'A <span style="color:yellow">warning</span> message'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    if font is None:
        mb.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    else:
        icon = _message_box_icon(mb, QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning)
        mb.setIconPixmap(icon)
    _ = mb.exec()


def ok_cancel(message: str, *, title: str | None = None, font: Font | None = None, default: bool = True) -> bool:
    """Prompt for a response to a message where the logical options are _Ok_ or _Cancel_.

    !!! note "See also"
        [yes_no][..yes_no], [yes_no_cancel][..yes_no_cancel]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py 'Change the current to <span style="color:red">60 mA</span>?'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then _Ok_ is selected,
            otherwise _Cancel_ is selected.

    Returns:
        `True` if _Ok_ was clicked, otherwise `False` if _Cancel_ was clicked.
    """
    ok = QtWidgets.QMessageBox.StandardButton.Ok
    cancel = QtWidgets.QMessageBox.StandardButton.Cancel
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Question)
    mb.setStandardButtons(ok | cancel)
    mb.setDefaultButton(ok if default else cancel)
    return mb.exec() == ok


def yes_no(message: str, *, title: str | None = None, font: Font | None = None, default: bool = True) -> bool:
    """Prompt for a response to a message where the logical options are _Yes_ or _No_.

    !!! note "See also"
        [ok_cancel][..ok_cancel], [yes_no_cancel][..yes_no_cancel]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py 'Change the current to <span style="color:red">60 mA</span>?'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then _Yes_ is selected,
            otherwise _No_ is selected.

    Returns:
        `True` if _Yes_ was clicked, otherwise `False` if _No_ was clicked.
    """
    yes = QtWidgets.QMessageBox.StandardButton.Yes
    no = QtWidgets.QMessageBox.StandardButton.No
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Question)
    mb.setStandardButtons(yes | no)
    mb.setDefaultButton(yes if default else no)
    return mb.exec() == yes


def yes_no_cancel(
    message: str, *, title: str | None = None, font: Font | None = None, default: bool | None = True
) -> bool | None:
    """Prompt for a response to a message where the logical options are _Yes_, _No_ or _Cancel_.

    !!! note "See also"
        [ok_cancel][..ok_cancel], [yes_no][..yes_no]

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py 'Change the current to <span style="color:red">60 mA</span>?'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then _Yes_ is selected,
            if `False` then _No_ is selected, if `None` then _Cancel_ is selected.

    Returns:
        `True` if _Yes_ was clicked, `False` if _No_ was clicked, `None` if _Cancel_ was clicked.
    """
    yes = QtWidgets.QMessageBox.StandardButton.Yes
    no = QtWidgets.QMessageBox.StandardButton.No
    cancel = QtWidgets.QMessageBox.StandardButton.Cancel
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Question)
    mb.setStandardButtons(yes | no | cancel)
    if default is None:
        mb.setDefaultButton(cancel)
    elif default:
        mb.setDefaultButton(yes)
    else:
        mb.setDefaultButton(no)
    response = mb.exec()
    if response == cancel:
        return None
    return response == yes


def _get_app_and_title(title: str | None) -> tuple[QtWidgets.QApplication, str]:
    """Returns a tuple of the QApplication instance and the title bar text of the active window."""
    app = application()
    if title is None:
        w = app.activeWindow()
        title = "MSL-Qt" if w is None else w.windowTitle()
    return app, title


def _input_dialog(
    *, title: str | None, message: str, font: Font | None = None
) -> tuple[QtWidgets.QApplication, QtWidgets.QInputDialog]:
    app, title = _get_app_and_title(title)
    dialog = QtWidgets.QInputDialog(app.activeWindow(), flags=Qt.WindowType.WindowCloseButtonHint)
    dialog.setWindowTitle(title)
    dialog.setLabelText(message)
    if font is not None:
        dialog.setFont(to_qfont(font))
    return app, dialog


def _message_box(
    *, title: str | None, message: str, font: Font | None = None
) -> tuple[QtWidgets.QApplication, QtWidgets.QMessageBox]:
    app, title = _get_app_and_title(title)
    mb = QtWidgets.QMessageBox(app.activeWindow())
    mb.setWindowTitle(title)
    mb.setText(message)
    if font is not None:
        mb.setFont(to_qfont(font))
    return app, mb


def _get_file_filters(filters: Filter | None) -> str:  # noqa: C901
    """Make the `filters` value be in the appropriate syntax."""

    def _check_ext(ex: str) -> str:
        """Check the format of the file extension."""
        if not ex:
            return all_files
        if "*" in ex:
            return ex
        if ex.startswith("."):
            return f"*{ex}"
        return f"*.{ex}"

    all_files = "All Files (*)"

    if not filters:
        return all_files

    if isinstance(filters, dict):
        f: list[str] = []
        for name, ext in filters.items():
            if isinstance(ext, str):
                f.append(f"{name} ({_check_ext(ext)})")
            else:
                e = " ".join(_check_ext(e) for e in ext)
                f.append(f"{name} ({e})")
        return ";;".join(f)

    if isinstance(filters, str):
        if filters.endswith(";;"):
            return filters[:-2]
        return filters

    return ";;".join(f or all_files for f in filters)


def _message_box_icon(mb: QtWidgets.QMessageBox, pixmap: QtWidgets.QStyle.StandardPixmap) -> QtGui.QPixmap:
    """Rescale the `pixmap` based on the font size of the QMessageBox."""
    icon = to_qicon(pixmap)
    point_size = mb.font().pointSizeF() / 9.0  # Default QMessageBox font size is 9 (on Windows)
    icon_width = icon.availableSizes()[-1].width() / 48.0  # Default QMessageBox.Icon size is 48 (on Windows)
    return rescale_icon(icon, point_size / icon_width)


class _Comment(QtWidgets.QDialog):
    def __init__(self, path: Path) -> None:  # noqa: PLR0915
        """A dialog to prompt the user to enter/select a comment."""
        super().__init__(None, Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinMaxButtonsHint)

        self.path: Path = path
        self.comments: list[list[str]] = []

        if self.path.is_file():
            try:
                comments = json.loads(self.path.read_text())
            except Exception as e:  # noqa: BLE001
                warning(f"Error loading JSON file:\n{self.path}\n\n{e}")
            else:
                if comments and isinstance(comments[0], dict):
                    self.comments = [[c["timestamp"], c["comment"]] for c in comments]
                else:
                    self.comments = comments

        self.comment: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit(self)
        height = self.comment.fontMetrics().lineSpacing()
        self.comment.setFixedHeight(5 * height)  # display 5 lines

        self.ok_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self)
        self.ok_button.setText("Ok")
        self.ok_button.setAutoDefault(False)
        _ = self.ok_button.clicked.connect(self.prepend_and_close)

        cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self)
        cancel_button.setText("Cancel")
        cancel_button.setAutoDefault(False)
        _ = cancel_button.clicked.connect(self.cancelled)

        #
        # the filter field
        #
        filter_label = QtWidgets.QLabel("Filter:")
        self.filter_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.filter_edit.setToolTip("Filter comments using a regular-expression pattern")
        _ = self.filter_edit.editingFinished.connect(self.apply_filter)

        self.filter_ignore_case: QtWidgets.QCheckBox = QtWidgets.QCheckBox(self)
        self.filter_ignore_case.setText("Ignore case?")
        self.filter_ignore_case.setChecked(True)
        self.filter_ignore_case.setToolTip("Whether to perform a case-insensitive filter")
        _ = self.filter_ignore_case.checkStateChanged.connect(self.apply_filter)

        #
        # history table
        #
        tip = (
            "Double click a row to select the comment.\n"
            "Delete comments by selecting the row(s) and pressing the Delete key."
        )
        self.table: QtWidgets.QTableWidget = QtWidgets.QTableWidget()
        table_header = ["Timestamp", "Comment"]
        self.table.setColumnCount(len(table_header))
        self.table.setHorizontalHeaderLabels(table_header)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setToolTip(tip)
        h_header = self.table.horizontalHeader()
        if h_header:
            h_header.setStretchLastSection(True)
            _ = h_header.sectionClicked.connect(self.resize_to_contents)
        _ = self.table.cellDoubleClicked.connect(self.table_double_click)
        self.table.keyPressEvent = self.table_key_press  # type: ignore[method-assign]
        for timestamp, comment in self.comments:
            self.append_to_history_table(timestamp, comment)
        self.resize_to_contents()

        #
        # main layout
        #
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding))
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding))

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(self.filter_ignore_case)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Enter a new comment or select one (double click) from the table"))
        layout.addWidget(self.comment)
        layout.addLayout(button_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        geo = screen_geometry(widget=self)
        self.resize(int(geo.width() * 0.4), int(geo.height() * 0.6))

    def append_to_history_table(self, timestamp: str, comment: str) -> None:
        index = self.table.rowCount()
        self.table.insertRow(index)
        self.table.setItem(index, 0, QtWidgets.QTableWidgetItem(timestamp))
        self.table.setItem(index, 1, QtWidgets.QTableWidgetItem(comment))

    @Slot()
    @Slot(int)
    def apply_filter(self, _: object = None) -> None:
        filter_text = self.filter_edit.text()
        if (not filter_text) and (self.table.rowCount() == len(self.comments)):
            # all rows are already visible
            return

        flag = re.IGNORECASE if self.filter_ignore_case.isChecked() else 0
        regex = re.compile(filter_text, flags=flag)
        self.table.setRowCount(0)
        for timestamp, comment in self.comments:
            if (not filter_text) or (regex.search(timestamp) is not None) or (regex.search(comment) is not None):
                self.append_to_history_table(timestamp, comment)
        self.resize_to_contents()

    @Slot()
    def cancelled(self) -> None:
        self.comment.setPlainText("")
        _ = self.close()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        if event.spontaneous():  # then the X in the title bar of the QDialog was clicked
            self.comment.setPlainText("")
        super().closeEvent(event)

    @Slot()
    def prepend_and_close(self) -> None:
        if self.text():
            timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")  # noqa: DTZ005
            self.comments.insert(0, [timestamp, self.text()])
            self.save_json()
        _ = self.close()

    @Slot()
    def resize_to_contents(self) -> None:
        self.table.verticalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def save_json(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as fp:
            json.dump(self.comments, fp, indent=2, ensure_ascii=False)

    @Slot(int, int)
    def table_double_click(self, row: int, _: int) -> None:
        # always use column 1 even if the timestamp column is double clicked
        table_item = self.table.item(row, 1)
        if table_item is not None:
            self.comment.setPlainText(table_item.text())

    def table_key_press(self, event: QtGui.QKeyEvent | None) -> None:
        if event is None:
            return

        # CTRL+A pressed
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self.table.selectAll()
            return

        if event.key() != Qt.Key.Key_Delete:
            return

        # sort the selected rows in reverse order for the self.table.removeRow method below
        model = self.table.selectionModel()
        selected = sorted([s.row() for s in model.selectedRows()], reverse=True)

        msg = "this comment" if len(selected) == 1 else f"these {len(selected)} comments"
        if not yes_no(f"Remove {msg} from the history?", default=False):
            return

        for index in selected:
            self.table.removeRow(index)
            del self.comments[index]

        self.save_json()

    def text(self) -> str:
        """The text in the comment editor."""
        return self.comment.toPlainText().strip()
