"""Exception handling."""

from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from ._qt import Qt, QtWidgets, application
from .prompt import save
from .utils import logger, save_image

if TYPE_CHECKING:
    from types import TracebackType


def excepthook(typ: type[BaseException], value: BaseException, tb: TracebackType | None) -> None:
    """Displays unhandled exceptions in a [QMessageBox][QtWidgets.QMessageBox].

    See [sys.excepthook][] for more details.

    Include the following to implement `excepthook` in your own application.

    ```python
    import sys
    from msl import qt

    sys.excepthook = qt.excepthook
    ```
    """

    class ErrorDialog(QtWidgets.QDialog):
        def __init__(self) -> None:
            super().__init__(None, Qt.WindowType.WindowCloseButtonHint)

            w = app.activeWindow()
            prefix = "MSL" if (w is None or not w.windowTitle()) else w.windowTitle()
            self.setWindowTitle(f"{prefix} || Unhandled Exception")

            self.setSizeGripEnabled(True)

            self.icon_label: QtWidgets.QLabel = QtWidgets.QLabel()
            critical_icon = app.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
            largest_size = critical_icon.availableSizes()[-1]
            self.icon_label.setPixmap(critical_icon.pixmap(largest_size))

            self.error_label: QtWidgets.QLabel = QtWidgets.QLabel(f"{value.__class__.__name__}:\n\n{value}")
            self.error_label.setWordWrap(True)

            self.ok_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Close")
            _ = self.ok_button.clicked.connect(self.close)
            self.ok_button.setToolTip("Close")

            self.screenshot_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Screenshot")
            _ = self.screenshot_button.clicked.connect(self.save_screenshot)
            self.screenshot_button.setToolTip("Save a screenshot of this window")

            self.copy_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Copy")
            _ = self.copy_button.clicked.connect(self.copy_to_clipboard)
            self.copy_button.setToolTip("Copy the error message to the system clipboard")

            self.show_details_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Hide details...")
            _ = self.show_details_button.clicked.connect(self.show_hide_details)
            self.show_details_button.setToolTip("Show less information")

            self.detailed_text_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
            self.detailed_text_edit.setText(details)
            self.detailed_text_edit.setReadOnly(True)

            expanding = QtWidgets.QSizePolicy.Policy.Expanding

            label_layout = QtWidgets.QHBoxLayout()
            label_layout.addWidget(self.icon_label)
            label_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignLeft)
            label_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, expanding, expanding))

            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.screenshot_button)
            button_layout.addWidget(self.copy_button)
            button_layout.addWidget(self.show_details_button)
            button_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, expanding, expanding))

            layout = QtWidgets.QVBoxLayout()
            layout.addLayout(label_layout)
            layout.addLayout(button_layout)
            layout.addWidget(self.detailed_text_edit, stretch=1)
            self.setLayout(layout)

        def save_screenshot(self) -> None:
            filename = save(filters="Images (*.png *.jpg *.jpeg *.bmp)")
            if filename:
                _ = save_image(self, filename)

        def show_hide_details(self) -> None:
            if self.detailed_text_edit.isVisible():
                self.detailed_text_edit.hide()
                self.show_details_button.setText("Show details...")
                self.show_details_button.setToolTip("Show more information")
                self.adjustSize()
            else:
                self.detailed_text_edit.show()
                self.show_details_button.setText("Hide details...")
                self.show_details_button.setToolTip("Show less information")

        def copy_to_clipboard(self) -> None:
            app.clipboard().setText(self.detailed_text_edit.toPlainText())

    details = "".join(traceback.format_exception(typ, value, tb))
    logger.error(details)

    # ensure that a QApplication exists
    app = application()

    dialog = ErrorDialog()
    dialog.raise_()
    _ = dialog.exec()
