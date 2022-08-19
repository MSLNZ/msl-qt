"""
Example showing the :class:`~msl.qt.widgets.toggle_switch.ToggleSwitch`.
"""
from msl.qt import (
    QtWidgets,
    application,
    ToggleSwitch
)


def print_state(checked):
    state = 'on' if checked else 'off'
    print(f'The switch is {state}')


def show():
    app = application()
    window = QtWidgets.QWidget()
    window.setWindowTitle('Toggle Switch Example')
    hbox = QtWidgets.QHBoxLayout()
    ts = ToggleSwitch(parent=window)
    ts.toggled.connect(print_state)
    hbox.addWidget(ts)
    window.setLayout(hbox)
    window.show()
    app.exec()


if __name__ == '__main__':
    show()
