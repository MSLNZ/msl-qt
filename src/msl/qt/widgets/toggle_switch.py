"""A toggle switch widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt._qt import QtCore, QtGui, QtWidgets
from msl.qt.convert import to_qcolor
from msl.qt.utils import screen_geometry

if TYPE_CHECKING:
    from typing import Callable

    from msl.qt.typing import Color


class ToggleSwitch(QtWidgets.QAbstractButton):
    """A toggle switch.

    <img src="../assets/images/toggle_switch.gif" style="width: 15%; height: auto;">
    """

    def __init__(
        self,
        *,
        height: int | None = None,
        initial: bool = False,
        on_color: Color = "#009688",
        off_color: Color = "#B4B4B4",
        parent: QtWidgets.QWidget | None = None,
        toggled: Callable[[bool], None] | None = None,
        tooltip: str | None = None,
    ) -> None:
        """A toggle switch.

        !!! example "Run the example"
            ```console
            python -c "from msl.examples.qt import show; show('ToggleSwitch')"
            ```

            ??? abstract "Click to view the example source code"
                <!-- fmt: off -->
                ```python
                --8<-- "src/msl/examples/qt/toggle_switch.py"
                ```
                <!-- fmt: on -->

        Args:
            height: The height, in pixels, of the toggle switch.
            initial: Whether the toggle switch is initially in the on (`True`) or off (`False`) state.
            on_color: The color when the toggle switch is on.
            off_color: The color when the toggle switch is off.
            parent: The parent widget.
            toggled: A callable function to use as a slot for the [toggled][QtWidgets.QAbstractButton.toggled] signal.
            tooltip: The tooltip to use for the toggle switch.
        """
        super().__init__(parent=parent)

        if height is None:
            self._height: int = int(screen_geometry(self).height() * 0.03)
            if self._height == 0:
                self._height = 25
        else:
            self._height = int(height)

        self._pad: int = 4
        self.setCheckable(True)
        self.setChecked(initial)
        if tooltip:
            self.setToolTip(tooltip)
        if toggled:
            _ = self.toggled.connect(toggled)

        self._off_brush: QtGui.QBrush = QtGui.QBrush(to_qcolor(off_color))
        self._on_brush: QtGui.QBrush = QtGui.QBrush(to_qcolor(on_color))
        self.update()

    @property
    def is_on(self) -> bool:
        """Whether the [ToggleSwitch][] is in the on or off state."""
        return self.isChecked()

    def off_color(self) -> QtGui.QColor:
        """Get the color of the [ToggleSwitch][] when it is off.

        Returns:
            The *off* color.
        """
        return self._off_brush.color()

    def set_off_color(self, color: Color) -> None:
        """Set the color of the [ToggleSwitch][] when it is off.

        Args:
            color: The color when the [ToggleSwitch][] is off.
        """
        self._off_brush = QtGui.QBrush(to_qcolor(color))
        self.update()

    def on_color(self) -> QtGui.QColor:
        """Get the color of the [ToggleSwitch][] when it is on.

        Returns:
            The *on* color.
        """
        return self._on_brush.color()

    def set_on_color(self, color: Color) -> None:
        """Set the color of the [ToggleSwitch][] when it is on.

        Args:
            color: The color when the [ToggleSwitch][] is on.
        """
        self._on_brush = QtGui.QBrush(to_qcolor(color))
        self.update()

    def turn_off(self) -> None:
        """Turn the [ToggleSwitch][] to the *off* state."""
        if self.isChecked():
            self.toggle()

    def turn_on(self) -> None:
        """Turn the [ToggleSwitch][] to the *on* state."""
        if not self.isChecked():
            self.toggle()

    def enterEvent(self, _: QtGui.QEnterEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QWidget.enterEvent`."""
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, _: QtGui.QPaintEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QWidget.paintEvent`."""
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
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)  # noqa: FBT003
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
            p.setBrush(QtCore.Qt.GlobalColor.black)
            p.setOpacity(0.12)
            p.drawRoundedRect(rect, radius, radius)
            p.setOpacity(1.0)
            p.setBrush(QtGui.QColor("#BDBDBD"))
            p.drawEllipse(ellipse)

    def sizeHint(self) -> QtCore.QSize:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QWidget.sizeHint`."""
        return QtCore.QSize(2 * (self._height + self._pad), self._height + 2 * self._pad)
