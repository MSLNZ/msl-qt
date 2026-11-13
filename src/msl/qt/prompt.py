"""Convenience functions to prompt the user.

The following functions create a dialog window to either notify the user of an
event that happened or to request information from the user.
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ._qt import Qt, QtGui, QtWidgets, application
from .constants import HOME_DIR
from .convert import to_qcolor, to_qfont
from .utils import screen_geometry

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from .typing import Color, Filter, Font


def critical(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using a *critical* alert icon.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py '<html>A <p style="color:red"><i>critical</i></p> error occurred!</html>'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    _ = mb.exec()


def double(
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
    """Prompt for a double-precision value (a Python [float][] data type).

    Args:
        message: The message that is shown to the user to describe what the value represents.
            The message can use HTML/CSS markup, e.g., `#!py "<html>Enter a mass, in &mu;g</html>"`.
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
    title: str = "Select File",
    directory: str | Path | None = None,
    filters: Filter | None = None,
) -> str:
    """Select a file.

    Args:
        title: The text to display in the title bar of the dialog window.
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
    title: str = "Select Files",
    directory: str | Path | None = None,
    filters: Filter | None = None,
) -> list[str]:
    """Select multiple files.

    Args:
        title: The text to display in the title bar of the dialog window.
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


def folder(*, title: str = "Select Folder", directory: str | Path | None = None) -> str:
    """Select a folder.

    Args:
        title: The text to display in the title bar of the dialog window.
        directory: The initial directory to start in.

    Returns:
        The path of the selected folder. Returns an empty string if the dialog was cancelled.
    """
    d = "" if directory is None else str(directory)
    app, title = _get_app_and_title(title)
    return QtWidgets.QFileDialog.getExistingDirectory(app.activeWindow(), title, d)


def information(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using an *information* alert icon.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py "<html>Laser at 26.3 &deg;C</html>"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Information)
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

    Args:
        message: The message that is shown to the user to describe what the value represents.
            The message can use HTML/CSS markup, e.g., `#!py "<html>Enter a mass, in &mu;g</html>"`.
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
    mn = -sys.maxsize if minimum is None else minimum
    mx = sys.maxsize if maximum is None else maximum
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
            `#!py "<html>Choose a <i>temperature</i> in &deg;C</html>"`
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


