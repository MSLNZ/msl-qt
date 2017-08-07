"""
Display all the icons available in QStyle.StandardPixmap and in the *standard* Windows DLL/EXE files.
"""
from PyQt5 import QtWidgets, QtCore


class ShowIcons(QtWidgets.QTabWidget):

    def __init__(self):
        super().__init__()

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

    def add_qt_tab(self, label, icons):
        """Add the Qt icons."""
        tab = QtWidgets.QWidget()
        self.addTab(tab, label)

        layout = QtWidgets.QGridLayout()

        count = 0
        num_cols = 4
        for i in icons:
            button = QtWidgets.QPushButton(i)
            button.setIcon(icon(getattr(QtWidgets.QStyle, i)))

            layout.addWidget(button, count // num_cols, count % num_cols)
            count += 1

        tab.setLayout(layout)

    def add_windows_tab(self):
        """Add the icons from the Windows DLL and EXE files."""
        num_cols = 12
        filename = self.windows_files[self.windows_index]

        tab = QtWidgets.QWidget()
        self.addTab(tab, filename)

        layout = QtWidgets.QGridLayout()

        index = 0
        while True:
            button = QtWidgets.QPushButton(str(index))
            try:
                button.setIcon(icon('{}|{}'.format(filename, str(index))))
            except IOError:
                break

            layout.addWidget(button, index // num_cols, index % num_cols)
            index += 1

        tab.setLayout(layout)

        self.windows_index += 1
        if self.windows_index == len(self.windows_files):
            self.timer.stop()
            prompt.information('Done loading icons.')


if __name__ == '__main__':
    import sys
    from msl.qt import application, icon, prompt

    app = application()
    s = ShowIcons()
    s.setWindowTitle('Standard Icons')
    s.show()
    sys.exit(app.exec())
