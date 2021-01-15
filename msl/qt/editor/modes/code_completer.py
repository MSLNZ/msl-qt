"""
Performs code completion for the :class:`BaseEditor`.
"""
import logging

from ... import (
    QtWidgets,
    QtGui,
    Qt,
    Signal,
    utils,
)
from ..types import Mode

logger = logging.getLogger(__name__)


class CodeCompleterMode(Mode):

    popup_event = Signal(bool)
    """
    :class:`~msl.qt._qt.Signal`: Signal that is emitted when the popup is shown 
    (emits :obj:`True`) or hidden (emits :obj:`False`).
    """

    def __init__(self, editor, *, min_prefix_length=1, case_sensitive=False, completion_mode='Popup'):
        """Performs code completion for the :class:`BaseEditor`.

        Parameters
        ----------
        editor : :class:`BaseEditor`
            The editor.
        min_prefix_length : :class:`int`, optional
            The minimum length that the prefix must be before the completion
            popup is displayed. To disable the popup based on the length of
            the prefix specify a value < 1.
        case_sensitive : :class:`bool`, optional
            Whether matching the completions is case sensitive.
        completion_mode : :class:`str`, optional
            How the completions are provided to the user. One of ``'Popup'``,
            ``'Inline'`` or ``'UnfilteredPopup'``.
        """
        super(CodeCompleterMode, self).__init__(editor)

        self._min_prefix_length = min_prefix_length

        self._trigger_key = Qt.Key_Space  # the CTRL+SPACE sequence triggers the completion popup
        self._trigger_text = '.'  # typing a '.' triggers the completion popup

        self._is_trigger_key = False  # is the key sequence CTRL+self._trigger_key ?
        self._is_trigger_text = False  # is the key sequence equal to self._trigger_text ?
        self._is_alnum_uscore = False  # is the key event alphanumeric or an underscore ?

        self._min_popup_width = int(utils.screen_geometry().width() * 0.3)

        self._model = QtGui.QStandardItemModel()

        self._completion_mode_map = {
            'Popup': QtWidgets.QCompleter.PopupCompletion,
            'Inline': QtWidgets.QCompleter.InlineCompletion,
            'UnfilteredPopup': QtWidgets.QCompleter.UnfilteredPopupCompletion,
            'Unfiltered': QtWidgets.QCompleter.UnfilteredPopupCompletion,
        }

        self._case_sensitive = Qt.CaseSensitive if case_sensitive else Qt.CaseInsensitive

        self._completer = QtWidgets.QCompleter()
        self._completer.setWidget(self.editor)
        self._completer.setModel(self._model)
        self._completer.setCompletionMode(self._completion_mode_map[completion_mode])
        self._completer.setCaseSensitivity(self._case_sensitive)
        self._completer.setWrapAround(True)

        popup = QtWidgets.QTableView()
        popup.setWordWrap(False)
        popup.setShowGrid(False)
        popup.setSortingEnabled(False)
        popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        popup.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        popup.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        popup.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #popup.horizontalHeader().setStretchLastSection(True)
        #popup.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        popup.horizontalHeader().hide()
        popup.verticalHeader().hide()
        popup.setStyleSheet('QAbstractScrollArea { background-color: #EAF2F8; outline: none }')
        self._completer.setPopup(popup)

    @property
    def case_sensitive(self):
        """:class:`bool`: Whether matching the completions is case sensitive."""
        return bool(self._completer.caseSensitivity())

    @case_sensitive.setter
    def case_sensitive(self, value):
        sensitive = Qt.CaseSensitive if value else Qt.CaseInsensitive
        self._completer.setCaseSensitivity(sensitive)

    @property
    def completer(self):
        """:class:`QtWidgets.QCompleter`: The completer that is used for the completions."""
        return self._completer

    @property
    def completion_mode(self):
        """:class:`str`: A `QCompleter.CompletionMode <http://doc.qt.io/qt-5/qcompleter.html#CompletionMode-enum>`_
        enum prefix that specifies how completions are provided to the user.
        One of ``'Popup'``, ``'Inline'`` or ``'UnfilteredPopup'``."""
        mode = self._completer.completionMode()
        for name, value in self._completion_mode_map.items():
            if value == mode:
                return name
        assert False, 'Unknown completion mode value {}'.format(mode)

    @completion_mode.setter
    def completion_mode(self, value):
        self._completer.setCompletionMode(self._completion_mode_map[value])

    @property
    def model(self):
        """:class:`QtCore.QAbstractItemModel`: The model that is used for the :obj:`.completer`."""
        return self._model

    @property
    def min_prefix_length(self):
        """:class:`int`: The minimum length that the prefix must be before the completion
        popup is displayed. To disable the popup based on the length of the prefix specify
        a value < 1."""
        return self._min_prefix_length

    @min_prefix_length.setter
    def min_prefix_length(self, value):
        self._min_prefix_length = int(value)

    @property
    def trigger_key(self):
        """:class:`str`: The key that, when pressed while the ``CTRL`` key is also
        pressed, will trigger the completion popup to be displayed. The value must
        be a `QtCore.Qt.Key_? <http://doc.qt.io/qt-5/qt.html#Key-enum>`_ value.
        Default value is ``'Space'``, i.e., ``QtCore.Qt.Key_Space``."""
        return self._trigger_key

    @trigger_key.setter
    def trigger_key(self, value):
        self._trigger_key = getattr(Qt, 'Key_'+str(value))

    @property
    def trigger_text(self):
        """:class:`str`: The text that when typed sequentially will trigger the
        completion popup to be displayed. Default value is ``'.'``, i.e., the
        dot character that is used by Python to access an attribute of an object.
        For C++ this would be the ``'->'`` sequence."""
        return self._trigger_key

    @trigger_text.setter
    def trigger_text(self, value):
        if not value:
            raise ValueError('The trigger text cannot be an empty sequence of characters.')
        self.trigger_text = str(value)

    def add(self):
        """Overrides :meth:`EditorType.add`."""
        self._completer.activated.connect(self._insert_completion)
        self.editor.key_press_event.connect(self._key_press_event)
        self.popup_event.connect(self.editor.code_completer_popup_event)

    def remove(self):
        """Overrides :meth:`EditorType.remove`."""
        self._completer.activated.disconnect(self._insert_completion)
        self.editor.key_press_event.disconnect(self._key_press_event)
        self.popup_event.disconnect(self.editor.code_completer_popup_event)

    def update_model(self, event):
        """Update the :obj:`.model` with the completions.

        .. attention::
           You **MUST** override this method and update the data in the
           :obj:`.model` otherwise the completion popup will never be
           displayed.
        """
        pass

    def _key_press_event(self, event):
        """The slot for the :math:`BaseEditor.keyPressEvent`."""
        self._is_trigger_key = self._is_trigger_key_event(event)
        self._is_trigger_text = self._is_trigger_text_event(event)
        self._is_alnum_uscore = self.editor.is_alphanumeric_or_underscore(event.text())

        if self._completer.popup().isVisible():
            # a key was pressed while the popup is visible
            key = event.key()
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                # performs the following:
                # - inserts the highlighted completion where the cursor is (overwriting the prefix)
                # - shifts any text that is to the right of the cursor (on the same line) over
                # - ignores the event so that the BaseEditor does not insert a Unicode U+2029 paragraph separator
                self._hide_popup()
                event.ignore()
            elif key == Qt.Key_Backspace:
                # performs the following:
                # - updates the prefix by removing the last character
                # - keeps the popup displayed if the prefix > self._min_prefix_length
                if len(self._completer.completionPrefix()) > self._min_prefix_length:
                    self._show_popup(event)
                else:
                    self._hide_popup()
            elif key == Qt.Key_Tab:
                # performs the following:
                # - inserts the highlighted completion where the cursor
                # - overwrites the prefix and the suffix (the entire word)
                # - ignores the event so that the BaseEditor does not insert a Tab
                self._overwrite_word()
                self._hide_popup()
                event.ignore()
            elif key == Qt.Key_Space:
                # starting a new word
                self._hide_popup()
            elif event.modifiers() == Qt.ShiftModifier:
                # assume that the user is going to type an upper-case letter
                self._show_popup(event)
            elif self._is_trigger_text:
                # then accessing an attribute of the previous word
                # update the model and then show the popup
                self._update_model(event)
                if self._min_prefix_length > 1:
                    self._hide_popup()
            elif self._is_alnum_uscore:
                # show the popup (using the newly-pressed text in the prefix)
                self._show_popup(event)
            else:
                self._hide_popup()
        elif self._is_alnum_uscore or self._is_trigger_key or self._is_trigger_text:
            # a valid key was pressed while the popup is not visible
            self._update_model(event)

    def _update_model(self, event):
        try:
            self.update_model(event)
        except Exception as e:
            logger.error(e)
            self._hide_popup()
        else:
            self._show_popup(event)

    def _hide_popup(self):
        self._completer.popup().hide()
        self.popup_event.emit(False)

    def _show_popup(self, event):
        """Show the completion popup."""

        # find the prefix
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.WordLeft, cursor.KeepAnchor)
        prefix = cursor.selectedText()
        rect = self.editor.cursorRect(cursor)

        # the keyPressEvent has not been accepted yet so we
        # need to modify the prefix with the current keyPressEvent
        if self._is_trigger_text:
            # we should accept all matches since we are accessing an attribute of an object
            prefix = ''
        elif event.key() == Qt.Key_Backspace:
            # ignore the last character (which will be removed from the Key_Backspace event)
            prefix = prefix[:-1]
        elif self._is_alnum_uscore:
            # append the alphanumeric or underscore value that was just typed
            prefix += event.text()
        elif self._is_trigger_key and (not prefix.strip() or prefix == self._trigger_text):
            rect = self.editor.cursorRect(self.editor.textCursor())
            prefix = ''

        if self._is_trigger_key or self._is_trigger_text or len(prefix) >= self._min_prefix_length:

            font = self.editor.font()
            font_metrics = QtGui.QFontMetrics(font)

            popup = self._completer.popup()
            popup.setFont(font)
            popup.setMinimumHeight(font_metrics.height() * 6)

            self._completer.setCompletionPrefix(prefix)

            if self._completer.completionCount() == 0:
                self._hide_popup()
            elif self._completer.completionCount() == 1 and self._completer.currentCompletion() == prefix:
                self._hide_popup()
            else:

                # resize the QTableView
                popup.resizeRowsToContents()
                col_width = popup.sizeHintForColumn(1)
                total_width = max(self._min_popup_width, font_metrics.averageCharWidth()*30)
                popup.setColumnWidth(0, total_width - col_width - popup.verticalScrollBar().sizeHint().width())
                popup.setColumnWidth(1, col_width)

                # move the popup to be under the current line in the BaseEditor
                offset = self.editor.viewportMargins().left()
                offset -= popup.verticalScrollBar().sizeHint().width() + 8  # shift by the width of the icon

                cursor = self.editor.textCursor()
                if self._is_trigger_text:
                    rect = self.editor.cursorRect(cursor)
                    offset += font_metrics.width(event.text())
                elif self._is_trigger_key:
                    if self.editor.peek_left(len(self._trigger_text)) == self._trigger_text:
                        cursor.movePosition(cursor.StartOfWord)
                        rect = self.editor.cursorRect(cursor)

                rect.setWidth(total_width)
                rect.translate(offset, 0)
                self._completer.complete(rect)

                # select the first item in the popup
                self._completer.setCurrentRow(0)
                self._completer.popup().setCurrentIndex(self._completer.currentIndex())
                self.popup_event.emit(True)

    def _is_trigger_key_event(self, event):
        """bool: checks whether CTRL+self._trigger_key was entered."""
        return event.modifiers() == self.editor.ControlModifier and event.key() == self._trigger_key

    def _is_trigger_text_event(self, event):
        """bool: checks whether event.text() == self._trigger_text"""
        text = event.text()
        if not text:
            return False

        if len(self._trigger_text) == 1 and self._trigger_text == text:
            return True

        # subtract 1 since the current keyPressEvent has not yet been inserted in to the BaseEditor
        peek = self.editor.peek_left(len(self._trigger_text)-1)
        if not peek:
            return False

        return self._trigger_text == peek + text

    def _insert_completion(self, completion):
        """insert the completion in the BaseEditor."""
        cursor = self.editor.textCursor()
        cursor.insertText(completion[len(self._completer.completionPrefix()):])
        self.editor.setTextCursor(cursor)

    def _overwrite_word(self):
        """replace the word (the characters before and after the cursor) with the selected completion"""

        # remove the word under the cursor
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.Left, cursor.KeepAnchor, n=len(self._completer.completionPrefix()))
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        cursor.removeSelectedText()

        # get the selected word from the popup
        row = self._completer.popup().selectionModel().currentIndex().row()
        word = self._completer.completionModel().index(row, 0).data()

        # the suffix will automatically be inserted from the Key_Tab event of the QCompleter
        # so we only need to insert the prefix
        # cannot use self._completer.completionPrefix() because word might be case-sensitive
        cursor.insertText(word[:len(self._completer.completionPrefix())])
