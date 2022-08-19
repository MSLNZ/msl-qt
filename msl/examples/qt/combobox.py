"""
A :class:`~msl.qt.widget.combobox.ComboBox` example.
"""
from msl.qt import ComboBox
from msl.qt import QtWidgets
from msl.qt import application
from msl.qt.convert import to_qicon


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.c1 = ComboBox(
            items='has tooltip',
            tooltip='only 1 item :(',
        )
        self.c2 = ComboBox(
            items=[c for c in 'abcdefg'] + ['initial'],
            initial='initial',
            text_changed=self.on_text_changed,
        )
        self.c3 = ComboBox(
            items={
                'data': 6,
                'icon': to_qicon(20),
                'icon-data': (to_qicon(12), 'icon'),
            },
            index_changed=self.on_index_changed,
        )
        self.c4 = ComboBox(parent=self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.c1)
        layout.addWidget(self.c2)
        layout.addWidget(self.c3)
        layout.addWidget(self.c4)
        self.setLayout(layout)

    def on_index_changed(self, index):
        data = self.sender().itemData(index)
        print(f'index={index}, data={data}')

    @staticmethod
    def on_text_changed(text):
        print(f'text: {text}')


def show():
    app = application()
    w = Window()
    w.show()
    app.exec()


if __name__ == '__main__':
    show()
