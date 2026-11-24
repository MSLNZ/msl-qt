"""A [QWidget][QtWidgets.QWidget] to display [logging][] records.

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('Logger')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8<-- "src/msl/examples/qt/logger.py"
        ```
"""

from __future__ import annotations

import logging
import random
from datetime import datetime
from typing import TYPE_CHECKING

from msl.qt.binding import Qt, QtGui, QtWidgets, application
from msl.qt.prompt import information, save
from msl.qt.utils import to_qcolor, to_qicon

if TYPE_CHECKING:
    from logging import LogRecord
    from pathlib import Path

    from msl.qt.typing import Color, SupportsWrite


class Logger(QtWidgets.QWidget):
    """A [QWidget][QtWidgets.QWidget] to display [logging][] records."""

    def __init__(  # noqa: PLR0915
        self,
        *,
        level: int | str = logging.INFO,
        fmt: str | None = None,
        datefmt: str | None = None,
        logger: logging.Logger | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A [QWidget][QtWidgets.QWidget] to display [logging][] records.

        Args:
            level: The [Logging Level][levels] to use to display the [LogRecord][logging.LogRecord].
            fmt: The [attributes][logrecord-attributes] to use to display the [LogRecord][logging.LogRecord].
                Default is `"%(asctime)s [%(levelname)s] %(message)s"`.
            datefmt: The [strftime format][strftime-strptime-behavior] to use for the time stamp.
                If `None`, the `YYYY-mm-dd HH:MM:SS.sss` format is used.
            logger: The [Logger][logging.Logger] to handle logging records from.
                If `None`, the root [Logger][logging.Logger] is used.
            parent: The parent widget.
        """
        super().__init__(parent=parent)

        self._records: list[logging.LogRecord] = []
        self._num_displayed: int = 0

        scheme = application().styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            self._color_map: dict[int, QtGui.QColor] = {
                logging.CRITICAL: QtGui.QColor(255, 0, 0),
                logging.ERROR: QtGui.QColor(244, 71, 71),
                logging.WARNING: QtGui.QColor(255, 251, 0),
                logging.INFO: QtGui.QColor(103, 150, 230),
                logging.DEBUG: QtGui.QColor(178, 103, 230),
                logging.NOTSET: QtGui.QColor(40, 110, 95),
            }
        else:
            self._color_map = {
                logging.CRITICAL: QtGui.QColor(255, 0, 0),
                logging.ERROR: QtGui.QColor(175, 25, 25),
                logging.WARNING: QtGui.QColor(180, 100, 127),
                logging.INFO: QtGui.QColor(0, 0, 255),
                logging.DEBUG: QtGui.QColor(127, 127, 127),
                logging.NOTSET: QtGui.QColor(40, 110, 95),
            }

        self._level_names: dict[str, int] = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if logger is None:
            logger = logging.getLogger()

        if logger.level == logging.NOTSET:
            logger.setLevel(logging.DEBUG)

        if isinstance(level, str):
            level = self._level_names[level.upper()]

        if not fmt:
            fmt = "%(asctime)s [%(levelname)s] %(message)s"

        self._current_level: int = level
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        formatter.default_msec_format = "%s.%03d"

        self._handler: logging.Handler = logging.Handler()
        self._handler.setFormatter(formatter)
        self._handler.emit = self._emit  # type: ignore[method-assign]
        logger.addHandler(self._handler)

        self._level_combobox: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        for name, data in self._level_names.items():
            self._level_combobox.addItem(name, userData=data)
            if data == self._current_level:
                self._level_combobox.setCurrentText(name)

        _ = self._level_combobox.currentTextChanged.connect(self._update_records)
        self._level_combobox.setToolTip("Select the logging level")

        self._level_checkbox: QtWidgets.QCheckBox = QtWidgets.QCheckBox()
        self._level_checkbox.setChecked(False)
        _ = self._level_checkbox.stateChanged.connect(self._level_checkbox_changed)
        self._update_level_checkbox_tooltip()

        self._label: QtWidgets.QLabel = QtWidgets.QLabel()
        self._update_label()

        self._save_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        self._save_button.setIcon(to_qicon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))
        _ = self._save_button.clicked.connect(self._save_records)
        self._save_button.setToolTip("Save the log records")

        self._text_browser: QtWidgets.QTextBrowser = QtWidgets.QTextBrowser(self)
        self._text_browser.setLineWrapMode(QtWidgets.QTextBrowser.LineWrapMode.NoWrap)
        self._vsb: QtWidgets.QScrollBar = self._text_browser.verticalScrollBar()

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self._level_combobox)
        top.addWidget(self._level_checkbox)
        top.addStretch()
        top.addWidget(self._label)
        top.addStretch()
        top.addWidget(self._save_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self._text_browser)
        self.setLayout(layout)

    @property
    def records(self) -> list[LogRecord]:
        """[list][][[LogRecord][logging.LogRecord]] &mdash; Returns the logging records."""
        return self._records

    def save(self, path: str | Path, *, level: int = logging.INFO) -> None:
        """Save the logging records to a file.

        Args:
            path: The path to save the logging records to. Appends the records to the
                file if the file already exists, otherwise creates a new file.
            level: All [LogRecord][logging.LogRecord]s with a [Logging Level][levels]
                &ge; `level` will be saved.
        """
        with open(path, mode="a") as fp:  # noqa: PTH123
            self._write_header(fp)
            for record in self._records:
                if record.levelno >= level:
                    _ = fp.write(self._handler.format(record) + "\n")
            _ = fp.write("\n")

    def set_level_color(self, level: int | str, color: Color) -> None:
        """Set the font color to use for a logging level.

        Args:
            level: The logging [level][levels] to change the color of.
                Can be the name or value of a logging [level][levels], e.g., `"INFO"`, `20` or [logging.INFO][].
            color: The color to use. The value is passed to [to_qcolor][msl.qt.utils.to_qcolor].
        """
        if isinstance(level, str):
            level = self._level_names[level.upper()]
        self._color_map[level] = to_qcolor(color)

    def _add_new_level(self, record: LogRecord) -> None:
        color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self._color_map[record.levelno] = color
        self._level_names[record.levelname] = record.levelno
        for i in range(self._level_combobox.count()):
            if record.levelno < self._level_combobox.itemData(i):
                self._level_combobox.insertItem(i, record.levelname, userData=record.levelno)
                return
        self._level_combobox.addItem(record.levelname, userData=record.levelno)

    def _append_record(self, record: LogRecord) -> None:
        """Append a LogRecord to the QTextBrowser."""
        if self._level_checkbox.isChecked() and record.levelno != self._level_combobox.currentData():
            return
        msg = self._handler.format(record)
        try:
            self._text_browser.setTextColor(self._color_map[record.levelno])
        except KeyError:
            self._add_new_level(record)
            self._text_browser.setTextColor(self._color_map[record.levelno])
        self._text_browser.append(msg)
        self._num_displayed += 1
        if self._vsb.maximum() - self._vsb.value() <= self._vsb.singleStep():
            self._text_browser.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            self._text_browser.moveCursor(QtGui.QTextCursor.MoveOperation.StartOfLine)

    def _emit(self, record: LogRecord) -> None:
        self._records.append(record)
        try:
            data = self._level_combobox.currentData()
        except RuntimeError:
            #   RuntimeError: wrapped C/C++ object of type QComboBox has been deleted
            logging.getLogger().removeHandler(self._handler)
            return

        if record.levelno >= data:
            self._append_record(record)
        self._update_label()

    def _level_checkbox_changed(self, _: int) -> None:
        self._update_records(self._level_combobox.currentText())

    def _save_records(self, _: bool) -> None:  # noqa: FBT001
        """Save the LogRecords that are currently displayed in the QTextBrowser to a file."""
        if len(self._records) == 0:
            information("There are no log records to save.")
            return
        option = QtWidgets.QFileDialog.Option.DontConfirmOverwrite
        title = "Save the Log Records (appends to an existing file)"
        path = save(filters={"Log Files": "*.log"}, title=title, options=option)
        if not path:
            return
        if not path.endswith(".log"):
            path += ".log"
        with open(path, mode="a") as fp:  # noqa: PTH123
            self._write_header(fp)
            fp.writelines(self._text_browser.toPlainText())
            __ = fp.write("\n\n")

    def _update_label(self) -> None:
        """Update the label that shows the number of LogRecords that are visible."""
        if not self._records:
            self._label.setText("There are no log records")
        elif self._num_displayed == len(self._records):
            self._label.setText("Displaying all log records")
        else:
            self._label.setText(f"Displaying {self._num_displayed} of {len(self._records)} log records")

    def _update_level_checkbox_tooltip(self) -> None:
        """Update the ToolTip for self._level_checkbox."""
        self._level_checkbox.setToolTip(f"Show {self._level_combobox.currentText()} level only")

    def _update_records(self, name: str) -> None:
        """Update the displayed LogRecords.

        Clears the QTextBrowser and adds all the LogRecords that have a
        levelno >= the currently-selected logging level.
        """
        self._num_displayed = 0
        self._text_browser.clear()
        self._update_level_checkbox_tooltip()
        levelno = self._level_names[name]
        for record in self._records:
            if record.levelno >= levelno:
                self._append_record(record)
        self._update_label()

    @staticmethod
    def _write_header(fp: SupportsWrite[str]) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ005
        _ = fp.write(f"# Saved {now}\n")
