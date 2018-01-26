"""
Exception handling used by **MSL-Qt**.
"""
import logging
import traceback

from . import QtWidgets, Qt, application

logger = logging.getLogger(__name__)


def excepthook(exc_type, exc_obj, exc_traceback):
    """Displays unhandled exceptions in a :class:`QtWidgets.QMessageBox`.

    See :func:`sys.excepthook` for more details.

    To implement the :func:`excepthook` in your own application include the following:

    .. code-block:: python

        import sys
        from msl import qt

        sys.excepthook = qt.excepthook

    """
    def event_handler(e):
        """Resize the QMessageBox"""
        result = QtWidgets.QMessageBox.event(msg, e)

        detailed_text = msg.findChild(QtWidgets.QTextEdit)
        if not detailed_text or not detailed_text.isVisible():
            return result

        detailed_text.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)
        detailed_text.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)

        msg.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)
        msg.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)

        return result

    details = ''.join(
        ['Traceback (most recent call last):\n'] +
        traceback.format_tb(exc_traceback) +
        [exc_obj.__class__.__name__ + ': ' + str(exc_obj)]
    )

    logger.error(details)

    # ensure that a QApplication exists
    app = application()

    # add a prefix to the title bar
    w = app.activeWindow()
    prefix = 'MSL' if w is None or not w.windowTitle() else w.windowTitle()

    msg = QtWidgets.QMessageBox()

    # want to be able to resize the QMessageBox to allow for the
    # DetailedText to be read easier
    # see http://www.qtcentre.org/threads/24888-Resizing-a-QMessageBox
    msg.event = event_handler

    msg.setSizeGripEnabled(True)
    msg.setWindowTitle(prefix + ' || Unhandled Exception')
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(exc_obj.__class__.__name__ + ':')
    msg.setInformativeText(str(exc_obj))
    msg.setDetailedText(details)
    msg.raise_()
    msg.exec_()
