"""
Inserts a line at a certain column in the :class:`BaseEditor`.
"""
import logging

from ... import (
    QtGui,
    Qt,
)
from ..types import Mode

logger = logging.getLogger(__name__)


class LineLengthMode(Mode):

    def __init__(self, editor, max_line_length=80, color=None):
        super(LineLengthMode, self).__init__(editor)

        self._column = max_line_length

        self._pen = None
        if color is None:
            color = Qt.darkGray
        self.color = color

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, value):
        self._column = int(value)

    @property
    def color(self):
        return self._pen.color()

    @color.setter
    def color(self, value):
        color = QtGui.QColor(value)
        color.setAlpha(50)
        self._pen = QtGui.QPen(color)

    def add(self):
        self.editor.paint_event.connect(self.paint_margin)
        self.editor.new_color_scheme_event.connect(self.update_color)

    def remove(self):
        self.editor.paint_event.disconnect(self.paint_margin)
        self.editor.new_color_scheme_event.disconnect(self.update_color)

    def update_color(self, scheme):
        self.color = scheme.foreground

    def paint_margin(self, event):
        font = self.editor.currentCharFormat().font()
        x = round(QtGui.QFontMetricsF(font).averageCharWidth() * self._column)
        x += self.editor.contentOffset().x()
        x += self.editor.document().documentMargin()
        p = QtGui.QPainter(self.editor.viewport())
        p.setPen(self._pen)
        p.drawLine(x, event.rect().top(), x, event.rect().bottom())
