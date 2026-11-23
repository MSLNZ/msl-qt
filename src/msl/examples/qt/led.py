"""Example to show the `LED` widget."""

from __future__ import annotations

import random
from typing import Any, cast

from msl.qt import LED, Qt, QtCore, QtWidgets, Slot, application


class BlinkingLEDs(QtWidgets.QWidget):
    """Main window to contain the LEDs."""

    def __init__(self) -> None:
        """Main window to contain the LEDs."""
        super().__init__()

        # The shape can be an enum value or member name (case in-sensitive)
        # The color can be anything that msl.qt.utils.to_qcolor() accepts
        params: list[dict[str, Any]] = [
            {"shape": LED.Circle, "on_color": Qt.GlobalColor.green, "clickable": True},
            {"shape": "Rounded", "on_color": (255, 0, 0)},
            {"shape": LED.Square, "on_color": "yellow", "clickable": True},
            {"shape": "Triangle", "on_color": "#0000FF"},
        ]

        self.leds: list[LED] = []
        layout = QtWidgets.QHBoxLayout()
        for kwargs in params:
            led = LED(**kwargs)
            _ = led.toggled.connect(self.on_led_toggled)
            _ = led.clicked.connect(self.on_led_clicked)
            layout.addWidget(led)
            self.leds.append(led)
        self.setLayout(layout)

        self._timer: QtCore.QTimer = QtCore.QTimer()
        _ = self._timer.timeout.connect(self.on_toggle_random_led)
        self._timer.start(2000)

    @Slot()
    def on_toggle_random_led(self) -> None:
        """Slot for the `QTimer.timeout`.

        Toggle the on/off state of a random LED.
        """
        random.choice(self.leds).toggle()

    @Slot(bool)
    def on_led_toggled(self, is_on: bool) -> None:
        """Print which LED had a state change."""
        sender = cast("LED", self.sender())
        state = "is on" if is_on else "is off"
        print(sender.shape().name, state)

    @Slot()
    def on_led_clicked(self, is_on: bool) -> None:
        """Print which LED was clicked."""
        sender = cast("LED", self.sender())
        shape = sender.shape().name
        if sender.is_clickable:
            state = "on" if is_on else "off"
            print(f"{shape} clicked {state}")
        else:
            print(f"{shape} clicked (ignored)")


def show() -> None:
    """Create the QApplication and show the LEDs."""
    app = application()
    b = BlinkingLEDs()
    b.setWindowTitle("Blinking LEDs")
    b.show()
    b.resize(400, 200)
    _ = app.exec()


if __name__ == "__main__":
    show()
