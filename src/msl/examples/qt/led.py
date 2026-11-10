"""Example to show the [LED][msl.qt.widgets.led.LED] widget."""

from __future__ import annotations

import random
from typing import Any, cast

from msl.qt import LED, Qt, QtCore, QtWidgets, Slot, application


class BlinkingLEDs(QtWidgets.QWidget):
    """Main window to contain the LEDs."""

    def __init__(self) -> None:
        """Main window to contain the LEDs."""
        super().__init__()

        self.setWindowTitle("Blinking LEDs")

        # The shape can be an enum value or member name (case in-sensitive)
        # The color can be anything that msl.qt.utils.to_qcolor() accepts
        params: list[dict[str, Any]] = [
            {"shape": LED.Circle, "on_color": Qt.GlobalColor.darkGreen, "clickable": True},
            {"shape": "Rounded", "on_color": (78, 82, 107)},
            {"shape": LED.Square, "on_color": "cyan", "clickable": True},
            {"shape": "Triangle", "on_color": "#6b3064"},
        ]

        self.leds: list[LED] = []
        layout = QtWidgets.QHBoxLayout()
        for kwargs in params:
            led = LED(**kwargs)
            _ = led.toggled.connect(self.led_state_changed)
            _ = led.clicked.connect(self.led_was_clicked)
            layout.addWidget(led)
            self.leds.append(led)
        self.setLayout(layout)

        self._timer: QtCore.QTimer = QtCore.QTimer()
        _ = self._timer.timeout.connect(self.toggle_random_led)
        self._timer.start(1000)

    @Slot()
    def toggle_random_led(self) -> None:
        """Slot for the `QTimer.timeout`.

        Toggle the on/off state of a random LED.
        """
        random.choice(self.leds).toggle()

    @Slot(bool)
    def led_state_changed(self, is_on: bool) -> None:
        """Print which LED had a state change."""
        sender = cast("LED", self.sender())
        print(sender.shape().name, "is on" if is_on else "is off")

    @Slot()
    def led_was_clicked(self) -> None:
        """Print which LED was clicked."""
        sender = cast("LED", self.sender())
        print(sender.shape().name, "was clicked")


def show() -> None:
    """Create the QApplication and show the LEDs."""
    app = application()
    b = BlinkingLEDs()
    b.show()
    b.resize(400, 200)
    _ = app.exec()


if __name__ == "__main__":
    show()
