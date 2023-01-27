"""
A toggle switch :class:`QtWidgets.QWidget`.
"""
from .. import Qt
from .. import QtCore
from .. import QtGui
from .. import QtWidgets
from .. import convert
from .. import utils


class ToggleSwitch(QtWidgets.QAbstractButton):

    def __init__(self, *, height=None, initial=False, on_color='#009688', off_color='#B4B4B4',
                 parent=None, toggled=None, tooltip=None):
        """A toggle switch, |toggle_switch|, :class:`QtWidgets.QWidget`

        .. |toggle_switch| image:: ../../docs/_static/toggle_switch.gif
           :scale: 40 %

        Parameters
        ----------
        height : :class:`int`, optional
            The height, in pixels, of the toggle switch.
        initial : :class:`bool`, optional
            Whether the toggle switch is initially in the on (:data:`True`) or off
            (:data:`False`) state.
        on_color
            The color when the :class:`ToggleSwitch` is on. See :func:`~.convert.to_qcolor`
            for details about the different data types that are supported.
        off_color
            The color when the :class:`ToggleSwitch` is off. See :func:`~.convert.to_qcolor`
            for details about the different data types that are supported.
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        toggled
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QAbstractButton.toggled` signal.
        tooltip : :class:`str`, optional
            The tooltip to use for the :class:`ToggleSwitch`.

        Example
        -------
        To view an example with the :class:`ToggleSwitch` run::

        >>> from msl.examples.qt import toggle_switch
        >>> toggle_switch.show()  # doctest: +SKIP
        """
        super(ToggleSwitch, self).__init__(parent=parent)

        if height is None:
            self._height = int(utils.screen_geometry(self).height() * 0.03)
        else:
            self._height = int(height)

        self._off_brush = None
        self._on_brush = None

        self._pad = 4
        self.setCheckable(True)
        self.setChecked(initial)
        self.set_on_color(on_color)
        self.set_off_color(off_color)
        if tooltip:
            self.setToolTip(tooltip)
        if toggled:
            self.toggled.connect(toggled)  # noqa: QAbstractButton.toggled

    @property
    def is_on(self):
        """:class:`bool`: Whether the :class:`ToggleSwitch` is on or off."""
        return self.isChecked()

    def off_color(self):
        """Get the color of the :class:`ToggleSwitch` when it is off.

        Returns
        -------
        :class:`QtGui.QColor`
            The off color.
        """
        return self._off_brush.color()

    def set_off_color(self, color):
        """Set the color of the :class:`ToggleSwitch` when it is off.

        Parameters
        -------
        color
            The color when the :class:`ToggleSwitch` is off. See :func:`~.convert.to_qcolor`
            for details about the different data types that are supported.
        """
        self._off_brush = QtGui.QBrush(convert.to_qcolor(color))
        self.update()

    def on_color(self):
        """Get the color of the :class:`ToggleSwitch` when it is on.

        Returns
        -------
        :class:`QtGui.QColor`
            The on color.
        """
        return self._on_brush.color()

    def set_on_color(self, color):
        """Set the color of the :class:`ToggleSwitch` when it is on.

        Parameters
        -------
        color
            The color when the :class:`ToggleSwitch` is on. See :func:`~.convert.to_qcolor`
            for details about the different data types that are supported.
        """
        self._on_brush = QtGui.QBrush(convert.to_qcolor(color))
        self.update()

    def turn_off(self):
        """Turn the :class:`ToggleSwitch` off."""
        if self.isChecked():
            self.toggle()

    def turn_on(self):
        """Turn the :class:`ToggleSwitch` on."""
        if not self.isChecked():
            self.toggle()

    def enterEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.enterEvent`."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.paintEvent`."""
        diameter = self._height - 2 * self._pad
        radius = diameter * 0.5

        if self.isChecked():
            brush = self._on_brush
            x = self.width() - diameter - self._pad
            opacity = 0.3
        else:
            brush = self._off_brush
            x = self._pad
            opacity = 0.5

        p = QtGui.QPainter(self)
        p.setPen(Qt.PenStyle.NoPen)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
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
            p.setBrush(Qt.GlobalColor.black)
            p.setOpacity(0.12)
            p.drawRoundedRect(rect, radius, radius)
            p.setOpacity(1.0)
            p.setBrush(QtGui.QColor('#BDBDBD'))
            p.drawEllipse(ellipse)

    def sizeHint(self):
        """Overrides :meth:`QtWidgets.QWidget.sizeHint`."""
        return QtCore.QSize(2 * (self._height + self._pad), self._height + 2 * self._pad)
