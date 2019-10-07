"""
Exception handling.
"""
import logging
import traceback as tb

from . import (
    Qt,
    QtGui,
    QtWidgets,
    application,
    prompt,
)

logger = logging.getLogger(__name__)


def excepthook(exctype, value, traceback):
    """Displays unhandled exceptions in a :class:`QtWidgets.QMessageBox`.

    See :func:`sys.excepthook` for more details.

    To implement the :func:`excepthook` in your own application include the following:

    .. code-block:: python

        import sys
        from msl import qt

        sys.excepthook = qt.excepthook

    """
    class ErrorDialog(QtWidgets.QDialog):

        def __init__(self):
            super(ErrorDialog, self).__init__(None, Qt.WindowCloseButtonHint)

            # add a prefix to the title bar
            w = app.activeWindow()
            prefix = 'MSL' if w is None or not w.windowTitle() else w.windowTitle()
            self.setWindowTitle(prefix + ' || Unhandled Exception')

            self.setSizeGripEnabled(True)

            self.icon_label = QtWidgets.QLabel()
            critical_icon = app.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
            largest_size = critical_icon.availableSizes()[-1]
            self.icon_label.setPixmap(critical_icon.pixmap(largest_size))

            self.error_label = QtWidgets.QLabel(value.__class__.__name__ + ':\n\n' + str(value))

            self.ok_button = QtWidgets.QPushButton('Close')
            self.ok_button.clicked.connect(self.close)
            self.ok_button.setToolTip('Close')

            self.screenshot_button = QtWidgets.QPushButton('Screenshot')
            self.screenshot_button.clicked.connect(self.save_screenshot)
            self.screenshot_button.setToolTip('Save a screenshot of this window')

            self.copy_button = QtWidgets.QPushButton('Copy')
            self.copy_button.clicked.connect(self.copy_to_clipboard)
            self.copy_button.setToolTip('Copy the error message to the system clipboard')

            self.show_details_button = QtWidgets.QPushButton('Hide details...')
            self.show_details_button.clicked.connect(self.show_hide_details)
            self.show_details_button.setToolTip('Show less information')

            self.detailed_textedit = QtWidgets.QTextEdit()
            self.detailed_textedit.setText(details)
            self.detailed_textedit.setReadOnly(True)

            expanding = QtWidgets.QSizePolicy.Expanding

            label_layout = QtWidgets.QHBoxLayout()
            label_layout.addWidget(self.icon_label)
            label_layout.addWidget(self.error_label, alignment=Qt.AlignLeft)
            label_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, expanding, expanding))

            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.screenshot_button)
            button_layout.addWidget(self.copy_button)
            button_layout.addWidget(self.show_details_button)
            button_layout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, expanding, expanding))

            layout = QtWidgets.QVBoxLayout()
            layout.addLayout(label_layout)
            layout.addLayout(button_layout)
            layout.addWidget(self.detailed_textedit, stretch=1)
            self.setLayout(layout)

        def save_screenshot(self):
            filename = prompt.save(filters='Images (*.png *.jpg *.jpeg *.bmp)')
            if filename:
                QtGui.QPixmap.grabWidget(self).toImage().save(filename)

        def show_hide_details(self):
            if self.detailed_textedit.isVisible():
                self.detailed_textedit.hide()
                self.show_details_button.setText('Show details...')
                self.show_details_button.setToolTip('Show more information')
                self.adjustSize()
            else:
                self.detailed_textedit.show()
                self.show_details_button.setText('Hide details...')
                self.show_details_button.setToolTip('Show less information')

        def copy_to_clipboard(self):
            app.clipboard().setText(self.detailed_textedit.toPlainText())

    details = ''.join(tb.format_exception(exctype, value, traceback))
    logger.error(details)

    # ensure that a QApplication exists
    app = application()

    dialog = ErrorDialog()
    dialog.raise_()
    dialog.exec_()
