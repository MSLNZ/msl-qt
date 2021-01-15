"""
Example to show the :class:`~msl.qt.editor.python.PythonEditor`.
"""
import os
import sys
import time
import logging

from msl.qt import (
    QtWidgets,
    QtCore,
    excepthook,
    utils,
    application,
)
from msl.qt.editor import (
    PythonEditor,
    COLOR_SCHEME_MAP,
)


class Main(QtWidgets.QWidget):

    def __init__(self, text, style, **kwargs):
        super(Main, self).__init__(**kwargs)

        self.editor = PythonEditor(font=16, color_scheme_name=style)

        self.cursor_label = QtWidgets.QLabel()
        self.editor.cursorPositionChanged.connect(self.update_label)

        styles = list(COLOR_SCHEME_MAP.keys())
        self.styles = QtWidgets.QComboBox()
        self.styles.setFocusPolicy(QtCore.Qt.NoFocus)
        self.styles.addItems(styles)
        self.styles.setCurrentIndex(styles.index(style))
        self.styles.currentTextChanged.connect(self.update_style)
        self.styles.setMaxVisibleItems(25)

        self.editor.set_text(text)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.cursor_label)
        layout.addWidget(self.styles)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def update_style(self, style_name):
        self.editor.color_scheme = style_name

    def update_label(self):
        cursor = self.editor.textCursor()
        self.cursor_label.setText('{}:{} [{}]'.format(
            cursor.blockNumber(),
            cursor.columnNumber(),
            cursor.position())
        )


def show():
    sys.excepthook = excepthook

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)-7s] -- %(name)s -- %(message)s',
    )

    path = os.path.join(os.path.dirname(__file__), 'editor_sample.py')
    with open(path) as fp:
        text = fp.read() * 1  # can make the file bigger

    t0 = time.perf_counter()
    app = application()
    main = Main(text, 'Chromodynamics')
    geo = utils.screen_geometry(main)
    main.resize(geo.width()*2//3, geo.height()//2)
    main.show()
    took = time.perf_counter()-t0
    print('Inserted {} lines in {:.3f} seconds'.format(main.editor.document().lineCount(), took))
    app.exec()


if __name__ == '__main__':
    show()
