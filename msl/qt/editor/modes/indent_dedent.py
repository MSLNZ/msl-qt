"""
Automatic indent and dedent for the :class:`BaseEditor`.
"""
import logging

from msl.qt import Qt, Signal

from .syntax_highlighter import TextBlockUserData
from ..types import Mode

logger = logging.getLogger(__name__)


class IndentDedentMode(Mode):

    indent_dedent_event = Signal(int)

    def __init__(self, editor, indent=4):
        Mode.__init__(self, editor)

        self._num_spaces = indent
        self._brackets = ('[', '{', '(')

    def add(self):
        self.editor.key_press_event.connect(self._update)
        self.indent_dedent_event.connect(self.editor.inserted_length_event)

    def remove(self):
        self.editor.key_press_event.disconnect(self._update)
        self.indent_dedent_event.disconnect(self.editor.inserted_length_event)

    def additional_newline_handler(self, cursor, left, right):
        """Return whether the method that overrides this function handled the newline"""
        return False

    def get_current_line_indentation(self):
        text = self.editor.textCursor().block().text()
        return len(text) - len(text.lstrip())

    def _update(self, event):
        if not event.isAccepted():
            return

        key = event.key()
        cursor = self.editor.textCursor()

        if key == Qt.Key_Tab or key == Qt.Key_Backtab:
            # this handles if a Tab or Backtab key is pressed if either
            # - no lines are selected (applies the key press to the current line only)
            # - multiple lines are selected (applies the key event to all selected lines)

            dedent = key == Qt.Key_Backtab

            start_position = min(cursor.anchor(), cursor.position())
            end_position = max(cursor.anchor(), cursor.position())

            cursor.setPosition(start_position, cursor.MoveAnchor)
            start_block = cursor.block().blockNumber()

            cursor.setPosition(end_position, cursor.MoveAnchor)
            end_block = cursor.block().blockNumber()
            if end_block == start_block or cursor.block().text().strip():
                end_block += 1

            iblock = 0
            nblocks = end_block - start_block
            cursor.setPosition(start_position, cursor.MoveAnchor)
            while iblock < nblocks:
                cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
                if dedent:
                    iline = 0
                    while iline < self._num_spaces:
                        cursor.movePosition(cursor.Right, mode=cursor.KeepAnchor)
                        text = cursor.selectedText()
                        if text.startswith('\u2029'):
                            # then this is an empty line (an empty block)
                            cursor.clearSelection()
                            iblock += 1
                        elif text != ' ':
                            break
                        else:
                            cursor.removeSelectedText()
                            cursor.clearSelection()
                            iline += 1
                else:
                    cursor.insertText(' ' * self._num_spaces)
                cursor.movePosition(cursor.NextBlock, cursor.MoveAnchor)
                iblock += 1

            if nblocks > 1:
                # set the cursor's selection to span all of the selected lines
                cursor.setPosition(start_position, cursor.MoveAnchor)
                cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
                while cursor.block().blockNumber() < end_block:
                    cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)
                    if not cursor.block().next().isValid():
                        # reached the end of the document
                        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                        break
            elif dedent:
                cursor.setPosition(max(start_position - self._num_spaces, 0), cursor.MoveAnchor)
            else:
                cursor.setPosition(start_position + self._num_spaces, cursor.MoveAnchor)

            self.editor.setTextCursor(cursor)
            event.ignore()

        elif key == Qt.Key_Backspace:
            if self.editor.peek_left(self._num_spaces) == ' ' * self._num_spaces:
                self.indent_dedent_event.emit(-self._num_spaces)
                cursor.movePosition(cursor.Left, mode=cursor.KeepAnchor, n=self._num_spaces)
                cursor.removeSelectedText()
                self.editor.setTextCursor(cursor)
                event.ignore()

        elif key == Qt.Key_Delete:
            if self.editor.peek_right(self._num_spaces) == ' ' * self._num_spaces:
                self.indent_dedent_event.emit(-self._num_spaces)
                cursor.movePosition(cursor.Right, mode=cursor.KeepAnchor, n=self._num_spaces)
                cursor.removeSelectedText()
                self.editor.setTextCursor(cursor)
                event.ignore()

        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            text = cursor.block().text()
            indent = self.get_current_line_indentation()

            column = cursor.positionInBlock()
            left = text[:column]
            right = text[column:]

            if not self.additional_newline_handler(cursor, left, right):
                left_rstrip = left.rstrip()
                text_not_to_right = len(right.strip()) == 1
                text = '\u2029' + ' ' * indent
                shift = 0
                for bracket in self._brackets:
                    if left_rstrip.endswith(bracket):
                        text += ' ' * self._num_spaces
                        shift += indent
                        if text_not_to_right:
                            text += '\u2029' + ' ' * indent
                            shift += 1
                        break

                cursor.insertText(text)
                cursor.setPosition(cursor.position() - shift)
                self.indent_dedent_event.emit(len(text))

            # must define block.userData() for each '\u2029' that was inserted
            # this is required for syntax highlighting
            block = cursor.block()
            while True:
                if block.userData():
                    break
                block.setUserData(TextBlockUserData(None))
                block = block.previous()

            self.editor.setTextCursor(cursor)
            event.ignore()

            self.editor.ensureCursorVisible()
