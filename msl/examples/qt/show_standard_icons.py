"""
Display all the icons available in QStyle.StandardPixmap and in the *standard* Windows DLL/EXE files.
"""
from PyQt5 import QtWidgets, QtCore

from msl.qt import application, icon, prompt


class ShowStandardIcons(object):

    def __init__(self):

        app = application()

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setWindowTitle('Standard Icons')
        self.tab_widget.closeEvent = self.close_event

        self.num_icons = 0
        self.zoom_widget = QtWidgets.QLabel()
        self.zoom_widget.setScaledContents(True)
        self.zoom_size = QtCore.QSize(512, 512)
        self.zoom_widget.resize(self.zoom_size)

        qt_icons = [sp for sp in dir(QtWidgets.QStyle) if sp.startswith('SP_')]
        self.add_qt_tab('Qt Icons', qt_icons)

        self.windows_files = [
            'accessibilitycpl',
            'compstui',
            'ddores',
            'dmdskres',
            'explorer',
            'gameux',
            'ieframe',
            'imageres',
            'mmcndmgr',
            'mmres',
            'moricons',
            'netcenter',
            'netshell',
            'networkexplorer',
            'pifmgr',
            'pnidui',
            'sensorscpl',
            'setupapi',
            'shell32',
            'wmploc',
            'wpdshext'
        ]
        self.windows_index = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.add_windows_tab)
        self.timer.start(0)

        app.exec()

    def add_qt_tab(self, label, icons):
        """Add the Qt icons."""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, label)

        layout = QtWidgets.QGridLayout()

        count = 0
        num_cols = 4
        for i in icons:
            button = QtWidgets.QPushButton(i)
            ico = icon(getattr(QtWidgets.QStyle, i))
            button.setIcon(ico)
            button.clicked.connect(lambda dummy, ic=ico, n=i: self.zoom(dummy, ic, n))

            layout.addWidget(button, count // num_cols, count % num_cols)
            count += 1
            self.num_icons += 1

        tab.setLayout(layout)

        # show the main widget now, after we have drawn some icons
        self.tab_widget.resize(self.tab_widget.sizeHint())
        self.tab_widget.show()

    def add_windows_tab(self):
        """Add the icons from the Windows DLL and EXE files."""
        num_cols = 12
        filename = self.windows_files[self.windows_index]

        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, filename)

        layout = QtWidgets.QGridLayout()

        index = 0
        while True:
            button = QtWidgets.QPushButton(str(index))
            try:
                name = '{}|{}'.format(filename, str(index))
                ico = icon(name)
            except IOError:
                break

            button.setIcon(ico)
            button.clicked.connect(lambda dummy, ic=ico, n=name: self.zoom(dummy, ic, n))
            layout.addWidget(button, index // num_cols, index % num_cols)
            index += 1
            self.num_icons += 1

        tab.setLayout(layout)

        self.windows_index += 1
        if self.windows_index == len(self.windows_files):
            self.timer.stop()
            prompt.information('Loaded {} icons.'.format(self.num_icons))

    def zoom(self, dummy, ico, name):
        self.zoom_widget.setWindowTitle(name)
        self.zoom_widget.setPixmap(ico.pixmap(self.zoom_size))
        self.zoom_widget.setWindowState(QtCore.Qt.WindowActive)
        self.zoom_widget.activateWindow()
        self.zoom_widget.show()

    def close_event(self, event):
        self.zoom_widget.close()


if __name__ == '__main__':
    ShowStandardIcons()
