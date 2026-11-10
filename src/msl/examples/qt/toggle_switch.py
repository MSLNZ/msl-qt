"""Example showing the [ToggleSwitch][msl.qt.widgets.toggle_switch.ToggleSwitch] widget."""

from __future__ import annotations

from msl.qt import QtWidgets, Slot, ToggleSwitch, application


@Slot(bool)
def print_state(checked: bool) -> None:
    """Slot to handle when the toggle switch is clicked."""
    print(checked)
    state = "on" if checked else "off"
    print(f"The switch is {state}")


def show() -> None:
    """Create the QApplication and show the ToggleSwitch."""
    app = application()
    window = QtWidgets.QWidget()
    window.setWindowTitle("Toggle Switch Example")
    layout = QtWidgets.QVBoxLayout()
    ts1 = ToggleSwitch(toggled=print_state)
    ts2 = ToggleSwitch(initial=True, on_color="red", tooltip="Not connected")
    layout.addWidget(ts1)
    layout.addWidget(ts2)
    window.setLayout(layout)
    window.show()
    _ = app.exec()


if __name__ == "__main__":
    show()
