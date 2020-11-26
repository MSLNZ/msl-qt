"""
Performs syntax checking.
"""
import logging

from msl.qt import QtGui, QtWidgets, Qt, Signal

from ..types import Mode
from ..profiler import Profile

logger = logging.getLogger(__name__)


class LinterMode(Mode):

    indent_dedent_event = Signal(int)

    def __init__(self, editor):
        Mode.__init__(self, editor)

        self._linter_info = list()  # list of (cursor_start_position, cursor_end_position, message)
        self._error_color = QtGui.QColor(Qt.red)
        self._warning_color = QtGui.QColor(Qt.darkGray)

    @property
    def error_color(self):
        return self._error_color

    @error_color.setter
    def error_color(self, color):
        self._error_color = QtGui.QColor(color)

    @property
    def warning_color(self):
        return self._warning_color

    @warning_color.setter
    def warning_color(self, color):
        self._warning_color = QtGui.QColor(color)

    def add(self):
        self.editor.new_text_event.connect(self._lint)
        self.editor.new_color_scheme_event.connect(self._update_color)
        self.editor.key_release_event.connect(self._check_lint)
        self.editor.key_press_event.connect(self._remove_previous)
        self.editor.mouse_move_event.connect(self._show_tooltip)
        self.editor.paste_event.connect(self._paste_event)
        self.indent_dedent_event.connect(self.editor.inserted_length_event)

    def remove(self):
        self.editor.new_text_event.disconnect(self._lint)
        self.editor.new_color_scheme_event.disconnect(self._update_color)
        self.editor.key_release_event.disconnect(self._check_lint)
        self.editor.key_press_event.disconnect(self._remove_previous)
        self.editor.mouse_move_event.disconnect(self._show_tooltip)
        self.editor.paste_event.disconnect(self._paste_event)
        self.indent_dedent_event.disconnect(self.editor.inserted_length_event)

    def lint(self, source_code):
        """Override this method to do the linting."""
        pass

    def _remove_previous(self, event):
        if self.editor.is_navigation(event):
            return

        if event.modifiers() != Qt.NoModifier and not event.text().strip():
            return

        # remove the previous WaveUnderline's
        if self._linter_info:
            cursor = self.editor.textCursor()
            position = cursor.position()
            delta = self.editor.inserted_length
            for previous_start, previous_end, msg in self._linter_info:
                if position <= previous_start + delta:
                    previous_start += delta
                    previous_end += delta
                cursor.setPosition(previous_start, mode=cursor.MoveAnchor)
                cursor.setPosition(previous_end, mode=cursor.KeepAnchor)
                fmt = cursor.charFormat()
                if fmt.underlineStyle() != fmt.WaveUnderline:
                    continue
                fmt.setUnderlineStyle(fmt.NoUnderline)
                fmt.setUnderlineColor(self.editor.color_scheme.foreground)
                cursor.setCharFormat(fmt)
            self.indent_dedent_event.emit(0)

    def _paste_event(self, text):
        self._lint()

    def _check_lint(self, event):
        if self.editor.is_navigation(event):
            return
        if event.key() == Qt.Key_Control or event.key() == Qt.Key_Shift:
            return
        if event.modifiers() != Qt.NoModifier:
            return
        self._lint()

    def _update_color(self, scheme):
        self.error_color = scheme.lint_error
        self.warning_color = scheme.lint_warning
        self._lint()

    @Profile()
    def _lint(self):
        self._linter_info = []

        source_code = self.editor.text()
        if not source_code:
            return

        try:
            self.lint(source_code)
        except Exception as e:
            logger.error(e)

    def _show_tooltip(self, event, cursor):
        if cursor.selectedText().strip():
            position = cursor.position()
            for start, end, message in self._linter_info:
                if start <= position <= end:
                    QtWidgets.QToolTip.showText(event.globalPos(), message)
        else:
            QtWidgets.QToolTip.hideText()
