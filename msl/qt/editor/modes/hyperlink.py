"""
Underlines the word under the cursor and provides a hyperlink action on a mouse click.
"""
import logging

from ... import (
    QtGui,
    QtWidgets,
    Qt,
    Signal,
)
from ..types import Mode

logger = logging.getLogger(__name__)


class HyperlinkMode(Mode):

    hyperlink_external_event = Signal(str, int)  # module path, cursor position

    def __init__(self, editor, color='#0681E0'):
        super(HyperlinkMode, self).__init__(editor)

        self._word = ''
        self._cursor_start = -1
        self._cursor_end = -1
        self._format = None
        self._foreground = QtGui.QColor(color)

    def add(self):
        self.editor.mouse_move_event.connect(self._mouse_moved)
        self.editor.key_release_event.connect(self._remove_hyperlink)
        self.editor.mouse_release_event.connect(self._mouse_release)
        self.hyperlink_external_event.connect(self.editor.hyperlink_external_event)

    def remove(self):
        self.editor.mouse_move_event.disconnect(self._mouse_moved)
        self.editor.key_release_event.disconnect(self._remove_hyperlink)
        self.editor.mouse_release_event.disconnect(self._mouse_release)
        self.hyperlink_external_event.disconnect(self.editor.hyperlink_external_event)

    def draw_hyperlink_from_scopes(self, scopes):
        """
        Override this method to make the final decision whether to draw the hyperlink.

        Only called if syntax highlighting is used.

        This method should check the syntax highlight scopes to determine if
        the hyperlink should be drawn. Return True if the hyperlink should
        be drawn.
        """
        return True

    def hyperlink(self, cursor):
        """
        Override this method to handle the hyperlink event.

        cursor -> the cursor located at the start of the word and with the word selected
        """
        pass

    def popup(self, cursor):
        """
        Override this method to handle the what the popup should show when the hyperlink is drawn.

        cursor -> the cursor located at the start of the word and with the word selected
        """
        pass

    def _mouse_moved(self, event, cursor):
        if self._word:
            self._remove_hyperlink()

        current_word = cursor.selectedText()
        if event.modifiers() == self.editor.ControlModifier and \
                self._word != current_word and \
                self.editor.is_alphanumeric_or_underscore(current_word) and \
                self._word_not_in_comment(cursor):
            self._draw_hyperlink(cursor)

    def _mouse_release(self, event):
        if self._cursor_start == -1:
            return

        if event.button() == Qt.LeftButton:
            cursor = self.editor.textCursor()
            cursor.setPosition(self._cursor_end, mode=cursor.MoveAnchor)
            cursor.setPosition(self._cursor_start, mode=cursor.KeepAnchor)
            self.hyperlink(cursor)

    def _word_not_in_comment(self, cursor):
        user_data = cursor.block().userData()
        if user_data is None:
            return True
        word = cursor.selectedText()
        index = cursor.positionInBlock() - len(word) + 1
        i = 0
        for token in user_data.tokens:
            i += len(token['value'])
            if word == token['value'] or i >= index:
                return self.draw_hyperlink_from_scopes(token['scopes'])
        return True

    def _draw_hyperlink(self, cursor):
        fmt = cursor.charFormat()

        self._cursor_start = cursor.selectionStart()
        self._cursor_end = cursor.selectionEnd()
        self._word = cursor.selectedText()
        self._format = QtGui.QTextCharFormat(fmt)

        fmt.setForeground(self._foreground)
        fmt.setUnderlineStyle(fmt.SingleUnderline)
        cursor.setCharFormat(fmt)
        QtWidgets.QApplication.setOverrideCursor(Qt.PointingHandCursor)
        self.popup(cursor)

    def _remove_hyperlink(self, event=None):
        if self._format and (event is None or event.key() == Qt.Key_Control):

            cursor = self.editor.textCursor()
            cursor.setPosition(self._cursor_start)
            cursor.setPosition(self._cursor_end, mode=cursor.KeepAnchor)
            cursor.setCharFormat(self._format)

            self._word = ''
            self._cursor_start = -1
            self._cursor_end = -1
            self._format = None
            QtWidgets.QApplication.restoreOverrideCursor()
