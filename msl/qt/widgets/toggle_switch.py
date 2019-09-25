"""
A toggle switch :class:`QtWidgets.QWidget`.
"""
from msl.qt import QtWidgets, Qt, QtCore, QtGui


class ToggleSwitch(QtWidgets.QAbstractButton):

    def __init__(self, *, parent=None, height=None, checked_color='#009688', unchecked_color='#B4B4B4'):
        """Constructs a toggle switch, |toggle_switch|

        .. |toggle_switch| image:: ../../docs/_static/toggle_switch.gif
           :scale: 40 %

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        height : :class:`int`, optional
            The height, in pixels, of the toggle switch.
        checked_color : :class:`QtGui.QColor`, optional
            The color to draw the switch when it is in the checked state.
            Can be any data type and value that the constructor of a
            :class:`QtGui.QColor` accepts.
        unchecked_color : :class:`QtGui.QColor`, optional
            The color to draw the switch when it is **not** in the checked state.
            Can be any data type and value that the constructor of a
            :class:`QtGui.QColor` accepts.

        Example
        -------
        To view an example with the :class:`ToggleSwitch` run::

        >>> from msl.examples.qt import toggle_switch  # doctest: +SKIP
        >>> toggle_switch.show()  # doctest: +SKIP
        """
        super(ToggleSwitch, self).__init__(parent=parent)

        screen_height = QtWidgets.QDesktopWidget().availableGeometry(self).height()
        self._height = height if height is not None else int(screen_height*0.03)
        self._pad = 4
        self._checked_brush = QtGui.QBrush(QtGui.QColor(checked_color))
        self._unchecked_brush = QtGui.QBrush(QtGui.QColor(unchecked_color))
        self.setCheckable(True)

    def enterEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.enterEvent`."""
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.paintEvent`."""
        diameter = self._height - 2 * self._pad
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
        p.setPen(Qt.NoPen)
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
            p.setBrush(Qt.black)
            p.setOpacity(0.12)
            p.drawRoundedRect(rect, radius, radius)
            p.setOpacity(1.0)
            p.setBrush(QtGui.QColor('#BDBDBD'))
            p.drawEllipse(ellipse)

    def sizeHint(self):
        """Overrides :meth:`QtWidgets.QWidget.sizeHint`."""
        return QtCore.QSize(2 * (self._height + self._pad), self._height + 2 * self._pad)
