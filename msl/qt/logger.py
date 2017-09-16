"""
A :class:`~QtWidgets.QWidget` to display :mod:`logging` messages.
"""
import random
import logging
import datetime

from PyQt5 import QtWidgets, QtGui, Qt

from msl.qt import prompt
from msl.qt.io import get_icon


class Logger(logging.Handler, QtWidgets.QWidget):

    def __init__(self,
                 level=logging.INFO,
                 fmt='%(asctime)s [%(levelname)s] -- %(name)s -- %(message)s',
                 datefmt=None,
                 ):
        """A :class:`~QtWidgets.QWidget` to display :mod:`logging` messages.

        Parameters
        ----------
        level : :obj:`int`, optional
            The default `logging level`_ to use to display the :obj:`~logging.LogRecord`
            (e.g., ``logging.INFO``).

            .. _logging level: https://docs.python.org/3/library/logging.html#logging-levels

        fmt : :obj:`str`, optional
            The `string format`_ to use to display the :obj:`~logging.LogRecord`.

            .. _string format: https://docs.python.org/3/library/logging.html#logrecord-attributes

        datefmt : :obj:`str` or :obj:`None`, optional
            The `date format`_ to use for the time stamp. If :obj:`None` then the ``ISO8601``
            date format is used.

            .. _date format: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

        Example
        -------
        To view an example of the :class:`Logger` widget run:

        >>> from msl.examples.qt import logger
        >>> logger.show() # doctest: +SKIP
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

        #
        # configure logging
        #

        root = logging.getLogger()
        self._current_level = level  # set the initial logging level
        root.setLevel(logging.NOTSET)  # however, the root logger must have access to all logging levels
        self.setFormatter(logging.Formatter(fmt, datefmt))
        logging.getLogger().addHandler(self)

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
        self._update_label()

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
        top.addStretch()
        top.addWidget(self._label)
        top.addStretch()
        top.addWidget(self._save_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self._text_browser)
        self.setLayout(layout)

    @property
    def records(self):
        """:obj:`list` of :obj:`~logging.LogRecord`: The history of all the log records."""
        return self._records

    def emit(self, record):
        """Overrides :obj:`logging.Handler.emit`."""
        self._records.append(record)
        if record.levelno >= self._level_combobox.currentData():
            self._append_record(record)
        self._update_label()

    def show_latest(self):
        """Move the vertical scrollbar to show the latest logging record."""
        vsb = self._text_browser.verticalScrollBar()
        vsb.setValue(vsb.maximum())

    def save(self, path, level=logging.INFO):
        """Save log records to a file.

        Parameters
        ----------
        path : :obj:`str`
            The path to save the log records to. Appends the records to the file
            if the file already exists, otherwise creates a new log file. It is
            recommended that the file extension be ``.log``, but not mandatory.
        level : :obj:`int`, optional
            All :obj:`~logging.LogRecord`\'s with a logging level >= `level`
            will be saved.
        """
        with open(path, 'a') as fp:
            self._write_header(fp)
            for record in self._records:
                if record.levelno >= level:
                    fp.write(self.format(record) + '\n')
            fp.write('\n')

    def _append_record(self, record):
        """Append a LogRecord to the QTextBrowser."""
        if self._level_checkbox.isChecked() and record.levelno != self._level_combobox.currentData():
            return
        msg = self.format(record)
        try:
            self._text_browser.setTextColor(self.color_map[record.levelno])
        except KeyError:
            self._add_new_level(record)
            self._text_browser.setTextColor(self.color_map[record.levelno])
        self._text_browser.append(msg)
        self._num_displayed += 1

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
        self._update_label()

    def _save_records(self, checked):
        """Save the LogRecords that are currently displayed in the QTextBrowser to a file."""
        if len(self._records) == 0:
            prompt.information('There are no log records to save.')
            return
        option = QtWidgets.QFileDialog.DontConfirmOverwrite
        title = 'Save the Log Records (appends to an existing file)'
        path = prompt.save(filters={'Log Files': '*.log'}, title=title, options=option)
        if path is None:
            return
        if not path.endswith('.log'):
            path += '.log'
        with open(path, 'a') as fp:
            self._write_header(fp)
            fp.writelines(self._text_browser.toPlainText())
            fp.write('\n\n')

    def _level_checkbox_changed(self, state):
        self._update_records(self._level_combobox.currentText())

    def _update_level_checkbox_tooltip(self):
        """Update the ToolTip for self._level_checkbox"""
        self._level_checkbox.setToolTip('Show {} level only?'.format(self._level_combobox.currentText()))

    def _update_label(self):
        """Update the label that shows the number of LogRecords that are visible."""
        if not self._records:
            self._label.setText('There are no log records')
        elif self._num_displayed == len(self._records):
            self._label.setText('Displaying all log records')
        else:
            self._label.setText('Displaying {} of {} log records'.format(self._num_displayed, len(self._records)))

    def _write_header(self, fp):
        fp.write('# Saved {}\n'.format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))

    def _add_new_level(self, record):
        # the MSL-Equipment package has a logging.DEMO level
        if record.levelname == 'DEMO':
            color = QtGui.QColor(93, 170, 78)
        else:
            color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.color_map[record.levelno] = color
        self._level_names[record.levelname] = record.levelno

        for i in range(self._level_combobox.count()):
            if record.levelno < self._level_combobox.itemData(i):
                self._level_combobox.insertItem(i, record.levelname, userData=record.levelno)
                return

        self._level_combobox.addItem(record.levelname, userData=record.levelno)
