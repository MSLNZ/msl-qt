"""
A :class:`~msl.qt.widget.checkbox.CheckBox` example.
"""
from msl.qt import CheckBox
from msl.qt import Qt
from msl.qt import QtWidgets
from msl.qt import application


def on_state_changed(state):
    print(f'The state of "Click Me!" is now {state}')


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.c1 = CheckBox(initial=True)
        self.c2 = CheckBox(text='Click Me!', state_changed=on_state_changed)
        self.c3 = CheckBox(
            initial=Qt.CheckState.PartiallyChecked,
            tooltip='partially checkable without a slot'
        )
        self.c4 = CheckBox(checkable=False, text='uncheckable')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.c1)
        layout.addWidget(self.c2)
        layout.addWidget(self.c3)
        layout.addWidget(self.c4)
        self.setLayout(layout)


def show():
    app = application()
    w = Window()
    w.show()
    app.exec()


if __name__ == '__main__':
    show()
