"""Example to show the `SpinBox` and `DoubleSpinBox` widgets."""

from __future__ import annotations

from typing import cast

from msl.qt import DEGREE, DoubleSpinBox, QtWidgets, Slot, SpinBox, application


class Window(QtWidgets.QWidget):
    """Main Window."""

    def __init__(self) -> None:
        """Main Window to contain ComboBoxes."""
        super().__init__()

        self.angle: SpinBox = SpinBox(
            value=100,
            suffix=DEGREE,
            minimum=0,
            maximum=360,
            value_changed=self.on_angle_changed,
            editing_finished=self.on_editing_finished,
            tooltip=f"A value between 0{DEGREE} and 360{DEGREE}",
        )

        self.voltage: DoubleSpinBox = DoubleSpinBox(
            value=3.1e-6,
            suffix="V",
            minimum=1e-9,
            maximum=1,
            use_si_prefix=True,
            value_changed=self.on_voltage_changed,
            editing_finished=self.on_editing_finished,
            tooltip="A value between 1 nV and 1 V",
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.angle)
        layout.addWidget(self.voltage)
        self.setLayout(layout)

    @Slot(int)
    def on_angle_changed(self, value: int) -> None:
        """Slot called when the angle changes."""
        print(f"angle changed  : {value}{DEGREE}")

    @Slot(float)
    def on_voltage_changed(self, value: float) -> None:
        """Slot called when the voltage changes."""
        print(f"voltage changed: {value:g} V")

    @Slot()
    def on_editing_finished(self) -> None:
        """Slot called when a spinbox loses focus, when Enter is pressed, or on a stepBy event."""
        sender = cast("SpinBox|DoubleSpinBox", self.sender())
        print(f"edit finished  : {sender.__class__.__name__}, value={sender.value():g}")


def show() -> None:
    """Create the QApplication and show the main window."""
    app = application()
    w = Window()
    w.show()
    hint = w.sizeHint()
    w.resize(hint.width() + 10, hint.height())
    _ = app.exec()


if __name__ == "__main__":
    show()
