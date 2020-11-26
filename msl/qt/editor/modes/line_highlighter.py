"""
Highlight the background color of the current line in the :class:`BaseEditor`.
"""
import logging

from msl.qt import QtWidgets, QtGui

from ..types import Mode

logger = logging.getLogger(__name__)


class LineHighlighterMode(Mode):

    def __init__(self, editor):
        """Highlight the background color of the current line in the :class:`BaseEditor`.

        The highlighter color is selected from the :class:`ColorScheme` that is used
        or the color can be manually set by :obj:`.color`.

        Parameters
        ----------
        editor : :class:`BaseEditor`
            The editor.
        """
        Mode.__init__(self, editor)

        self._selection = QtWidgets.QTextEdit.ExtraSelection()
        self._selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

    @property
    def color(self):
        """:class:`QtGui.QColor`: The background color to use for highlighting the current line."""
        return self._selection.format.background().color()

    @color.setter
    def color(self, color):
        self._selection.format.setBackground(QtGui.QColor(color))
        self.highlight()

    def add(self):
        """Overrides :meth:`EditorType.add`."""
        self.editor.cursorPositionChanged.connect(self.highlight)
        self.editor.new_color_scheme_event.connect(self._update_color)

    def remove(self):
        """Overrides :meth:`EditorType.remove`."""
        self.unhighlight()
        self.editor.cursorPositionChanged.disconnect(self.highlight)
        self.editor.new_color_scheme_event.disconnect(self._update_color)

    def highlight(self):
        """Slot to highlight the current line."""
        self._selection.cursor = self.editor.textCursor()
        if self._selection.cursor.selectedText():
            self.unhighlight()
        else:
            self.editor.setExtraSelections([self._selection])

    def unhighlight(self):
        self.editor.setExtraSelections([])

    def _update_color(self, scheme):
        self.color = scheme.line_highlight
