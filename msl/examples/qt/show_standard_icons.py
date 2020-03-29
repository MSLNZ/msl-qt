"""
Display all the icons available in :obj:`QtWidgets.QStyle.StandardPixmap` and in
the *standard* Windows DLL/EXE files.
"""
from msl.qt import (
    QtWidgets,
    QtCore,
    application,
    io
)

try:
    # check if pythonnet is installed
    import clr
    has_clr = True
except ImportError:
    has_clr = False


class ShowStandardIcons(object):

    def __init__(self):

        app = application()

        self.tab_widget = QtWidgets.QTabWidget()

        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle('Standard Icons')
        self.main_window.setCentralWidget(self.tab_widget)
        self.main_window.closeEvent = self.close_event

        # add a progress bar to the status bar
        self.progress_bar = QtWidgets.QProgressBar(self.main_window.statusBar())
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.main_window.statusBar().addPermanentWidget(self.progress_bar)
        self.main_window.showMaximized()

        self.num_icons = 0
        self.file_index = 0
        self.zoom_widget = QtWidgets.QDialog()
        self.zoom_widget.setSizeGripEnabled(True)
        self.zoom_widget.resize(QtCore.QSize(256, 256))
        self.zoom_widget.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        vbox = QtWidgets.QVBoxLayout()
        self.zoom_label = QtWidgets.QLabel()
        self.zoom_label.setScaledContents(True)
        vbox.addWidget(self.zoom_label)
        self.zoom_widget.setLayout(vbox)

        qt_icons = [sp for sp in dir(QtWidgets.QStyle) if sp.startswith('SP_')]

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

        self.num_files = 1 + len(self.windows_files)
        self.progress_bar.setRange(0, self.num_files)

        self.add_qt_tab('Qt Icons', qt_icons)

        if has_clr:
            self.windows_index = 0
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.add_windows_tab)
            self.timer.start(0)
        else:
            self.update_message('Loaded {} icons.'.format(self.num_icons))
            self.progress_bar.hide()

        app.exec_()

    def add_qt_tab(self, label, icons):
        """Add the Qt icons."""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, label)

        layout = QtWidgets.QGridLayout()

        self.update_message('Loading Qt icons...')

        count = 0
        num_cols = 4
        for i in icons:
            button = QtWidgets.QPushButton(i)
            ico = io.get_icon(getattr(QtWidgets.QStyle, i))
            button.setIcon(ico)
            button.clicked.connect(lambda *args, ic=ico, n=i: self.zoom(ic, n))

            layout.addWidget(button, count // num_cols, count % num_cols)
            count += 1
            self.num_icons += 1

        tab.setLayout(layout)

        self.file_index += 1
        self.progress_bar.setValue(self.file_index)

    def add_windows_tab(self):
        """Add the icons from the Windows DLL and EXE files."""
        num_cols = 16
        filename = self.windows_files[self.windows_index]
        self.update_message('Loading icons from {}...'.format(filename))

        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, filename)

        layout = QtWidgets.QGridLayout()

        index = 0
        while True:
            button = QtWidgets.QPushButton(str(index))
            try:
                name = '{}|{}'.format(filename, str(index))
                ico = io.get_icon(name)
            except IOError:
                break

            button.setIcon(ico)
            button.clicked.connect(lambda *args, ic=ico, n=name: self.zoom(ic, n))
            layout.addWidget(button, index // num_cols, index % num_cols)
            index += 1
            self.num_icons += 1

        self.file_index += 1
        self.progress_bar.setValue(self.file_index)

        tab.setLayout(layout)

        self.windows_index += 1
        if self.windows_index == len(self.windows_files):
            self.timer.stop()
            self.update_message('Loaded {} icons.'.format(self.num_icons))
            self.progress_bar.hide()

    def update_message(self, text):
        self.main_window.statusBar().showMessage(text)

    def zoom(self, ico, name):
        self.zoom_widget.setWindowTitle(name)
        self.zoom_label.setPixmap(ico.pixmap(self.zoom_widget.size()))
        self.zoom_widget.setWindowState(QtCore.Qt.WindowActive)
        self.zoom_widget.activateWindow()
        self.zoom_widget.show()

    def close_event(self, event):
        self.zoom_widget.close()


if __name__ == '__main__':
    ShowStandardIcons()
