"""
A :class:`~msl.qt.widget.line_edit.LineEdit` example.
"""
from random import randint

from msl.qt import LineEdit
from msl.qt import QtWidgets
from msl.qt import application
from msl.qt import QtCore


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.e1 = LineEdit(text='fixed', read_only=True)
        self.e2 = LineEdit(text='enter text', rescale=True, text_changed=self.on_text_changed)
        self.e3 = LineEdit(rescale=True, tooltip='Connected to QTimer')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.e1)
        layout.addWidget(self.e2)
        layout.addWidget(self.e3)
        self.setLayout(layout)

    def on_timeout(self):
        self.e3.setText('x' * randint(10, 25))

    def on_text_changed(self, text):
        print(f'The text is now {text!r}')


def show():
    app = application()
    w = Window()
    w.show()
    app.exec()


if __name__ == '__main__':
    show()
