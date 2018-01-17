"""
Example showing the :obj:`ToggleSwitch <msl.qt.toggle_switch.ToggleSwitch>`.
"""
from msl.qt import QtWidgets, application, ToggleSwitch


def print_state(checked):
    print('The switch is {}'.format('on' if checked else 'off'))


def show():
    app = application()
    window = QtWidgets.QWidget()
    window.setWindowTitle('Toggle Switch Example')
    hbox = QtWidgets.QHBoxLayout()
    ts = ToggleSwitch(window)
    ts.toggled.connect(print_state)
    hbox.addWidget(ts)
    window.setLayout(hbox)
    window.show()
    app.exec_()


if __name__ == '__main__':
    show()
