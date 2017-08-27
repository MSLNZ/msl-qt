"""
Displays :mod:`logging` messages.
"""
import logging

from PyQt5 import QtWidgets, QtGui, Qt

from msl.qt import get_icon, prompt


class Logger(logging.Handler, QtWidgets.QWidget):

    def __init__(self, **kwargs):
        """Displays :mod:`logging` messages.

        Parameters
        ----------
        **kwargs
            The keyword arguments are passed to :obj:`logging.basicConfig`.
        """
        logging.Handler.__init__(self)
        QtWidgets.QWidget.__init__(self)

        # a list of all the LogRecords that were emitted
        self._records = []
        self._num_displayed = 0

        self.color_map = {
            logging.CRITICAL: QtGui.QColor(255, 0, 0),
            logging.ERROR: QtGui.QColor(175, 25, 25),
            logging.WARN: QtGui.QColor(180, 100, 127),
            logging.INFO: QtGui.QColor(0, 0, 255),
            logging.DEBUG: QtGui.QColor(127, 127, 127),
            logging.NOTSET: QtGui.QColor(40, 110, 95)
        }

        self._level_names = {
            'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARN': logging.WARN,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG
        }

        # the MSL-Equipment package has a logging.DEMO level
        self._has_demo_level = hasattr(logging, 'DEMO')
        if self._has_demo_level:
            self.color_map[logging.DEMO] = QtGui.QColor(93, 170, 78)
            self._level_names['DEMO'] = logging.DEMO

        # configure logging
        self._current_level = kwargs.pop('level', logging.INFO)
        handlers = (self,) + kwargs.pop('handlers', ())
        format = kwargs.pop('format', '%(asctime)s [%(levelname)s] -- %(name)s -- %(message)s')
        logging.basicConfig(level=logging.NOTSET, handlers=handlers, format=format, **kwargs)

        #
        # create the widgets
        #

        self._level_combobox = QtWidgets.QComboBox(self)
        for name in sorted(self._level_names, key=self._level_names.get, reverse=False):
            self._level_combobox.addItem(name, userData=self._level_names[name])
        for key in self._level_names:
            if self._level_names[key] == self._current_level:
                self._level_combobox.setCurrentText(key)
                break
        self._level_combobox.currentTextChanged.connect(self._update_records)
        self._level_combobox.setToolTip('Select the logging level')

        self._level_checkbox = QtWidgets.QCheckBox()
        self._level_checkbox.setChecked(False)
        self._level_checkbox.stateChanged.connect(self._level_checkbox_changed)
        self._update_level_checkbox_tooltip()

        self._label = QtWidgets.QLabel()

        self._save_button = QtWidgets.QPushButton()
        self._save_button.setIcon(get_icon(Qt.QStyle.SP_DialogSaveButton))
        self._save_button.clicked.connect(self._save_records)
        self._save_button.setToolTip('Save the log records')

        self._text_browser = QtWidgets.QTextBrowser(self)
        self._text_browser.setLineWrapMode(QtWidgets.QTextBrowser.NoWrap)

        #
        # add the widgets to the layout
        #

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self._level_combobox)
        top.addWidget(self._level_checkbox)
        top.addWidget(self._label, stretch=1)
        top.addWidget(self._save_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self._text_browser)
        self.setLayout(layout)

    @property
    def records(self):
        """:obj:`list` of :obj:`logging.LogRecord`: A history of all the log records."""
        return self._records

    def emit(self, record):
        """Overrides :obj:`logging.Handler.emit`."""
        self._records.append(record)
        if record.levelno >= self._level_combobox.currentData():
            self._append_record(record)

    def view_latest_message(self):
        """Move the vertical scrollbar to display the latest logging message."""
        vsb = self._text_browser.verticalScrollBar()
        vsb.setValue(vsb.maximum())

    def _append_record(self, record):
        """Append a LogRecord to the QTextBrowser."""
        if self._level_checkbox.isChecked() and record.levelno != self._level_combobox.currentData():
            return
        msg = self.format(record)
        self._text_browser.setTextColor(self.color_map[record.levelno])
        self._text_browser.append(msg)
        self._num_displayed += 1
        self._update_label()

    def _update_records(self, name):
        """
        Clears the QTextBrowser and adds all the LogRecords that have a
        levelno >= the currently-selected logging level.
        """
        self._num_displayed = 0
        self._text_browser.clear()
        self._update_level_checkbox_tooltip()
        levelno = self._level_names[name]
        for record in self._records:
            if record.levelno >= levelno:
                self._append_record(record)

    def _save_records(self, checked):
        """Save the LogRecords that are currently displayed in the QTextBrowser to a file."""
        path = prompt.save(filters={'Log Files': '*.log'}, title='Save the Log Records')
        if path is None:
            return
        with open(path, 'w') as fp:
            fp.writelines(self._text_browser.toPlainText())

    def _level_checkbox_changed(self, state):
        self._update_records(self._level_combobox.currentText())

    def _update_level_checkbox_tooltip(self):
        """Update the ToolTip for self._level_checkbox"""
        self._level_checkbox.setToolTip('Show {} level only?'.format(self._level_combobox.currentText()))

    def _update_label(self):
        """Update the label that shows the number of LogRecords that are visible."""
        if self._num_displayed == len(self._records):
            self._label.setText('Displaying all log records')
        else:
            self._label.setText('Displaying {} of {} log records'.format(self._num_displayed, len(self._records)))