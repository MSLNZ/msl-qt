"""
A :class:`~QtWidgets.QWidget` for :class:`~msl.equipment.connection_msl.ConnectionMessageBased`.
"""

import time

from PyQt5 import QtWidgets, QtCore, QtGui

from msl.qt.io import get_drag_enter_paths


class MessageBased(QtWidgets.QWidget):

    def __init__(self, connection, parent=None):
        """
        A :class:`~QtWidgets.QWidget` for :class:`~msl.equipment.connection_msl.ConnectionMessageBased`.

        Parameters
        ----------
        connection : :class:`~msl.equipment.connection.Connection`
            The connection to the equipment.

        parent : :class:`~QtWidgets.QWidget`
            The parent widget.
        """
        super(MessageBased, self).__init__(parent)

        self._conn = connection

        r = connection.equipment_record
        self.setWindowTitle('{} || {} || {}'.format(r.manufacturer, r.model, r.serial))
        self.setAcceptDrops(True)
        self._dropped_commands = []
        self.abort_execution = False
        self.font = None

        self.header = ['Method', 'Message', 'Reply']
        self.table = QtWidgets.QTableWidget(0, len(self.header), self)
        self.table.setHorizontalHeaderLabels(self.header)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_horizontal_popup_menu)
        self.table.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.verticalHeader().customContextMenuRequested.connect(self.show_vertical_popup_menu)

        self.query_delay_spinbox = QtWidgets.QDoubleSpinBox()
        self.query_delay_spinbox.setToolTip('The delay to wait between a <b>write</b> and a <b>read</b>')
        self.query_delay_spinbox.setMinimum(0.0)
        self.query_delay_spinbox.setValue(self._conn.query_delay)
        self.query_delay_spinbox.setSuffix(' seconds')
        self.query_delay_spinbox.setSingleStep(0.1)

        self.use_rows = QtWidgets.QLineEdit()
        self.use_rows.setToolTip('Enter the rows to execute or leave blank to execute all rows.\nFor example: 1,3,5-8')

        style = self.style()
        self.remove_icon = style.standardIcon(style.SP_DialogCancelButton)
        self.insert_before_icon = style.standardIcon(style.SP_DialogOkButton)
        self.insert_after_icon = QtGui.QIcon(self.insert_before_icon.pixmap(16, 16).transformed(QtGui.QTransform().scale(-1, 1)))
        self.execute_icon = style.standardIcon(style.SP_FileDialogDetailedView)
        self.abort_icon = style.standardIcon(style.SP_BrowserStop)
        self.clear_icon = style.standardIcon(style.SP_DialogResetButton)

        self.execute_thread = Execute(self)
        self.execute_thread.sigError.connect(self.execute_error)
        self.execute_thread.finished.connect(self.update_execute_button)
        self.execute_button = QtWidgets.QPushButton()
        self.execute_button.clicked.connect(self.execute_start)
        self.update_execute_button()

        save_icon = style.standardIcon(style.SP_DriveFDIcon)
        self.save_button = QtWidgets.QPushButton(save_icon, 'Save')
        self.save_button.setToolTip('Save the table to a tab-delimited file')
        self.save_button.clicked.connect(self.save)

        execute_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel('Delay'), 1, 0, alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.query_delay_spinbox, 1, 1)
        grid.addWidget(QtWidgets.QLabel('Rows'), 2, 0, alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self.use_rows, 2, 1)
        grid.addWidget(self.execute_button, 3, 0, 1, 2)
        grid.addWidget(self.save_button, 4, 0, 1, 2)
        grid.setRowStretch(5, 1)
        execute_widget.setLayout(grid)

        self.insert_row()
        self.table.resizeColumnsToContents()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.table)
        splitter.addWidget(execute_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([1, 0])

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def show_vertical_popup_menu(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            r = 'row' if len(selected) == 1 else 'rows'
            t = 'the' if len(selected) == 1 else 'each'
            menu = QtWidgets.QMenu(self)
            remove = menu.addAction(self.remove_icon, 'Delete the selected '+r)
            remove.triggered.connect(lambda: self.remove_selected(selected))
            insert_before = menu.addAction(self.insert_before_icon, 'Insert a row before %s selected row' % t)
            insert_before.triggered.connect(lambda: self.insert_selected(selected, 0))
            insert_after = menu.addAction(self.insert_after_icon, 'Insert a row after %s selected row' % t)
            insert_after.triggered.connect(lambda: self.insert_selected(selected, 1))
            clear = menu.addAction(self.clear_icon, 'Remove all of the empty rows')
            clear.triggered.connect(self.remove_empty_rows)
            menu.exec_(QtGui.QCursor.pos())

    def show_horizontal_popup_menu(self):
        selected = self.table.selectionModel().selectedColumns()
        if len(selected) == 1 and selected[0].column() == 0:
            msg = 'Cannot clear the {} column'.format(self.header[selected[0].column()])
            QtWidgets.QMessageBox.information(self, self.windowTitle(), msg)
            return
        if selected:
            menu = QtWidgets.QMenu(self)
            if len(selected) == 1:
                msg = 'Clear the {} column'.format(self.header[selected[0].column()])
            else:
                msg = 'Clear the selected columns'
            clear = menu.addAction(self.clear_icon, msg)
            clear.triggered.connect(lambda: self.clear_column(selected))
            menu.exec_(QtGui.QCursor.pos())

    def remove_selected(self, selected):
        for index in sorted((s.row() for s in selected), reverse=True):
            self.table.removeRow(index)
        if self.table.rowCount() == 0:
            self.insert_row()

    def insert_selected(self, selected, offset):
        for index in sorted(s.row() for s in selected):
            self.insert_row(index + offset)
            offset += 1

    def insert_row(self, index=None):
        """Insert a new row.

        Parameters
        ----------
        index : :obj:`int` or :obj:`None`
            If :obj:`None` then append a row, else the index number (0 based) for
            where to insert the row.
        """
        cb = QtWidgets.QComboBox()
        cb.addItems(['write', 'read', 'query'])
        index = index if index is not None else self.table.rowCount()
        self.table.insertRow(index)
        self.table.setCellWidget(index, 0, cb)
        self.table.setCellWidget(index, 1, QtWidgets.QLineEdit())
        self.table.setCellWidget(index, 2, QtWidgets.QLineEdit())

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            lines = QtWidgets.QApplication.clipboard().text().splitlines()
            self.insert_lines(lines)

    def dragEnterEvent(self, event):
        paths = get_drag_enter_paths(event, '*.txt')
        if paths:
            for path in paths:
                with open(path) as fp:
                    self._dropped_commands.extend(fp.readlines())
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        self.insert_lines(self._dropped_commands)

    def insert_lines(self, lines):
        lines = [line for line in lines if line.strip()]
        index = self.table.rowCount() - 1
        if self.table.cellWidget(index, 1).text() or self.table.cellWidget(index, 0).currentText() == 'read':
            self.insert_row()
            index += 1
        for i, line in enumerate(lines):
            prefix = line.lower()
            if prefix.startswith('write'):
                self.table.cellWidget(index, 0).setCurrentText('write')
                line = line[5:]
            elif prefix.startswith('read'):
                self.table.cellWidget(index, 0).setCurrentText('read')
                line = line[4:]
            elif prefix.startswith('query'):
                self.table.cellWidget(index, 0).setCurrentText('query')
                line = line[5:]
            text = line.split('\t')
            if len(text) == 0:
                msg = ''
                reply = ''
            elif len(text) == 1:
                if self.table.cellWidget(index, 0).currentText() == 'read':
                    msg = ''
                    reply = text[0]
                else:
                    msg = text[0]
                    reply = ''
            elif len(text) == 2:
                if text[0]:
                    msg = text[0]
                    reply = text[1]
                else:
                    if self.table.cellWidget(index, 0).currentText() == 'read':
                        msg = ''
                        reply = text[1]
                    else:
                        msg = text[1]
                        reply = ''
            else:
                if text[0]:
                    msg = text[0]
                    reply = ' '.join(text[1:])
                else:
                    msg = text[1]
                    reply = ' '.join(text[2:])
            self.table.cellWidget(index, 1).setText(msg.strip())
            self.table.cellWidget(index, 2).setText(reply.strip())
            if self.font is None:
                self.font = self.table.cellWidget(index, 2).font()
            if i < len(lines) - 1:
                self.insert_row()
                index += 1

    def execute_start(self):
        self.abort_execution = self.execute_thread.isRunning()
        if not self.execute_thread.isRunning():
            for index in range(self.table.rowCount()):
                self.table.cellWidget(index, 1).setStyleSheet('background-color: white')
                self.table.cellWidget(index, 2).setStyleSheet('background-color: white')
            self.execute_thread.start()
            self.update_execute_button()

    def update_execute_button(self):
        if self.execute_thread.isRunning():
            self.execute_button.setIcon(self.abort_icon)
            self.execute_button.setText('Abort')
            self.execute_button.setToolTip('Abort sending messages to the device')
        else:
            self.execute_button.setIcon(self.execute_icon)
            self.execute_button.setText('Execute')
            self.execute_button.setToolTip('Send the messages to the device')

    def execute_error(self, message):
        QtWidgets.QMessageBox.critical(self, self.windowTitle(), message)
        self.update_execute_button()

    def save(self):
        path, ext = QtWidgets.QFileDialog.getSaveFileName(self, self.windowTitle(), filter='Text files (*.txt)')
        if not path:
            return
        if not path.endswith('.txt'):
            path += '.txt'
        with open(path, 'w') as fp:
            for i in range(self.table.rowCount()):
                method = self.table.cellWidget(i, 0).currentText()
                message = self.table.cellWidget(i, 1).text().strip()
                reply = self.table.cellWidget(i, 2).text().strip()
                fp.writelines('{}\t{}\t{}\n'.format(method, message, reply))

    def clear_column(self, selected):
        for s in selected:
            index = s.column()
            if index == 0:
                msg = 'Cannot clear the {} column'.format(self.header[index])
                QtWidgets.QMessageBox.information(self, self.windowTitle(), msg)
                continue
            for i in range(self.table.rowCount()):
                self.table.cellWidget(i, index).setText('')

    def remove_empty_rows(self):
        for i in range(self.table.rowCount()-1, -1, -1):
            message = self.table.cellWidget(i, 1).text().strip()
            reply = self.table.cellWidget(i, 2).text().strip()
            if not message and not reply:
                self.table.removeRow(i)
        if self.table.rowCount() == 0:
            self.insert_row()


class Execute(QtCore.QThread):

    sigError = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent

    def run(self):
        # determine which rows to execute
        if self.parent.use_rows.text():
            rows = []
            for item in self.parent.use_rows.text().split(','):
                item = item.strip()
                if not item:
                    continue
                if item.isdigit():
                    rows.append(int(item))
                elif '-' in item:
                    item_split = item.split('-')
                    if len(item_split) != 2:
                        self.sigError.emit('Invalid range: ' + item)
                        return
                    try:
                        start, end = map(int, item_split)
                    except ValueError as err:
                        self.sigError.emit('Invalid start-end range: {}'.format(err))
                        return
                    if start > end:
                        self.sigError.emit('Start row {} > End row {}'.format(start, end))
                        return
                    rows.extend([value for value in range(start, end+1)])
                else:
                    self.sigError.emit('Invalid row: ' + item)
                    return
        else:
            rows = [i+1 for i in range(self.parent.table.rowCount())]

        # determine which rows have commands
        commands = []
        for row in rows:
            if row < 1 or row > self.parent.table.rowCount():
                self.sigError.emit('Row {} does not exist'.format(row))
                return
            index = row-1
            method = self.parent.table.cellWidget(index, 0).currentText()
            message = self.parent.table.cellWidget(index, 1).text().strip()
            if not message and method != 'read':
                continue
            commands.append((index, method, message))

        # send the commands
        if not commands:
            self.sigError.emit('There are no messages to send')
            return

        for index, method, message in commands:
            if self.parent.abort_execution:
                break
            widget1 = self.parent.table.cellWidget(index, 1)
            widget2 = self.parent.table.cellWidget(index, 2)
            if self.parent.font is None:
                self.parent.font = widget1.font()
            try:
                widget1.setStyleSheet('background-color: yellow')
                widget2.setStyleSheet('background-color: yellow')
                if method == 'read':
                    if self.parent.query_delay_spinbox.value() > 0:
                        time.sleep(self.parent.query_delay_spinbox.value())
                    reply = self.parent.conn.read()
                elif method == 'write':
                    num_bytes, status = self.parent.conn.write(message)
                    if status != 0:
                        self.sigError.emit('Status Code: {}'.format(status))
                        return
                    reply = '<sent {} bytes>'.format(num_bytes)
                elif method == 'query':
                    reply = self.parent.conn.query(message, self.parent.query_delay_spinbox.value())
                else:
                    self.sigError.emit('Method "{}" not implemented'.format(method))
                    return
                widget1.setStyleSheet('background-color: white')
                widget2.setStyleSheet('background-color: white')
                self.parent.font.setItalic(method == 'write')
                widget2.setFont(self.parent.font)
                widget2.setText(reply.strip())
            except Exception as err:
                self.sigError.emit('{}({})\n\n{}'.format(method, message, err))
                return
