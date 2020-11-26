"""
Draw line numbers on the left margin
"""
from msl.qt import QtCore, QtGui, Qt

from ..types import Panel


class LineNumberPanel(Panel):

    def __init__(self, editor):
        Panel.__init__(self, editor)
        if editor.color_scheme:
            self._foreground = editor.color_scheme.foreground
            self._background = editor.color_scheme.background
            self._line_highlight = editor.color_scheme.line_highlight
        else:
            self._foreground = Qt.black
            self._background = Qt.lightGray
            self._line_highlight = Qt.lightGray

    def line_number_area_width(self):
        new_block_count = self.editor.blockCount()
        digits = 1
        maximum = max(1, new_block_count)
        while maximum >= 10:
            maximum /= 10
            digits += 1
        return 4 + self.editor.fontMetrics().width('9') * digits

    def update_line_number_area_width(self):
        self.editor.setViewportMargins(self.line_number_area_width()-2, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.update_line_number_area_width()

    def update_color_scheme(self, scheme):
        self._foreground = scheme.foreground
        self._background = scheme.background
        self._line_highlight = scheme.line_highlight

    def update_geometry(self, event):
        cr = self.editor.contentsRect()
        self.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def sizeHint(self):
        return QtCore.QSize(self.line_number_area_width(), 0)

    def add(self):
        self.editor.updateRequest.connect(self.update_line_number_area)
        self.editor.new_color_scheme_event.connect(self.update_color_scheme)
        self.editor.resize_event.connect(self.update_geometry)
        self.update_line_number_area_width()

    def remove(self):
        self.editor.updateRequest.disconnect(self.update_line_number_area)
        self.editor.new_color_scheme_event.disconnect(self.update_color_scheme)
        self.editor.resize_event.disconnect(self.update_geometry)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), self._background)
        painter.setPen(self._foreground)
        font = self.editor.font()
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()
        width = self.width()
        current_line = self.editor.textCursor().blockNumber()
        event_top = event.rect().top()
        event_bottom = event.rect().bottom()
        while block.isValid() and top <= event_bottom:
            if block.isVisible() and bottom >= event_top:
                font.setBold(block_number == current_line)
                if block_number == current_line:
                    painter.fillRect(0, top, width, bottom-top, self._line_highlight)
                painter.setFont(font)
                painter.drawText(0, top, width, bottom-top, Qt.AlignRight, str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1
