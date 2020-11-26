"""
Finds the first none-blank character when the Home key is pressed. If
the cursor is already at the first non-blank character then moves the cursor
to the actual home position in the block.
"""
import logging

from msl.qt import Qt

from ..types import Mode

logger = logging.getLogger(__name__)


class SmartHomeMode(Mode):

    def __init__(self, editor):
        Mode.__init__(self, editor)

        self._original_position = 0
        self._move_to_actual_home = False

    def update_parameters(self):
        self._move_to_actual_home = False
        self._original_position = self.editor.textCursor().position()

    def add(self):
        self.editor.key_press_event.connect(self.find_home)
        self.editor.cursorPositionChanged.connect(self.update_parameters)

    def remove(self):
        self.editor.key_press_event.disconnect(self.find_home)
        self.editor.cursorPositionChanged.connect(self.update_parameters)

    def find_home(self, event):
        if not event.isAccepted():
            return

        if event.key() != Qt.Key_Home:
            return

        if event.modifiers() == self.editor.ControlModifier:
            return

        cursor = self.editor.textCursor()

        text = cursor.block().text()
        if not text.strip() or text[:1].strip():
            return

        if not cursor.atBlockStart():
            cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
            if not cursor.selectedText().strip():
                return

        cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
        if not self._move_to_actual_home:
            cursor.movePosition(cursor.WordRight, cursor.MoveAnchor)
        home_position = cursor.position()

        if event.modifiers() == Qt.ShiftModifier:
            cursor.setPosition(self._original_position, cursor.MoveAnchor)
            cursor.setPosition(home_position, cursor.KeepAnchor)

        temp1 = self._original_position
        temp2 = not self._move_to_actual_home

        self.editor.setTextCursor(cursor)

        self._original_position = temp1
        self._move_to_actual_home = temp2

        event.ignore()