def comment(
    *,
    path: str | Path | None = None,
    title: str | None = None,
    even_row_color: Color | None = None,
    odd_row_color: Color | None = None,
    text_color: Color | None = None,
) -> str:
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

    Args:
        path: The path to a [JSON](https://www.json.org/) file that contains the history
            of the comments that have been entered. If `None`, the default path is used.
            The file is created if it does not exist.
        title: The text to display in the title bar of the dialog window.
        even_row_color: The background color of the even-numbered rows in the history table.
            The default color is chosen based on the color scheme of the operating system.
        odd_row_color: The background color of the odd-numbered rows in the history table.
            The default color is chosen based on the color scheme of the operating system.
        text_color: The text color of a comment in the history table.
            The default color is chosen based on the color scheme of the operating system.

    Returns:
        The comment.
    """
    app, title = _get_app_and_title(title)

    if text_color is None:
        text_color = app.palette().color(QtGui.QPalette.ColorRole.Text)

    if even_row_color is None:
        even_row_color = app.palette().color(QtGui.QPalette.ColorRole.Window)

    if odd_row_color is None:
        scheme = app.styleHints().colorScheme()
        even_row_color = to_qcolor(even_row_color)
        odd_row_color = even_row_color.lighter(150) if scheme == Qt.ColorScheme.Dark else even_row_color.darker(110)

    p = Path(path) if path else (HOME_DIR / "msl-qt-comments.json")
    c = _Comment(p, even_row_color, odd_row_color, text_color)
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

    Args:
        message: The message that is shown to the user. The message can use HTML/CSS markup, e.g.,
            `#!py "<html>Enter a <i>hostname</i> or <i>IP address</i></html>"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        value: The initial value.
        multi_line: Whether the entered text can span multiple lines.
        echo: The *echo* mode to use for the entered value (see also, [password][..password]).

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

    Args:
        message: The message that is shown to the user. The message can use HTML/CSS markup, e.g.,
            `#!py "<html>Enter a <i>secure password</i></html>"`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.

    Returns:
        The password.
    """
    return text(message, title=title, font=font, echo=QtWidgets.QLineEdit.EchoMode.Password)


def warning(message: str | Exception, *, title: str | None = None, font: Font | None = None) -> None:
    """Display a message in a dialog window using a *warning* alert icon.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py '<html>A <p style="color:yellow">warning</p> message</html>'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    _ = mb.exec()


def ok_cancel(message: str, *, title: str | None = None, font: Font | None = None, default: bool = True) -> bool:
    """Prompt for a response to a message where the logical options are `Ok` or `Cancel`.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py '<html>Change the laser diode current to <p style="color:green">60 mA</p>?</html>'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then `Ok` is selected,
            otherwise `Cancel` is selected.

    Returns:
        `True` if `Ok` was clicked, otherwise `False` if `Cancel` was clicked.
    """
    ok = QtWidgets.QMessageBox.StandardButton.Ok
    cancel = QtWidgets.QMessageBox.StandardButton.Cancel
    _, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Icon.Question)
    mb.setStandardButtons(ok | cancel)
    mb.setDefaultButton(ok if default else cancel)
    return mb.exec() == ok


def yes_no(message: str, *, title: str | None = None, font: Font | None = None, default: bool = True) -> bool:
    """Prompt for a response to a message where the logical options are `Yes` or `No`.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py '<html>Change the laser diode current to <p style="color:green">60 mA</p>?</html>'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then `Yes` is selected,
            otherwise `No` is selected.

    Returns:
        `True` if `Yes` was clicked, otherwise `False` if `No` was clicked.
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
    """Prompt for a response to a message where the logical options are `Yes`, `No` or `Cancel`.

    Args:
        message: The message to display. The message can use HTML/CSS markup, e.g.,
            `#!py '<html>Change the laser diode current to <p style="color:green">60 mA</p>?</html>'`.
        title: The text to display in the title bar of the dialog window.
            If `None`, the text in the title bar of the active window is used.
        font: The font to use.
        default: The button to initially select. If `True` then `Yes` is selected,
            if `False` then `No` is selected, if `None` then `Cancel` is selected.

    Returns:
        `True` if `Yes` was clicked, `False` if `No` was clicked, `None` if `Cancel` was clicked.
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
        title = "MSL" if w is None else w.windowTitle()
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


class _Comment(QtWidgets.QDialog):
    def __init__(self, path: Path, even_row_color: Color, odd_row_color: Color, text_color: Color) -> None:  # noqa: PLR0915
        """A dialog to prompt the user to enter/select a comment."""
        super().__init__(None, Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinMaxButtonsHint)

        self.path: Path = path
        self.comments: list[dict[str, str]] = []
        self.even_row_color: QtGui.QColor = to_qcolor(even_row_color)
        self.odd_row_color: QtGui.QColor = to_qcolor(odd_row_color)
        self.text_color: QtGui.QColor = to_qcolor(text_color)

        if self.path.is_file():
            try:
                self.comments = json.loads(self.path.read_text())
            except Exception as e:  # noqa: BLE001
                warning(f"Error loading JSON file:\n{self.path}\n\n{e}")

        self.comment: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit(self)
        height = self.comment.fontMetrics().lineSpacing()
        self.comment.setFixedHeight(5 * height)  # display 5 lines

        from .widgets.button import Button  # noqa: PLC0415

        self.ok_button: Button = Button(
            text="OK",
            left_click=self.prepend_and_close,
            tooltip="Select the comment and exit",
            parent=self,
        )
        self.ok_button.add_menu_item(
            text="Clear history",
            icon=QtWidgets.QStyle.StandardPixmap.SP_DialogResetButton,
            triggered=self.clear_history,
            tooltip="Delete all comments that are in the history",
        )

        #
        # the filter field
        #
        self.filter_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.filter_edit.setToolTip("Search filter for the history")
        _ = self.filter_edit.returnPressed.connect(self.apply_filter)

        filter_button: Button = Button(
            icon=QtWidgets.QStyle.StandardPixmap.SP_FileDialogContentsView,
            tooltip="Apply filter",
            left_click=self.apply_filter,
        )
        clear_button: Button = Button(
            icon=QtWidgets.QStyle.StandardPixmap.SP_LineEditClearButton,
            tooltip="Clear filter",
            left_click=self.clear_filter,
        )

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(filter_button)
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(clear_button)
        filter_layout.setSpacing(1)

        #
        # history table
        #
        self.table: QtWidgets.QTableWidget = QtWidgets.QTableWidget()
        table_header = ["Timestamp", "Comment"]
        self.table.setColumnCount(len(table_header))
        self.table.setHorizontalHeaderLabels(table_header)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        h_header = self.table.horizontalHeader()
        if h_header:
            h_header.setStretchLastSection(True)
            _ = h_header.sectionClicked.connect(self.update_table_row_colors_and_resize)
        _ = self.table.cellDoubleClicked.connect(self.table_double_click)
        self.table.keyPressEvent = self.table_key_press  # type: ignore[method-assign]
        for item in self.comments:
            self.append_to_history_table(item["timestamp"], item["comment"])
        self.update_table_row_colors_and_resize()

        #
        # main layout
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Enter a new comment or select one from the history below"))
        layout.addWidget(self.comment)
        layout.addWidget(self.ok_button)
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

    def apply_filter(self) -> None:
        filter_text = self.filter_edit.text().lower()
        if not filter_text and self.table.rowCount() == len(self.comments):
            # all rows are already visible
            return

        self.table.setRowCount(0)
        for item in self.comments:
            if not filter_text or filter_text in item["timestamp"] or filter_text in item["comment"].lower():
                self.append_to_history_table(item["timestamp"], item["comment"])
        self.update_table_row_colors_and_resize()

    def clear_filter(self) -> None:
        # clear the filter text, only if there is text written in the filter
        if self.filter_edit.text():
            self.filter_edit.setText("")
            self.apply_filter()

    def clear_history(self) -> None:
        if not self.comments or not yes_no("Clear the entire history?", default=False):
            return
        self.table.setRowCount(0)
        self.comments = []
        self.save_json()

    def prepend_and_close(self) -> None:
        _ = self.close()

        if not self.text():
            # no new comments were entered so there is nothing to save to the history file
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ005
        self.comments.insert(0, {"timestamp": timestamp, "comment": self.text()})
        self.save_json()

    def save_json(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as fp:
            json.dump(self.comments, fp, indent=2, ensure_ascii=False)

    def table_double_click(self, row: int, _: int) -> None:
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

        if len(selected) == self.table.rowCount():
            self.clear_history()
            return

        msg = "this item" if len(selected) == 1 else f"these {len(selected)} items"
        if not yes_no(f"Remove {msg} from the history?", default=False):
            return

        for index in selected:
            self.table.removeRow(index)
            del self.comments[index]

        self.save_json()

    def text(self) -> str:
        """The text in the comment editor."""
        return self.comment.toPlainText().strip()

    def update_table_row_colors_and_resize(self) -> None:
        for row in range(self.table.rowCount()):
            color = self.even_row_color if row % 2 else self.odd_row_color
            table_item = self.table.item(row, 0)
            if table_item is not None:
                table_item.setBackground(color)
                table_item.setForeground(self.text_color)
            table_item = self.table.item(row, 1)
            if table_item is not None:
                table_item.setBackground(color)
                table_item.setForeground(self.text_color)
        self.table.verticalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
