"""
A :class:`~QtWidgets.QWidget` for :class:`~msl.equipment.connection_msl.ConnectionMessageBased`.

This widget allows for reading/writing messages from/to equipment.
"""
import time
import traceback

from msl.qt import QtWidgets, QtCore, QtGui, prompt
from msl.qt.io import get_icon, get_drag_enter_paths
from msl.qt.equipment import show_record


class MessageBased(QtWidgets.QWidget):

    def __init__(self, connection, parent=None):
        """
        A :class:`~QtWidgets.QWidget` for a :class:`~msl.equipment.connection_msl.ConnectionMessageBased` connection.

        This widget allows for reading/writing messages from/to equipment.

        Parameters
        ----------
        connection : :class:`~msl.equipment.connection_msl.ConnectionMessageBased`
            The connection to the equipment.
        parent : :class:`QtWidgets.QWidget`
            The parent widget.

        Example
        -------
        To view an example of the :class:`MessageBased` widget that will send messages to a
        *dummy* :class:`~msl.equipment.record_types.EquipmentRecord` in demo mode, run:

        >>> from msl.examples.qt.equipment import message_based # doctest: +SKIP
        >>> message_based.show() # doctest: +SKIP
        """
        super(MessageBased, self).__init__(parent=parent)

        r = connection.equipment_record
        self.setWindowTitle('{} || {} || {}'.format(r.manufacturer, r.model, r.serial))
        self.setAcceptDrops(True)

        self._conn = connection
        self._dropped_commands = []
        self._abort_execution = False
        self._command_list = []

        self._header = ['Action', 'Delay', 'Message', 'Reply']
        self._actions = ['write', 'read', 'query', 'delay']
        self._table = QtWidgets.QTableWidget(0, len(self._header), self)
        self._table.setHorizontalHeaderLabels(self._header)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._table.horizontalHeader().customContextMenuRequested.connect(self._show_horizontal_popup_menu)
        self._table.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._table.verticalHeader().customContextMenuRequested.connect(self._show_vertical_popup_menu)

        self._timeout_spinbox = QtWidgets.QDoubleSpinBox()
        self._timeout_spinbox.setToolTip('<html>The timeout value to use for <i>read</i> commands</html>')
        self._timeout_spinbox.setRange(0, 999999999)
        if 'ConnectionPyVISA' in '{}'.format(connection.__class__.__bases__):  # a PyVISA connection
            self._timeout_spinbox.setSuffix(' ms')
            self._timeout_spinbox.setDecimals(0)
        else:
            self._timeout_spinbox.setSuffix(' s')
            self._timeout_spinbox.setDecimals(2)
        try:
            self._timeout_spinbox.setValue(self._conn.timeout)
        except TypeError:  # in case the connection is established in demo mode
            self._timeout_spinbox.setValue(0)
        self._timeout_spinbox.valueChanged.connect(self._update_timeout)

        self._use_rows = QtWidgets.QLineEdit()
        self._use_rows.setToolTip('Enter the rows to execute or leave blank to execute all rows.\nFor example: 1,3,5-8')

        self._execute_icon = get_icon(QtWidgets.QStyle.SP_ArrowRight)
        self._continuous_icon = get_icon(QtWidgets.QStyle.SP_BrowserReload)
        self._abort_icon = get_icon(QtWidgets.QStyle.SP_BrowserStop)
        self._clear_icon = get_icon(QtWidgets.QStyle.SP_DialogResetButton)
        self._remove_icon = get_icon(QtWidgets.QStyle.SP_DialogCancelButton)
        self._insert_before_icon = get_icon(QtWidgets.QStyle.SP_DialogOkButton)
        # create an insert_after_icon by transforming the insert_before_icon
        size = self._insert_before_icon.availableSizes()[-1]
        pixmap = self._insert_before_icon.pixmap(size).transformed(QtGui.QTransform().scale(-1, 1))
        self._insert_after_icon = QtGui.QIcon(pixmap)

        self._execute_thread = _Execute(self)
        self._execute_thread.finished.connect(self._check_if_looping)
        self._execute_thread.sig_error.connect(self._execute_error)
        self._execute_thread.sig_update_row_color.connect(self._update_row_appearance)
        self._execute_thread.sig_highlight_row.connect(self._highlight_row)
        self._execute_thread.sig_update_reply.connect(self._update_reply)
        self._execute_thread.sig_show_execute_icon.connect(self._show_execute_icon)

        self._loop_checkbox = QtWidgets.QCheckBox()
        self._loop_checkbox.setToolTip('Run continuously?')
        self._loop_checkbox.clicked.connect(self._show_execute_icon)

        save_icon = get_icon(QtWidgets.QStyle.SP_DriveFDIcon)
        self._save_button = QtWidgets.QPushButton(save_icon, 'Save')
        self._save_button.setToolTip('Save the table to a tab-delimited file')
        self._save_button.clicked.connect(self._save)

        self._info_button = QtWidgets.QPushButton(get_icon(QtWidgets.QStyle.SP_FileDialogInfoView), '')
        self._info_button.setToolTip('Display the information about the equipment')
        self._info_button.clicked.connect(lambda clicked, record=r: show_record(record))

        self._status_label = QtWidgets.QLabel()

        self._execute_button = QtWidgets.QPushButton()
        self._execute_button.clicked.connect(self._execute_start)
        self._show_execute_icon()

        self._status_label.setText('Create a new Execution Table or\n'
                                   'Drag & Drop or Copy & Paste\n'
                                   'a previous Execution Table')

        execute_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel('Timeout'), 1, 0, alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self._timeout_spinbox, 1, 1, 1, 2)
        grid.addWidget(QtWidgets.QLabel('Rows'), 2, 0, alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self._use_rows, 2, 1, 1, 2)
        grid.addWidget(self._execute_button, 3, 0, 1, 2)
        grid.addWidget(self._loop_checkbox, 3, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        grid.addWidget(self._save_button, 4, 0, 1, 2)
        grid.addWidget(self._info_button, 4, 2, 1, 1)
        grid.addWidget(self._status_label, 5, 0, 1, 3, alignment=QtCore.Qt.AlignBottom)
        grid.setRowStretch(5, 1)
        execute_widget.setLayout(grid)

        self._create_row()
        self._table.resizeColumnsToContents()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._table)
        splitter.addWidget(execute_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([1, 0])

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def keyPressEvent(self, event):
        """Overrides `keyPressEvent <https://doc.qt.io/qt-5/qwidget.html#keyPressEvent>`_."""
        if event.matches(QtGui.QKeySequence.Paste):
            lines = QtWidgets.QApplication.clipboard().text().splitlines()
            self._insert_lines(lines)

    def dragEnterEvent(self, event):
        """Overrides `dragEnterEvent <https://doc.qt.io/qt-5/qwidget.html#dragEnterEvent>`_."""
        self._dropped_commands = []
        paths = get_drag_enter_paths(event, '*.txt')
        if paths:
            for path in paths:
                with open(path) as fp:
                    self._dropped_commands.extend(fp.readlines())
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Overrides `dragMoveEvent <https://doc.qt.io/qt-5/qwidget.html#dragMoveEvent>`_."""
        event.accept()

    def dropEvent(self, event):
        """Overrides `dropEvent <https://doc.qt.io/qt-5/qwidget.html#dropEvent>`_."""
        self._insert_lines(self._dropped_commands)

    def _update_timeout(self, val):
        self._conn.timeout = val

    def _show_vertical_popup_menu(self):
        """Handles a right-click on the selected row button(s)"""
        selected = self._table.selectionModel().selectedRows()
        if selected:
            r = 'row' if len(selected) == 1 else 'rows'
            t = 'the' if len(selected) == 1 else 'each'
            menu = QtWidgets.QMenu(self)
            remove = menu.addAction(self._remove_icon, 'Delete the selected ' + r)
            remove.triggered.connect(lambda: self._remove_selected_rows(selected))
            insert_before = menu.addAction(self._insert_before_icon, 'Insert a row before %s selected row' % t)
            insert_before.triggered.connect(lambda: self._insert_selected(selected, 0))
            insert_after = menu.addAction(self._insert_after_icon, 'Insert a row after %s selected row' % t)
            insert_after.triggered.connect(lambda: self._insert_selected(selected, 1))
            clear = menu.addAction(self._clear_icon, 'Remove all of the empty rows')
            clear.triggered.connect(self._remove_empty_rows)
            menu.exec_(QtGui.QCursor.pos())

    def _show_horizontal_popup_menu(self):
        """handles a right-click on the selected column button(s)"""
        selected = self._table.selectionModel().selectedColumns()
        if len(selected) == len(self._header):
            menu = QtWidgets.QMenu(self)
            clear = menu.addAction(self._clear_icon, 'Clear the table')
            clear.triggered.connect(self._clear_table)
            menu.exec_(QtGui.QCursor.pos())

    def _remove_selected_rows(self, selected):
        """remove a row either before or after the selected row(s)"""
        for index in sorted((s.row() for s in selected), reverse=True):
            self._table.removeRow(index)
        if self._table.rowCount() == 0:
            self._create_row()

    def _insert_selected(self, selected, offset):
        """insert a row either before or after the selected row(s)"""
        for index in sorted(s.row() for s in selected):
            self._create_row(index + offset)
            offset += 1

    def _create_row(self, index=None):
        """Create a new row.

        Parameters
        ----------
        index : :class:`int` or :obj:`None`
            If :obj:`None` then append a row, else the index number (0 based) for
            where to create and insert the row.
        """
        cb = QtWidgets.QComboBox()
        cb.addItems(self._actions)
        sb = QtWidgets.QSpinBox()
        sb.setRange(0, 999999)
        msg = QtWidgets.QLineEdit()
        reply = QtWidgets.QLineEdit()
        reply.setReadOnly(True)
        index = index if index is not None else self._table.rowCount()
        self._table.insertRow(index)
        self._table.setCellWidget(index, 0, cb)
        self._table.setCellWidget(index, 1, sb)
        self._table.setCellWidget(index, 2, msg)
        self._table.setCellWidget(index, 3, reply)
        cb.currentTextChanged.connect(lambda text: self._update_row_appearance(text, index))
        self._update_row_appearance(cb.currentText(), index)

    def _update_row_appearance(self, text, index):
        """Sets the enabled/disabled, the tooltip, the font, the color of a row in the table"""
        delay_widget = self._table.cellWidget(index, 1)
        message_widget = self._table.cellWidget(index, 2)
        reply_widget = self._table.cellWidget(index, 3)

        delay_widget.setEnabled(text != 'write')
        message_widget.setEnabled(text in ('write', 'query'))
        reply_widget.setEnabled(text != 'delay')

        # set the Delay tool tip
        if text == 'read':
            delay_widget.setToolTip('The time to wait, in ms, before sending the read command')
        elif text == 'query':
            delay_widget.setToolTip('The time to wait, in ms, between sending the write and read commands')
        elif text == 'delay':
            delay_widget.setToolTip('No message is sent. Just insert a pause, in ms')
        else:
            delay_widget.setToolTip('A delay is not used for a write command')

        # set the style sheet for the Message and Reply QLineEdit's
        if text == 'delay':
            message_widget.setStyleSheet('background-color: lightgray')
            reply_widget.setStyleSheet('background-color: lightgray')
        elif text == 'read':
            message_widget.setStyleSheet('background-color: lightgray')
            reply_widget.setStyleSheet('background-color: white')
        else:
            message_widget.setStyleSheet('background-color: white')
            reply_widget.setStyleSheet('background-color: white')

        # use italic font if the reply is for a write command
        font = reply_widget.font()
        font.setItalic(text == 'write')
        reply_widget.setFont(font)

    def _insert_lines(self, lines):
        """fill the table either from a copy-paste event of from a file"""

        lines = [line.split('\t') for line in lines if len(line.split('\t')) == 4]
        if not lines:
            return

        # create a new row if the last row is not "empty"
        index = self._table.rowCount() - 1
        if self._table.cellWidget(index, 2).text() or \
                        self._table.cellWidget(index, 0).currentText() in ('read', 'delay'):
            self._create_row()
            index += 1

        for i, line in enumerate(lines):
            action, delay_str, message, reply = line
            if action not in self._actions:
                continue
            try:
                delay = int(float(delay_str))
            except:
                continue
            self._table.cellWidget(index, 0).setCurrentText(action)
            self._table.cellWidget(index, 1).setValue(delay)
            self._table.cellWidget(index, 2).setText(message.strip())
            # Shouldn't insert the replies since that could be confusing.
            # Perhaps the user gets distracted after loading a file and then forgets
            # whether they clicked the Execute button to refresh the Reply values
            if i < len(lines) - 1:
                self._create_row()
                index += 1

    def _execute_start(self):
        """start/stop the execution thread"""
        self._abort_execution = self._execute_thread.isRunning()
        if not self._execute_thread.isRunning():
            if not self._generate_command_list():
                # then there was an error generating the command list
                return
            if not self._command_list:
                prompt.critical('There are no messages to send')
                return
            self._execute_thread._error = False
            self._start_thread()

    def _start_thread(self):
        """start the execution thread"""
        self._show_abort_icon()
        self._execute_thread.start()
        self._start_time = time.time()
        time.sleep(0.1)  # block the main gui for a little bit

    def _check_if_looping(self):
        """check if the loop checkbox is checked to restart the execution thread"""
        if self._loop_checkbox.isChecked() and not self._execute_thread._error and not self._abort_execution:
            self._start_thread()
        else:
            self._show_execute_icon()

    def _show_abort_icon(self):
        """updates the icon and text of the execution button"""
        self._execute_button.setIcon(self._abort_icon)
        self._execute_button.setText('Abort')
        self._execute_button.setToolTip('Abort')
        self._save_button.setEnabled(False)

    def _show_execute_icon(self):
        """updates the icon and text of the execution button"""
        if self._execute_thread.isRunning() and not self._abort_execution:
            return
        if self._loop_checkbox.isChecked():
            self._execute_button.setIcon(self._continuous_icon)
        else:
            self._execute_button.setIcon(self._execute_icon)
        self._execute_button.setText('Execute')
        self._execute_button.setToolTip('Execute')
        self._save_button.setEnabled(True)
        self._status_label.setText('')

    def _execute_error(self, message):
        """called if there was an exception raised in the execution thread"""
        prompt.critical(message)
        self._show_execute_icon()

    def _save(self):
        """Save the table to a text file"""
        path = prompt.save(filters='Text files (*.txt)')
        if path is None:
            return
        if not path.endswith('.txt'):
            path += '.txt'
        with open(path, 'w') as fp:
            for i in range(self._table.rowCount()):
                method = self._table.cellWidget(i, 0).currentText()
                delay = self._table.cellWidget(i, 1).value()
                message = self._table.cellWidget(i, 2).text().strip()
                reply = self._table.cellWidget(i, 3).text().strip()
                fp.write('{}\t{}\t{}\t{}\n'.format(method, delay, message, reply))

    def _clear_table(self):
        """delete all rows in the table"""
        for i in range(self._table.rowCount()-1, -1, -1):
            self._table.removeRow(i)
        self._create_row()

    def _remove_empty_rows(self):
        """Remove all the empty rows (rows which have no message and reply and that are not a delay)"""
        for i in range(self._table.rowCount()-1, -1, -1):
            if self._table.cellWidget(i, 0).currentText() == 'delay':
                continue
            message = self._table.cellWidget(i, 2).text().strip()
            reply = self._table.cellWidget(i, 3).text().strip()
            if not message and not reply:
                self._table.removeRow(i)
        if self._table.rowCount() == 0:
            self._create_row()

    def _generate_command_list(self):
        """Generate the list of commands to execute"""
        # determine which rows to execute
        if self._use_rows.text():
            rows = []
            for item in self._use_rows.text().split(','):
                item = item.strip()
                if not item:
                    continue
                if item.isdigit():
                    rows.append(int(item))
                elif '-' in item:
                    item_split = item.split('-')
                    if len(item_split) != 2:
                        prompt.critical('Invalid range: ' + item)
                        return False
                    try:
                        start, end = map(int, item_split)
                    except ValueError as err:
                        prompt.critical('Invalid start-end range: {}'.format(err))
                        return False
                    if start > end:
                        prompt.critical('Start row {} > End row {}'.format(start, end))
                        return False
                    rows.extend([value for value in range(start, end+1)])
                else:
                    prompt.critical('Invalid row: ' + item)
                    return False
        else:
            rows = [i+1 for i in range(self._table.rowCount())]

        # determine which rows have commands
        self._command_list = []
        for row in rows:
            if row < 1 or row > self._table.rowCount():
                prompt.critical('Row {} does not exist'.format(row))
                return False
            index = row-1
            action = self._table.cellWidget(index, 0).currentText()
            delay = self._table.cellWidget(index, 1).value() * 1e-3
            message = self._table.cellWidget(index, 2).text().strip()
            if not message and action not in ('read', 'delay'):
                continue
            self._command_list.append((index, action, delay, message))

        return True

    def _highlight_row(self, row):
        """Change the background color of the specified row index"""
        self._table.cellWidget(row, 2).setStyleSheet('background-color: yellow')
        self._table.cellWidget(row, 3).setStyleSheet('background-color: yellow')
        self._status_label.setText('Executing row {} of {}'.format(row+1, self._table.rowCount()))

    def _update_reply(self, row, reply):
        """Update the cell text with the response from the equipment"""
        self._table.cellWidget(row, 3).setText(reply)


class _Execute(QtCore.QThread):

    sig_error = QtCore.pyqtSignal(str)
    sig_update_row_color = QtCore.pyqtSignal(str, int)
    sig_highlight_row = QtCore.pyqtSignal(int)
    sig_update_reply = QtCore.pyqtSignal(int, str)
    sig_show_execute_icon = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self._error = False

    def run(self):
        if self._error:
            return

        for index, action, delay, message in self.parent._command_list:
            if self._error or self.parent._abort_execution:
                self.sig_show_execute_icon.emit()
                break

            self.sig_highlight_row.emit(index)
            try:
                if action == 'read':
                    if delay > 0:
                        time.sleep(delay)
                    reply = self.parent._conn.read()
                elif action == 'write':
                    num_bytes = self.parent._conn.write(message)
                    reply = '<sent {} bytes>'.format(num_bytes)
                elif action == 'query':
                    reply = self.parent._conn.query(message, delay)
                elif action == 'delay':
                    time.sleep(delay)
                    reply = ''
                else:
                    assert False, 'Method "{}" not implemented'.format(action)
                self.sig_update_reply.emit(index, reply.strip())
            except Exception:
                self._error = True
                self.sig_error.emit('Row {}: {}({})\n\n{}'.format(index+1, action, message, traceback.format_exc()))
                break
            finally:
                self.sig_update_row_color.emit(action, index)
