"""
Performs automatic completion for the :class:`BaseEditor`.
"""
from msl.qt import Qt, Signal

from ..types import Mode


class AutoCompleteMode(Mode):

    inserted_text_event = Signal(int)

    def __init__(self, editor, **kwargs):
        """

        Parameters
        ----------
        editor
        kwargs : Additional auto-complete key-value pairs,
            i.e. for a C/C++ multi-line comment {'/*': '*/'}
        """
        Mode.__init__(self, editor)

        self._maps = {
            '"': '"',
            "'": "'",
            '(': ')',
            '{': '}',
            '[': ']',
        }

        self._maps.update(kwargs)

    def add(self):
        self.editor.key_press_event.connect(self.complete)
        self.inserted_text_event.connect(self.editor.inserted_length_event)

    def remove(self):
        self.editor.key_press_event.disconnect(self.complete)
        self.inserted_text_event.disconnect(self.editor.inserted_length_event)

    def complete(self, event):
        if not event.isAccepted():
            return

        if self.editor.is_navigation(event):
            return

        text = event.text()
        cursor = self.editor.textCursor()

        # check if the key that was pressed is already the next character
        right = self.editor.peek_right().strip()
        if right and right == text:
            # then ignore the key press and shift the cursor over by 1
            cursor.setPosition(cursor.position() + 1)
            self.editor.setTextCursor(cursor)
            event.ignore()
            return

        # check whether auto-complete characters are being deleted
        if right and event.key() == Qt.Key_Backspace:

            # check if multiple matching characters are to the left of the cursor
            left = self.editor.peek_left().strip()
            for key in self._maps:
                nkey = len(key)
                if nkey > 1 and self.editor.peek_left(nkey) == key:
                    left = key
                    cursor.setPosition(cursor.position() - nkey + 1)
                    break

            # check if multiple matching characters are to the right of the cursor
            n = 1
            for key, value in self._maps.items():
                nkey = len(key)
                if nkey > 1 and self.editor.peek_right(nkey) == value:
                    n = nkey
                    right = value
                    break

            if self._maps.get(left) == right:
                cursor.movePosition(cursor.Right, mode=cursor.KeepAnchor, n=2*n-1)
                cursor.removeSelectedText()

            return

        # check if multiple matching characters are to the left of the cursor
        # NOTE: the key press event has not been accepted yet
        matching = None
        for key in self._maps:
            n = len(key) - 1
            if n and self.editor.peek_left(n) + text == key:
                matching = self._maps[key]
                break

        if matching is None:
            matching = self._maps.get(text)

        # check whether to insert the matching characters
        if matching:
            position = cursor.position()
            cursor.insertText(text + matching)
            cursor.setPosition(position + 1)
            self.inserted_text_event.emit(len(matching))
            self.editor.setTextCursor(cursor)
            event.ignore()
