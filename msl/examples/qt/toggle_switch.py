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
    layout = QtWidgets.QVBoxLayout()
    ts1 = ToggleSwitch(toggled=print_state)
    ts2 = ToggleSwitch(initial=True, on_color='red', tooltip='Not connected')
    layout.addWidget(ts1)
    layout.addWidget(ts2)
    window.setLayout(layout)
    window.show()
    app.exec()


if __name__ == '__main__':
    show()
