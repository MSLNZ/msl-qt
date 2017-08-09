"""
A toggle switch QWidget.
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class ToggleSwitch(QtWidgets.QAbstractButton):

    def __init__(self, parent=None, checked_color='#009688', unchecked_color='#B4B4B4'):
        """Constructs a toggle switch, |switch|

        .. |switch| image:: ../../docs/_static/toggle_switch.gif
           :scale: 50 %

        .. literalinclude:: ../../msl/examples/qt/toggle_switch.py

        Parameters
        ----------
        parent : :obj:`QWidget`
            The parent :obj:`QWidget`.
        checked_color : :obj:`str` or :obj:`QColor`
            The color to draw the switch when it is in the checked state.
        unchecked_color : :obj:`str` or :obj:`QColor`
            The color to draw the switch when it is **not** in the checked state.
        """
        super(ToggleSwitch, self).__init__(parent)

        self._pad = 4
        self._checked_brush = QtGui.QBrush(QtGui.QColor(checked_color))
        self._unchecked_brush = QtGui.QBrush(QtGui.QColor(unchecked_color))
        self.setCheckable(True)

    def paintEvent(self, event):
        """Overrides the paintEvent method."""
        diameter = self.height() - 2 * self._pad
        radius = diameter * 0.5

        if self.isChecked():
            brush = self._checked_brush
            x = self.width() - diameter - self._pad
            opacity = 0.3
        else:
            brush = self._unchecked_brush
            x = self._pad
            opacity = 0.5

        p = QtGui.QPainter(self)
        p.setPen(QtCore.Qt.NoPen)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        ellipse = QtCore.QRect(x, self._pad, diameter, diameter)
        w = max(diameter, self.width() - 2 * self._pad)
        rect = QtCore.QRect(self._pad, self._pad, w, diameter)
        if self.isEnabled():
            p.setBrush(brush)
            p.setOpacity(opacity)
            p.drawRoundedRect(rect, radius, radius)
            p.setOpacity(1.0)
            p.drawEllipse(ellipse)
        else:
            p.setBrush(QtCore.Qt.black)
            p.setOpacity(0.12)
            p.drawRoundedRect(rect, radius, radius)
            p.setOpacity(1.0)
            p.setBrush(QtGui.QColor('#BDBDBD'))
            p.drawEllipse(ellipse)

    def enterEvent(self, event):
        """Overrides the enterEvent method."""
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def sizeHint(self):
        """Overrides the sizeHint method."""
        return QtCore.QSize(2 * (self.height() + self._pad), self.height() + 2 * self._pad)
