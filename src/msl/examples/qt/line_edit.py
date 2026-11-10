"""Example to show the [LineEdit][msl.qt.widgets.line_edit.LineEdit] widget."""

from __future__ import annotations

from random import randint

from msl.qt import LineEdit, QtCore, QtWidgets, Slot, application


class Window(QtWidgets.QWidget):
    """Main window to contain the `LineEdit`."""

    def __init__(self) -> None:
        """Main window to contain the `LineEdit`."""
        super().__init__()

        self.timer: QtCore.QTimer = QtCore.QTimer()
        _ = self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.e1: LineEdit = LineEdit(text="fixed", read_only=True)
        self.e2: LineEdit = LineEdit(text="enter text", rescale=True, text_changed=self.on_text_changed)
        self.e3: LineEdit = LineEdit(rescale=True, tooltip="Connected to QTimer")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.e1)
        layout.addWidget(self.e2)
        layout.addWidget(self.e3)
        self.setLayout(layout)

    @Slot()
    def on_timeout(self) -> None:
        """Slot for the `QTimer.timeout` signal."""
        self.e3.setText("x" * randint(10, 25))

    @Slot(str)
    def on_text_changed(self, text: str) -> None:
        """Slot for the `LineEdit.textChanged` signal."""
        print(f"The text is now {text!r}")


def show() -> None:
    """Create the QApplication and show the main window."""
    app = application()
    w = Window()
    w.show()
    _ = app.exec()


if __name__ == "__main__":
    show()
