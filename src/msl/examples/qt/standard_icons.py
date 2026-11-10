"""Display all icons in `QtWidgets.QStyle.StandardPixmap` and in the *standard* Windows DLL/EXE files."""

# pyright: reportImplicitOverride=false
from __future__ import annotations

import sys
from functools import partial
from typing import TYPE_CHECKING

from msl.qt import Qt, QtCore, QtWidgets, application, convert, excepthook

if TYPE_CHECKING:
    from msl.qt import QtGui


class ShowStandardIcons(QtWidgets.QMainWindow):
    """Main window to show the icons."""

    def __init__(self) -> None:
        """Main window to show the icons."""
        super().__init__()

        self.tab_widget: QtWidgets.QTabWidget = QtWidgets.QTabWidget()

        self.setWindowTitle("Standard Icons")
        self.setCentralWidget(self.tab_widget)

        # add a progress bar to the status bar
        self.progress_bar: QtWidgets.QProgressBar = QtWidgets.QProgressBar(self.statusBar())
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.num_icons: int = 0
        self.file_index: int = 0
        self.zoom_widget: QtWidgets.QDialog = QtWidgets.QDialog()
        self.zoom_widget.setSizeGripEnabled(True)
        self.zoom_widget.resize(QtCore.QSize(256, 256))
        self.zoom_widget.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        vbox = QtWidgets.QVBoxLayout()
        self.zoom_label: QtWidgets.QLabel = QtWidgets.QLabel()
        self.zoom_label.setScaledContents(True)
        vbox.addWidget(self.zoom_label)
        self.zoom_widget.setLayout(vbox)

        qt_icons = [sp for sp in dir(QtWidgets.QStyle.StandardPixmap) if sp.startswith("SP_")]

        self.windows_files: list[str] = [
            "accessibilitycpl",
            "compstui",
            "ddores",
            "dmdskres",
            "explorer",
            "gameux",
            "ieframe",
            "imageres",
            "mmcndmgr",
            "mmres",
            "moricons",
            "netcenter",
            "netshell",
            "networkexplorer",
            "pifmgr",
            "pnidui",
            "sensorscpl",
            "setupapi",
            "shell32",
            "wmploc",
            "wpdshext",
        ]

        self.add_qt_tab("Qt Icons", qt_icons)

        if sys.platform == "win32":
            num_files = 1 + len(self.windows_files)
            self.progress_bar.setRange(0, num_files)

            self.windows_index: int = 0
            self.timer: QtCore.QTimer = QtCore.QTimer()
            _ = self.timer.timeout.connect(self.add_windows_tab)
            self.timer.start(0)
        else:
            self.update_message(f"Loaded {self.num_icons} icons.")
            self.progress_bar.hide()

    def add_qt_tab(self, label: str, icons: list[str]) -> None:
        """Add the Qt icons."""
        tab = QtWidgets.QWidget()
        _ = self.tab_widget.addTab(tab, label)

        layout = QtWidgets.QGridLayout()

        self.update_message("Loading Qt icons...")

        num_cols = 4
        for i, name in enumerate(icons):
            button = QtWidgets.QPushButton(name)
            icon = convert.to_qicon(getattr(QtWidgets.QStyle, name))
            button.setIcon(icon)
            _ = button.clicked.connect(partial(self.zoom, icon, name))
            layout.addWidget(button, i // num_cols, i % num_cols)
            self.num_icons += 1

        tab.setLayout(layout)

        self.file_index += 1
        self.progress_bar.setValue(self.file_index)

    def add_windows_tab(self) -> None:
        """Add the icons from the Windows DLL and EXE files."""
        num_cols = 16
        filename = self.windows_files[self.windows_index]
        self.update_message(f"Loading icons from {filename}...")

        tab = QtWidgets.QWidget()
        _ = self.tab_widget.addTab(tab, filename)

        layout = QtWidgets.QGridLayout()

        index = 0
        while True:
            button = QtWidgets.QPushButton(str(index))
            name = f"{filename}|{index}"
            try:
                icon = convert.to_qicon(name)
            except OSError:
                break

            button.setIcon(icon)
            _ = button.clicked.connect(partial(self.zoom, icon, name))
            layout.addWidget(button, index // num_cols, index % num_cols)
            index += 1
            self.num_icons += 1

        self.file_index += 1
        self.progress_bar.setValue(self.file_index)

        tab.setLayout(layout)

        self.windows_index += 1
        if self.windows_index == len(self.windows_files):
            self.timer.stop()
            self.update_message(f"Loaded {self.num_icons} icons.")
            self.progress_bar.hide()

    def update_message(self, text: str) -> None:
        """Update the status bar with a message."""
        self.statusBar().showMessage(text)

    def zoom(self, icon: QtGui.QIcon, name: str) -> None:
        """Slot to handle when an icon is clicked.

        Displays the icon in a larger widget.
        """
        self.zoom_widget.setWindowTitle(name)
        self.zoom_label.setPixmap(icon.pixmap(self.zoom_widget.size()))
        self.zoom_widget.setWindowState(Qt.WindowState.WindowActive)
        self.zoom_widget.activateWindow()
        self.zoom_widget.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Overrides `QtWidgets.QMainWindow.closeEvent`."""
        _ = self.zoom_widget.close()
        super().closeEvent(event)


def show() -> None:
    """Create the QApplication and show the main window."""
    sys.excepthook = excepthook
    app = application()
    main = ShowStandardIcons()
    main.showMaximized()
    _ = app.exec()


if __name__ == "__main__":
    show()
