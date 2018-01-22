"""
Example showing the use of the :obj:`ConfigurationViewer <msl.qt.equipment.configuration_viewer.ConfigurationViewer>`
widget.
"""
from msl.qt import application
from msl.qt.equipment import ConfigurationViewer


def show():
    app = application()
    w = ConfigurationViewer()
    w.setWindowTitle('MSL-Equipment Configuration Viewer')
    w.resize(app.desktop().width()//2, app.desktop().height()//2)
    w.show()
    app.exec_()


if __name__ == '__main__':
    show()
