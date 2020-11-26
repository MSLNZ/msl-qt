"""
Highlights matching brackets and parenthesis.
"""
import logging

from msl.qt import QtGui, QtWidgets

from ..types import Mode

logger = logging.getLogger(__name__)


class BracketMatcherMode(Mode):

    OPENING_BRACKETS = {'(': ')', '[': ']', '{': '}'}
    CLOSING_BRACKETS = {')': '(', ']': '[', '}': '{'}

    def __init__(self, editor):
        Mode.__init__(self, editor)

        self._count = 0
        self._old_format = None
        self._positions = [-1, -1]
        self._selections = [
            QtWidgets.QTextEdit.ExtraSelection(),
            QtWidgets.QTextEdit.ExtraSelection()
        ]

    def add(self):
        self.editor.new_color_scheme_event.connect(self._update_color_scheme)
        self.editor.cursorPositionChanged.connect(self._check_highlight)

    def remove(self):
        self.editor.new_color_scheme_event.disconnect(self._update_color_scheme)
        self.editor.cursorPositionChanged.disconnect(self._check_highlight)

    def _update_color_scheme(self, scheme):
        self._old_format = None

        self._selections = [
            QtWidgets.QTextEdit.ExtraSelection(),
            QtWidgets.QTextEdit.ExtraSelection()
        ]

        # underline, stippled_underline, squiggly_underline, foreground
        for selection in self._selections:
            if scheme.brackets_options == 'underline':
                selection.format.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
            elif scheme.brackets_options == 'stippled_underline':
                selection.format.setUnderlineStyle(QtGui.QTextCharFormat.DotLine)
            elif scheme.brackets_options == 'squiggly_underline':
                selection.format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
            elif scheme.brackets_options == 'foreground':
                selection.format.setForeground(scheme.brackets_foreground)
            else:
                selection.format.setBackground(scheme.brackets_background)

    def _check_highlight(self):
        if self._old_format is not None:
            self._unhighlight()

        self._count = 0
        cursor = self.editor.textCursor()
        left = self.editor.peek_left()
        right = self.editor.peek_right()

        try:
            matching = self.OPENING_BRACKETS[left]
            self._positions[0] = cursor.position() - 1
            self._find_closing_bracket(cursor, left, matching)
            return
        except KeyError:
            pass

        try:
            matching = self.OPENING_BRACKETS[right]
            self._positions[0] = cursor.position()
            cursor.movePosition(cursor.Right, mode=cursor.MoveAnchor)
            self._find_closing_bracket(cursor, right, matching)
            return
        except KeyError:
            pass

        try:
            matching = self.CLOSING_BRACKETS[left]
            self._positions[1] = cursor.position() - 1
            cursor.movePosition(cursor.Left, mode=cursor.MoveAnchor)
            self._find_opening_bracket(cursor, left, matching)
            return
        except KeyError:
            pass

        try:
            matching = self.CLOSING_BRACKETS[right]
            self._positions[1] = cursor.position()
            self._find_opening_bracket(cursor, right, matching)
            return
        except KeyError:
            pass

    def _find_closing_bracket(self, cursor, bracket, matching):
        while not cursor.atEnd():
            position = self._find_matching_bracket(cursor, bracket, matching, cursor.Right)
            if position:
                self._positions[1] = position - 1
                self._rehighlight()
                return

    def _find_opening_bracket(self, cursor, bracket, matching):
        while not cursor.atStart():
            position = self._find_matching_bracket(cursor, bracket, matching, cursor.Left)
            if position:
                self._positions[0] = position
                self._rehighlight()
                return

    def _find_matching_bracket(self, cursor, bracket, matching, direction):
        cursor.movePosition(direction, mode=cursor.KeepAnchor)
        text = cursor.selectedText()
        if text == matching:
            self._count -= 1
            if self._count < 0:
                return cursor.position()
        elif text == bracket:
            self._count += 1
        cursor.clearSelection()

    def _unhighlight(self):
        cursor = self.editor.textCursor()
        for i in range(2):
            selection = self._selections[i]
            selection.cursor = cursor
            selection.cursor.setPosition(self._positions[i], mode=cursor.MoveAnchor)
            selection.cursor.movePosition(cursor.Right, mode=cursor.KeepAnchor)
            selection.cursor.setCharFormat(self._old_format)
        self._old_format = None

    def _rehighlight(self):
        cursor = self.editor.textCursor()
        selections = self.editor.extraSelections()
        for i in range(2):
            selection = self._selections[i]
            selection.cursor = cursor
            selection.cursor.setPosition(self._positions[i], mode=cursor.MoveAnchor)
            selection.cursor.movePosition(cursor.Right, mode=cursor.KeepAnchor)
            self._old_format = selection.cursor.charFormat()
            selection.cursor.setCharFormat(self._old_format)
            selections.append(selection)
        self.editor.setExtraSelections(selections)
