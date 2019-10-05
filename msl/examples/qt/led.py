"""
An :class:`~msl.qt.widget.led.LED` example.
"""
import random

from msl.qt import (
    application,
    Qt,
    QtWidgets,
    QtCore,
    LED,
)


class BlinkingLEDs(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(BlinkingLEDs, self).__init__(parent)

        self.setWindowTitle('Blinking LEDs')

        # The shape can be an enum value or member name (case in-sensitive)
        # The color can be anything that msl.qt.utils.to_qcolor() accepts
        params = [
            {'shape': LED.Circle, 'on_color': Qt.darkGreen, 'clickable': True},
            {'shape': 'rouNDed', 'on_color': (78, 82, 107)},
            {'shape': 2, 'on_color': 'cyan', 'clickable': True},
            {'shape': 'Triangle', 'on_color': '#6b3064'},
        ]

        self.leds = []
        layout = QtWidgets.QHBoxLayout()
        for kwargs in params:
            led = LED(**kwargs)
            led.toggled.connect(self.led_state_changed)
            led.clicked.connect(self.led_was_clicked)
            layout.addWidget(led)
            self.leds.append(led)
        self.setLayout(layout)

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.toggle_random_led)
        self._timer.start(200)

    def toggle_random_led(self):
        random.choice(self.leds).toggle()

    def led_state_changed(self, is_on):
        print(self.sender().shape().name, 'is on' if is_on else 'is off')

    def led_was_clicked(self):
        print(self.sender().shape().name, 'was clicked')


def show():
    app = application()
    b = BlinkingLEDs()
    b.show()
    app.exec_()


if __name__ == "__main__":
    show()
