"""
A :class:`QtWidgets.QDialog` to prompt the user to enter comments.
"""
import json
import os
from datetime import datetime

from .. import Button
from .. import Qt
from .. import QtWidgets
from .. import convert
from .. import prompt
from .. import utils
from ..constants import HOME_DIR


class Comments(QtWidgets.QDialog):

    def __init__(self, json_path, title, even_row_color, odd_row_color):
        """A :class:`QtWidgets.QDialog` to prompt the user to enter comments.

        Do not instantiate directly. Use :func:`msl.qt.prompt.comments` instead.
        """
        super(Comments, self).__init__(
            None, Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinMaxButtonsHint)

        self.setWindowTitle(title)

        self.path = json_path if json_path else os.path.join(HOME_DIR, 'msl-qt-comments.json')

        self.comments = []
        self.even_row_color = convert.to_qcolor(even_row_color)
        self.odd_row_color = convert.to_qcolor(odd_row_color)

        self._load_json()

        self.comment_textedit = QtWidgets.QPlainTextEdit(self)
        height = self.comment_textedit.fontMetrics().lineSpacing()
        self.comment_textedit.setFixedHeight(5 * height)  # display 5 lines

        self.ok_button = Button(
            text='OK',
            left_click=self._prepend_and_close,
            tooltip='Select the comment and exit',
            parent=self,
        )
        self.ok_button.add_menu_item(
            text='Clear history',
            icon=QtWidgets.QStyle.StandardPixmap.SP_DialogResetButton,
            triggered=self._clear_history,
            tooltip='Delete all comments that are in the history'
        )

        #
        # the filter field
        #
        self.filter_edit = QtWidgets.QLineEdit()
        self.filter_edit.setToolTip('Search filter for the history')
        self.filter_edit.returnPressed.connect(self._apply_filter)  # noqa: returnPressed.connect

        filter_button = Button(
            icon=QtWidgets.QStyle.StandardPixmap.SP_FileDialogContentsView,
            tooltip='Apply filter',
            left_click=self._apply_filter
        )
        clear_button = Button(
            icon=QtWidgets.QStyle.StandardPixmap.SP_LineEditClearButton,
            tooltip='Clear filter',
            left_click=self._clear_filter
        )

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(filter_button)
        filter_layout.addWidget(self.filter_edit)
        filter_layout.addWidget(clear_button)
        filter_layout.setSpacing(1)

        #
        # history table
        #
        self.table = QtWidgets.QTableWidget()
        table_header = ['Timestamp', 'Comment']
        self.table.setColumnCount(len(table_header))
        self.table.setHorizontalHeaderLabels(table_header)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().sectionClicked.connect(self._update_table_row_colors_and_resize)  # noqa: sectionClicked.connect
        self.table.cellDoubleClicked.connect(self._table_double_click)  # noqa: cellDoubleClicked.connect
        self.table.keyPressEvent = self._table_key_press
        for item in self.comments:
            self._append_to_history_table(item['timestamp'], item['comment'])
        self._update_table_row_colors_and_resize()

        #
        # main layout
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Enter a new comment or select one from the history below'))
        layout.addWidget(self.comment_textedit)
        layout.addWidget(self.ok_button)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        geo = utils.screen_geometry(widget=self)
        self.resize(int(geo.width()*0.4), int(geo.height()*0.6))

    def _append_to_history_table(self, timestamp, comment):
        index = self.table.rowCount()
        self.table.insertRow(index)
        self.table.setItem(index, 0, QtWidgets.QTableWidgetItem(timestamp))
        self.table.setItem(index, 1, QtWidgets.QTableWidgetItem(comment))

    def _apply_filter(self):
        filter_text = self.filter_edit.text().lower()
        if not filter_text and self.table.rowCount() == len(self.comments):
            # all rows are already visible
            return

        self.table.setRowCount(0)
        for item in self.comments:
            if not filter_text or filter_text in item['timestamp'] or filter_text in item['comment'].lower():
                self._append_to_history_table(item['timestamp'], item['comment'])
        self._update_table_row_colors_and_resize()

    def _clear_filter(self):
        # clear the filter text, only if there is text written in the filter
        if self.filter_edit.text():
            self.filter_edit.setText('')
            self._apply_filter()

    def _clear_history(self):
        if not self.comments or not prompt.yes_no('Clear the entire history?', default=False):
            return
        self.table.setRowCount(0)
        self.comments = []
        self._save_json()

    def _load_json(self):
        if not os.path.isfile(self.path):
            # assume that this is a new file that will be created
            return

        with open(self.path, mode='rb') as fp:
            try:
                self.comments = json.load(fp)
            except Exception as e:
                prompt.warning(f'Error loading JSON file:\n{self.path}\n\n{e}')

    def _prepend_and_close(self):
        self.close()

        if not self.text():
            # no new comments were entered so there is nothing to save to the history file
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.comments.insert(0, {'timestamp': timestamp, 'comment': self.text()})
        self._save_json()

    def _save_json(self):
        # ensure that the intermediate directories exist
        root = os.path.dirname(self.path)
        if root and not os.path.isdir(root):
            os.makedirs(root)

        with open(self.path, mode='wt') as fp:
            json.dump(self.comments, fp, indent=2, ensure_ascii=False)

    def _table_double_click(self, row, column):  # noqa: parameter 'column' is not used
        self.comment_textedit.setPlainText(self.table.item(row, 1).text())

    def _table_key_press(self, event):
        # CTRL+A pressed
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self.table.selectAll()
            return

        if event.key() != Qt.Key.Key_Delete:
            return

        # sort the selected rows in reverse order for the self.table.removeRow method below
        selected = sorted([s.row() for s in self.table.selectionModel().selectedRows()], reverse=True)

        if len(selected) == self.table.rowCount():
            self._clear_history()
            return

        msg = 'this item' if len(selected) == 1 else f'these {len(selected)} items'
        if not prompt.yes_no(f'Remove {msg} from the history?', default=False):
            return

        for index in selected:
            self.table.removeRow(index)
            del self.comments[index]

        self._save_json()

    def _update_table_row_colors_and_resize(self):
        for row in range(self.table.rowCount()):
            color = self.even_row_color if row % 2 else self.odd_row_color
            try:
                self.table.item(row, 0).setBackground(color)
                self.table.item(row, 1).setBackground(color)
            except AttributeError:
                # non-reproducible bug
                # sometimes the item in the row has a NoneTye
                # possibly do to signaling issues?
                pass
        self.table.verticalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def text(self):
        """str: The text in the comment editor."""
        return self.comment_textedit.toPlainText().strip()
