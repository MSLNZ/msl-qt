"""An LED widget."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from msl.qt._qt import QtCore, QtGui, QtSvg, QtWidgets, Signal
from msl.qt.convert import to_qcolor
from msl.qt.utils import screen_geometry

if TYPE_CHECKING:
    from msl.qt.typing import Color


class Shape(Enum):
    """[LED][msl.qt.widgets.LED] shapes."""

    Circle = "Circle"
    Rounded = "Rounded"
    Square = "Square"
    Triangle = "Triangle"


class LED(QtWidgets.QWidget):
    """An LED widget."""

    Circle: Shape = Shape.Circle
    Rounded: Shape = Shape.Rounded
    Square: Shape = Shape.Square
    Triangle: Shape = Shape.Triangle

    clicked: Signal = Signal()
    """Emitted when the LED is clicked (even if it is not `clickable`)."""

    toggled: Signal = Signal(bool)
    """Emitted when the LED changes state."""

    def __init__(
        self,
        *,
        parent: QtWidgets.QWidget | None = None,
        shape: str | Shape = "Circle",
        on_color: Color = "#0F6900",
        off_color: Color = "grey",
        clickable: bool = False,
        tooltip: str | None = None,
    ) -> None:
        """An LED widget, <img src="assets/images/led_widget.gif" style="width: 40%; height: auto;">.

        This class is based off of the [QLed](https://github.com/jazzycamel/QLed) project.

        !!! example
            ```python
            from msl.examples.qt import led
            led.show()
            ```

        Args:
            parent: The parent widget.
            shape: The shape to draw the LED.
            on_color: The color of the LED when it is on.
            off_color: The color of the LED when it is off.
            clickable: Whether the state of the LED can be changed by clicking on it.
            tooltip: The tooltip to use for the LED.
        """
        super().__init__(parent=parent)
        self._is_on: bool = False
        self._renderer: QtSvg.QSvgRenderer = QtSvg.QSvgRenderer()

        self._height_hint: int = screen_geometry(self).height() // 38
        self._rounded_factor: float = 2.0
        self._triangle_factor: float = 4.0 / 3.0

        if tooltip:
            self.setToolTip(tooltip)

        self._is_clickable: bool = bool(clickable)
        self._off_color: QtGui.QColor = to_qcolor(off_color)
        self._on_color: QtGui.QColor = to_qcolor(on_color)
        self._shape: Shape = Shape(shape)
        self.update()

    @property
    def is_on(self) -> bool:
        """[bool][] &mdash; Whether the LED is on or off."""
        return self._is_on

    def clickable(self) -> bool:
        """Get if the on/off state of the LED can be changed by clicking on it."""
        return self._is_clickable

    def set_clickable(self, clickable: bool) -> None:  # noqa: FBT001
        """Set if the on/off state of the LED can be changed by clicking on it.

        Args:
            clickable: Whether the state of the LED can be changed by clicking on it.
        """
        self._is_clickable = bool(clickable)

    def off_color(self) -> QtGui.QColor:
        """Get the color of the LED when it is off."""
        return self._off_color

    def set_off_color(self, color: Color) -> None:
        """Set the color of the LED when it is off.

        Args:
            color: The color when the LED is off.
        """
        self._off_color = to_qcolor(color)
        self.update()

    def on_color(self) -> QtGui.QColor:
        """Get the color of the LED when it is on."""
        return self._on_color

    def set_on_color(self, color: Color) -> None:
        """Set the color of the LED when it is on.

        Args:
            color: The *on* color.
        """
        self._on_color = to_qcolor(color)
        self.update()

    def shape(self) -> Shape:
        """Get the shape of the LED."""
        return self._shape

    def set_shape(self, shape: str | Shape) -> None:
        """Set the shape of the LED.

        Args:
            shape: The shape to draw the LED.
        """
        self._shape = Shape(shape)
        self.update()

    def toggle(self) -> None:
        """Toggle the on/off state of the LED."""
        self._is_on = not self._is_on
        self.update()
        self.toggled.emit(self._is_on)

    def turn_off(self) -> None:
        """Turn the LED off."""
        if self._is_on:
            self.toggle()

    def turn_on(self) -> None:
        """Turn the LED on."""
        if not self._is_on:
            self.toggle()

    def sizeHint(self) -> QtCore.QSize:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides [sizeHint][QtWidgets.QWidget.sizeHint]."""
        if self._shape == Shape.Triangle:
            w = round(self._triangle_factor * self._height_hint)
            return QtCore.QSize(w, self._height_hint)
        if self._shape == Shape.Rounded:
            w = round(self._rounded_factor * self._height_hint)
            return QtCore.QSize(w, self._height_hint)
        return QtCore.QSize(self._height_hint, self._height_hint)

    def paintEvent(self, _: QtGui.QPaintEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides [paintEvent][QtWidgets.QWidget.paintEvent]."""
        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        h = float(option.rect.height())
        w = float(option.rect.width())
        if self._shape in {Shape.Triangle, Shape.Rounded}:
            aspect = self._triangle_factor if self._shape == Shape.Triangle else self._rounded_factor
            ah = w / aspect
            aw = w
            if ah > h:
                ah = h
                aw = h * aspect
            x = abs(aw - w) / 2.0
            y = abs(ah - h) / 2.0
            bounds = QtCore.QRectF(x, y, aw, ah)
        else:
            size = min(w, h)
            x = abs(size - w) / 2.0
            y = abs(size - h) / 2.0
            bounds = QtCore.QRectF(x, y, size, size)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)  # noqa: FBT003

        color = (self._on_color if self._is_on else self._off_color) if self.isEnabled() else to_qcolor("#BDBDBD")
        lighter = color.lighter(150)  # 150 -> 50% brighter
        color_str = f"rgb({color.red()}),{color.green()},{color.blue()})"
        lighter_str = f"rgb({lighter.red()},{lighter.green()},{lighter.blue()})"

        svg = (SVG_MAP[self._shape] % (color_str, lighter_str)).encode("utf8")
        if self._renderer.load(QtCore.QByteArray(svg)):
            self._renderer.render(painter, bounds)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides [mouseReleaseEvent][QtWidgets.QWidget.mouseReleaseEvent]."""
        if self._is_clickable:
            self.toggle()
        self.clicked.emit()
        super().mouseReleaseEvent(event)


# cSpell: ignore xlink linecap linejoin miterlimit sodipodi nodetypes csccscc
# ruff: disable[E501]
SVG_MAP = {
    Shape.Circle: """
      <svg height="50.000000px" id="svg9493" width="50.000000px" xmlns="https://www.w3.org/2000/svg">
        <defs id="defs9495">
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient6650" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient6494">
            <stop id="stop6496" offset="0.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
            <stop id="stop6498" offset="1.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient6648" x1="23.213980" x2="23.201290" xlink:href="#linearGradient6494" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient6646" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient6644" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient id="linearGradient6506">
            <stop id="stop6508" offset="0.0000000" style="stop-color:#ffffff;stop-opacity:0.0000000;"/>
            <stop id="stop6510" offset="1.0000000" style="stop-color:#ffffff;stop-opacity:0.87450981;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7498" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient7464">
            <stop id="stop7466" offset="0.0000000" style="stop-color:#00039a;stop-opacity:1.0000000;"/>
            <stop id="stop7468" offset="1.0000000" style="stop-color:#afa5ff;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7496" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient id="linearGradient5756">
            <stop id="stop5758" offset="0.0000000" style="stop-color:#828282;stop-opacity:1.0000000;"/>
            <stop id="stop5760" offset="1.0000000" style="stop-color:#929292;stop-opacity:0.35294119;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9321" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient id="linearGradient5742">
            <stop id="stop5744" offset="0.0000000" style="stop-color:#adadad;stop-opacity:1.0000000;"/>
            <stop id="stop5746" offset="1.0000000" style="stop-color:#f0f0f0;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7492" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9527" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9529" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9531" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9533" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
        </defs>
        <g id="layer1">
          <g id="g9447" style="overflow:visible" transform="matrix(31.25000,0.000000,0.000000,31.25000,-625.0232,-1325.000)">
            <path d="M 24.000001,43.200001 C 24.000001,43.641601 23.641601,44.000001 23.200001,44.000001 C 22.758401,44.000001 22.400001,43.641601 22.400001,43.200001 C 22.400001,42.758401 22.758401,42.400001 23.200001,42.400001 C 23.641601,42.400001 24.000001,42.758401 24.000001,43.200001 z " id="path6596" style="fill:url(#linearGradient6644);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="translate(-2.399258,-1.000000e-6)"/>
            <path d="M 23.906358,43.296204 C 23.906358,43.625433 23.639158,43.892633 23.309929,43.892633 C 22.980700,43.892633 22.713500,43.625433 22.713500,43.296204 C 22.713500,42.966975 22.980700,42.699774 23.309929,42.699774 C 23.639158,42.699774 23.906358,42.966975 23.906358,43.296204 z " id="path6598" style="fill:url(#linearGradient6646);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="matrix(1.082474,0.000000,0.000000,1.082474,-4.431649,-3.667015)"/>
            <path d="M 23.906358,43.296204 C 23.906358,43.625433 23.639158,43.892633 23.309929,43.892633 C 22.980700,43.892633 22.713500,43.625433 22.713500,43.296204 C 22.713500,42.966975 22.980700,42.699774 23.309929,42.699774 C 23.639158,42.699774 23.906358,42.966975 23.906358,43.296204 z " id="path6600" style="fill:url(#linearGradient6648);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="matrix(0.969072,0.000000,0.000000,0.969072,-1.788256,1.242861)"/>
            <path d="M 23.906358,43.296204 C 23.906358,43.625433 23.639158,43.892633 23.309929,43.892633 C 22.980700,43.892633 22.713500,43.625433 22.713500,43.296204 C 22.713500,42.966975 22.980700,42.699774 23.309929,42.699774 C 23.639158,42.699774 23.906358,42.966975 23.906358,43.296204 z " id="path6602" style="fill:url(#linearGradient6650);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="matrix(0.773196,0.000000,0.000000,0.597938,2.776856,17.11876)"/>
          </g>
        </g>
      </svg>
    """,
    Shape.Rounded: """
      <svg height="50.000000px" id="svg9493" width="100.00000px" xmlns="https://www.w3.org/2000/svg">
        <defs id="defs9495">
          <linearGradient gradientTransform="matrix(0.928127,0.000000,0.000000,0.639013,13.55634,12.87587)" gradientUnits="userSpaceOnUse" id="linearGradient13424" x1="21.593750" x2="21.593750" xlink:href="#linearGradient6506" y1="47.917328" y2="46.774261"/>
          <linearGradient id="linearGradient6494">
            <stop id="stop6496" offset="0.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
            <stop id="stop6498" offset="1.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientTransform="translate(12.00000,-4.000002)" gradientUnits="userSpaceOnUse" id="linearGradient13427" x1="21.591305" x2="21.593750" xlink:href="#linearGradient6494" y1="46.617390" y2="47.781250"/>
          <linearGradient gradientTransform="translate(12.00000,-4.000002)" gradientUnits="userSpaceOnUse" id="linearGradient13430" x1="21.408695" x2="21.834784" xlink:href="#linearGradient5756" y1="46.556522" y2="47.843750"/>
          <linearGradient gradientTransform="translate(12.00000,-4.000002)" gradientUnits="userSpaceOnUse" id="linearGradient13433" x1="21.594427" x2="21.600000" xlink:href="#linearGradient5742" y1="46.376728" y2="48.000000"/>
          <linearGradient gradientTransform="matrix(0.928127,0.000000,0.000000,0.639013,21.55634,15.27587)" gradientUnits="userSpaceOnUse" id="linearGradient13472" x1="21.593750" x2="21.593750" xlink:href="#linearGradient6506" y1="47.917328" y2="46.774261"/>
          <linearGradient gradientTransform="translate(20.00000,-1.600002)" gradientUnits="userSpaceOnUse" id="linearGradient13475" x1="21.591305" x2="21.593750" xlink:href="#linearGradient9163" y1="46.617390" y2="47.781250"/>
          <linearGradient gradientTransform="translate(20.00000,-1.600002)" gradientUnits="userSpaceOnUse" id="linearGradient13478" x1="21.408695" x2="21.834784" xlink:href="#linearGradient5756" y1="46.556522" y2="47.843750"/>
          <linearGradient gradientTransform="translate(20.00000,-1.600002)" gradientUnits="userSpaceOnUse" id="linearGradient13481" x1="21.594427" x2="21.600000" xlink:href="#linearGradient5742" y1="46.376728" y2="48.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9199" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient9163">
            <stop id="stop9165" offset="0.0000000" style="stop-color:#000000;stop-opacity:1.0000000;"/>
            <stop id="stop9167" offset="1.0000000" style="stop-color:#8c8c8c;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9197" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9195" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9193" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient id="linearGradient6506">
            <stop id="stop6508" offset="0.0000000" style="stop-color:#ffffff;stop-opacity:0.0000000;"/>
            <stop id="stop6510" offset="1.0000000" style="stop-color:#ffffff;stop-opacity:0.87450981;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7498" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient7464">
            <stop id="stop7466" offset="0.0000000" style="stop-color:#00039a;stop-opacity:1.0000000;"/>
            <stop id="stop7468" offset="1.0000000" style="stop-color:#afa5ff;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7496" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient id="linearGradient5756">
            <stop id="stop5758" offset="0.0000000" style="stop-color:#828282;stop-opacity:1.0000000;"/>
            <stop id="stop5760" offset="1.0000000" style="stop-color:#929292;stop-opacity:0.35294119;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9321" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient id="linearGradient5742">
            <stop id="stop5744" offset="0.0000000" style="stop-color:#adadad;stop-opacity:1.0000000;"/>
            <stop id="stop5746" offset="1.0000000" style="stop-color:#f0f0f0;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7492" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9527" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9529" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9531" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9533" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(24.16238,0.000000,0.000000,18.68556,-538.2464,-790.0391)" gradientUnits="userSpaceOnUse" id="linearGradient1336" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(30.28350,0.000000,0.000000,30.28350,-680.9062,-1286.161)" gradientUnits="userSpaceOnUse" id="linearGradient1339" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientTransform="matrix(33.82731,0.000000,0.000000,33.82731,-763.5122,-1439.594)" gradientUnits="userSpaceOnUse" id="linearGradient1342" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientTransform="matrix(31.25000,0.000000,0.000000,31.25000,-700.0000,-1325.000)" gradientUnits="userSpaceOnUse" id="linearGradient1345" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
        </defs>
        <g id="layer1">
          <g id="g13543" style="overflow:visible" transform="matrix(31.25000,0.000000,0.000000,31.25000,-999.9999,-1325.000)">
            <path d="M 32.799998,42.400000 L 34.399998,42.400000 C 34.843198,42.400000 35.199998,42.756800 35.199998,43.200000 C 35.199998,43.643200 34.843198,44.000000 34.399998,44.000000 L 32.799998,44.000000 C 32.356798,44.000000 31.999998,43.643200 31.999998,43.200000 C 31.999998,42.756800 32.356798,42.400000 32.799998,42.400000 z " id="path13335" style="fill:url(#linearGradient13433);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000"/>
            <path d="M 32.812498,42.562498 C 32.447387,42.562498 32.156248,42.829606 32.156248,43.187498 C 32.156248,43.545390 32.454607,43.843750 32.812498,43.843748 L 34.406248,43.843748 C 34.764141,43.843748 35.031248,43.552611 35.031248,43.187498 C 35.031248,42.822387 34.771358,42.562498 34.406248,42.562498 L 32.812498,42.562498 z " id="path13337" style="fill:url(#linearGradient13430);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
            <path d="M 32.812498,42.624998 C 32.485887,42.624998 32.218748,42.871665 32.218748,43.187498 C 32.218748,43.503332 32.496667,43.781249 32.812498,43.781248 L 34.406248,43.781248 C 34.722082,43.781248 34.968748,43.514111 34.968748,43.187498 C 34.968748,42.860887 34.732858,42.624998 34.406248,42.624998 L 32.812498,42.624998 z " id="path13339" style="fill:url(#linearGradient13427);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
            <path d="M 32.872983,42.669849 C 32.569847,42.669849 32.321908,42.827473 32.321908,43.029294 C 32.321908,43.231116 32.579852,43.408709 32.872983,43.408708 L 34.352185,43.408708 C 34.645320,43.408708 34.874257,43.238004 34.874257,43.029294 C 34.874257,42.820585 34.655321,42.669849 34.352185,42.669849 L 32.872983,42.669849 z " id="path13341" style="fill:url(#linearGradient13424);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
          </g>
        </g>
      </svg>
    """,
    Shape.Square: """
      <svg height="50.000000px" id="svg9493" width="50.000000px" xmlns="https://www.w3.org/2000/svg">
        <defs id="defs9495">
          <linearGradient gradientTransform="matrix(0.388435,0.000000,0.000000,0.618097,2.806900,2.626330)" gradientUnits="userSpaceOnUse" id="linearGradient31681" x1="21.593750" x2="21.593750" xlink:href="#linearGradient6506" y1="47.917328" y2="46.774261"/>
          <linearGradient id="linearGradient6494">
            <stop id="stop6496" offset="0.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
            <stop id="stop6498" offset="1.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient31704" x1="18.390625" x2="18.390625" xlink:href="#linearGradient6494" y1="43.400002" y2="44.593750"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient31624" x1="17.728125" x2="19.031250" xlink:href="#linearGradient5756" y1="43.337502" y2="44.656250"/>
          <linearGradient gradientTransform="matrix(0.500000,0.000000,0.000000,1.000000,-3.600000,-8.800000)" gradientUnits="userSpaceOnUse" id="linearGradient31686" x1="29.600000" x2="29.600000" xlink:href="#linearGradient5742" y1="39.991302" y2="41.599998"/>
          <linearGradient gradientTransform="matrix(0.388435,0.000000,0.000000,0.618097,7.606900,5.026330)" gradientUnits="userSpaceOnUse" id="linearGradient31649" x1="21.593750" x2="21.593750" xlink:href="#linearGradient6506" y1="47.917328" y2="46.774261"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient31710" x1="18.390625" x2="18.390625" xlink:href="#linearGradient9163" y1="43.400002" y2="44.593750"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient31570" x1="17.728125" x2="19.031250" xlink:href="#linearGradient5756" y1="43.337502" y2="44.656250"/>
          <linearGradient gradientTransform="matrix(0.500000,0.000000,0.000000,1.000000,1.200000,-6.400000)" gradientUnits="userSpaceOnUse" id="linearGradient31654" x1="29.600000" x2="29.600000" xlink:href="#linearGradient5742" y1="39.991302" y2="41.599998"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9199" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient9163">
            <stop id="stop9165" offset="0.0000000" style="stop-color:#000000;stop-opacity:1.0000000;"/>
            <stop id="stop9167" offset="1.0000000" style="stop-color:#8c8c8c;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9197" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9195" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9193" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient id="linearGradient6506">
            <stop id="stop6508" offset="0.0000000" style="stop-color:#ffffff;stop-opacity:0.0000000;"/>
            <stop id="stop6510" offset="1.0000000" style="stop-color:#ffffff;stop-opacity:0.87450981;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7498" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient7464">
            <stop id="stop7466" offset="0.0000000" style="stop-color:#00039a;stop-opacity:1.0000000;"/>
            <stop id="stop7468" offset="1.0000000" style="stop-color:#afa5ff;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7496" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient id="linearGradient5756">
            <stop id="stop5758" offset="0.0000000" style="stop-color:#828282;stop-opacity:1.0000000;"/>
            <stop id="stop5760" offset="1.0000000" style="stop-color:#929292;stop-opacity:0.35294119;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9321" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient id="linearGradient5742">
            <stop id="stop5744" offset="0.0000000" style="stop-color:#adadad;stop-opacity:1.0000000;"/>
            <stop id="stop5746" offset="1.0000000" style="stop-color:#f0f0f0;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7492" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9527" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9529" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9531" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9533" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(24.16238,0.000000,0.000000,18.68556,-538.2464,-790.0391)" gradientUnits="userSpaceOnUse" id="linearGradient1336" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(30.28350,0.000000,0.000000,30.28350,-680.9062,-1286.161)" gradientUnits="userSpaceOnUse" id="linearGradient1339" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientTransform="matrix(33.82731,0.000000,0.000000,33.82731,-763.5122,-1439.594)" gradientUnits="userSpaceOnUse" id="linearGradient1342" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientTransform="matrix(31.25000,0.000000,0.000000,31.25000,-700.0000,-1325.000)" gradientUnits="userSpaceOnUse" id="linearGradient1345" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
        </defs>
        <g id="layer1">
          <g id="g31718" style="overflow:visible" transform="matrix(31.25000,0.000000,0.000000,31.25000,-325.0000,-975.0000)">
            <path d="M 10.400000,31.200000 L 12.000000,31.200000 L 12.000000,32.800000 L 10.400000,32.800000 L 10.400000,31.200000 z " id="path31614" style="fill:url(#linearGradient31686);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000"/>
            <path d="M 17.750000,43.343750 L 17.750000,44.656250 L 19.031250,44.656250 L 19.031250,43.343750 L 17.750000,43.343750 z " id="path31616" style="fill:url(#linearGradient31624);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="translate(-7.190625,-12.00000)"/>
            <path d="M 17.812500,43.406250 L 17.812500,44.593750 L 18.968750,44.593750 L 18.968750,43.406250 L 17.812500,43.406250 z " id="path31618" style="fill:url(#linearGradient31704);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible" transform="translate(-7.190625,-12.00000)"/>
            <path d="M 10.891195,31.445120 C 10.630356,31.445967 10.660563,31.393294 10.660563,31.792800 C 10.660563,31.988016 10.768517,32.159796 10.891195,32.159795 L 11.510263,32.159795 C 11.632945,32.159795 11.728757,31.994678 11.728757,31.792800 C 11.728757,31.389990 11.754584,31.441761 11.510263,31.445120 L 10.891195,31.445120 z " id="path31620" sodipodi:nodetypes="csccscc" style="fill:url(#linearGradient31681);fill-opacity:1.0000000;stroke:none;stroke-width:0.80000001;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
          </g>
        </g>
      </svg>
    """,
    Shape.Triangle: """
      <svg height="50.000000px" id="svg9493" width="50.000000px" xmlns="https://www.w3.org/2000/svg">
        <defs id="defs9495">
          <linearGradient gradientTransform="matrix(0.389994,0.000000,0.000000,0.403942,4.557010,29.83582)" gradientUnits="userSpaceOnUse" id="linearGradient28861" x1="23.187498" x2="23.187498" xlink:href="#linearGradient6506" y1="28.449617" y2="26.670279"/>
          <linearGradient id="linearGradient6494">
            <stop id="stop6496" offset="0.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
            <stop id="stop6498" offset="1.0000000" style="stop-color:%s;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientTransform="translate(-9.587500,13.60000)" gradientUnits="userSpaceOnUse" id="linearGradient28864" x1="23.181250" x2="23.187500" xlink:href="#linearGradient6494" y1="26.793751" y2="27.843750"/>
          <linearGradient gradientTransform="translate(-9.587500,13.60000)" gradientUnits="userSpaceOnUse" id="linearGradient28867" x1="22.762501" x2="23.812500" xlink:href="#linearGradient5756" y1="26.687500" y2="27.906250"/>
          <linearGradient gradientTransform="translate(-9.600000,13.60000)" gradientUnits="userSpaceOnUse" id="linearGradient28870" x1="23.187500" x2="23.200001" xlink:href="#linearGradient5742" y1="26.400000" y2="28.000000"/>
          <linearGradient gradientTransform="matrix(0.389994,0.000000,0.000000,0.403942,9.357010,32.23582)" gradientUnits="userSpaceOnUse" id="linearGradient28801" x1="23.187498" x2="23.187498" xlink:href="#linearGradient6506" y1="28.449617" y2="26.670279"/>
          <linearGradient gradientTransform="translate(-4.787500,16.00000)" gradientUnits="userSpaceOnUse" id="linearGradient28804" x1="23.181250" x2="23.187500" xlink:href="#linearGradient9163" y1="26.793751" y2="27.843750"/>
          <linearGradient gradientTransform="translate(-4.787500,16.00000)" gradientUnits="userSpaceOnUse" id="linearGradient28807" x1="22.762501" x2="23.812500" xlink:href="#linearGradient5756" y1="26.687500" y2="27.906250"/>
          <linearGradient gradientTransform="translate(-4.800000,16.00000)" gradientUnits="userSpaceOnUse" id="linearGradient28810" x1="23.187500" x2="23.200001" xlink:href="#linearGradient5742" y1="26.400000" y2="28.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9199" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient9163">
            <stop id="stop9165" offset="0.0000000" style="stop-color:#000000;stop-opacity:1.0000000;"/>
            <stop id="stop9167" offset="1.0000000" style="stop-color:#8c8c8c;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9197" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9195" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9193" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient id="linearGradient6506">
            <stop id="stop6508" offset="0.0000000" style="stop-color:#ffffff;stop-opacity:0.0000000;"/>
            <stop id="stop6510" offset="1.0000000" style="stop-color:#ffffff;stop-opacity:0.87450981;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7498" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient id="linearGradient7464">
            <stop id="stop7466" offset="0.0000000" style="stop-color:#00039a;stop-opacity:1.0000000;"/>
            <stop id="stop7468" offset="1.0000000" style="stop-color:#afa5ff;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7496" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient id="linearGradient5756">
            <stop id="stop5758" offset="0.0000000" style="stop-color:#828282;stop-opacity:1.0000000;"/>
            <stop id="stop5760" offset="1.0000000" style="stop-color:#929292;stop-opacity:0.35294119;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9321" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient id="linearGradient5742">
            <stop id="stop5744" offset="0.0000000" style="stop-color:#adadad;stop-opacity:1.0000000;"/>
            <stop id="stop5746" offset="1.0000000" style="stop-color:#f0f0f0;stop-opacity:1.0000000;"/>
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient7492" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9527" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9529" x1="22.935030" x2="23.662106" xlink:href="#linearGradient5756" y1="42.699776" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9531" x1="23.213980" x2="23.201290" xlink:href="#linearGradient7464" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientUnits="userSpaceOnUse" id="linearGradient9533" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(24.16238,0.000000,0.000000,18.68556,-538.2464,-790.0391)" gradientUnits="userSpaceOnUse" id="linearGradient1336" x1="23.402565" x2="23.389874" xlink:href="#linearGradient6506" y1="44.066776" y2="42.883698"/>
          <linearGradient gradientTransform="matrix(30.28350,0.000000,0.000000,30.28350,-680.9062,-1286.161)" gradientUnits="userSpaceOnUse" id="linearGradient1339" x1="23.213980" x2="23.201290" xlink:href="#linearGradient9163" y1="42.754631" y2="43.892632"/>
          <linearGradient gradientTransform="matrix(33.82731,0.000000,0.000000,33.82731,-763.5122,-1439.594)" gradientUnits="userSpaceOnUse" id="linearGradient1342" x1="23.349695" x2="23.440580" xlink:href="#linearGradient5756" y1="42.767944" y2="43.710873"/>
          <linearGradient gradientTransform="matrix(31.25000,0.000000,0.000000,31.25000,-700.0000,-1325.000)" gradientUnits="userSpaceOnUse" id="linearGradient1345" x1="23.193102" x2="23.200001" xlink:href="#linearGradient5742" y1="42.429230" y2="44.000000"/>
        </defs>
        <g id="layer1">
          <g id="g28884" style="overflow:visible" transform="matrix(31.25000,0.000000,0.000000,31.25000,-400.0000,-1250.000)">
            <path d="M 14.400000,41.600000 L 12.800000,41.600000 L 13.600000,40.000000 L 14.400000,41.600000 z " id="path28664" sodipodi:nodetypes="cccc" style="fill:url(#linearGradient28870);fill-opacity:1.0000000;stroke:none;stroke-width:0.064000003;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000"/>
            <path d="M 13.600000,40.256250 L 12.975000,41.506250 L 14.225000,41.506250 L 13.600000,40.256250 z " id="path28666" style="fill:url(#linearGradient28867);fill-opacity:1.0000000;stroke:none;stroke-width:0.064000003;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
            <path d="M 13.600000,40.381250 L 13.068750,41.443750 L 14.131250,41.443750 L 13.600000,40.381250 z " id="path28668" style="fill:url(#linearGradient28864);fill-opacity:1.0000000;stroke:none;stroke-width:0.064000003;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
            <path d="M 13.575621,40.552906 C 13.555816,40.559679 13.538695,40.572979 13.526872,40.590776 C 13.522451,40.594595 13.518372,40.598819 13.514685,40.603399 L 13.307500,41.032587 C 13.299161,41.047990 13.294953,41.065424 13.295313,41.083080 C 13.296850,41.096430 13.300996,41.109315 13.307500,41.120950 C 13.310377,41.129925 13.314481,41.138427 13.319688,41.146196 C 13.323375,41.150775 13.327454,41.155000 13.331875,41.158819 C 13.339376,41.164212 13.347584,41.168462 13.356250,41.171442 C 13.367483,41.178179 13.379923,41.182474 13.392812,41.184066 L 13.807180,41.184066 C 13.835802,41.183428 13.862639,41.169530 13.880304,41.146196 C 13.884725,41.142377 13.888804,41.138152 13.892491,41.133573 C 13.898995,41.121938 13.903142,41.109053 13.904679,41.095703 C 13.905039,41.078047 13.900831,41.060614 13.892491,41.045211 C 13.892751,41.041007 13.892751,41.036791 13.892491,41.032587 L 13.685307,40.603399 C 13.681620,40.598819 13.677541,40.594595 13.673120,40.590776 C 13.650701,40.559305 13.612491,40.544463 13.575621,40.552906 z " id="path28670" style="fill:url(#linearGradient28861);fill-opacity:1.0000000;stroke:none;stroke-width:0.064000003;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4.0000000;stroke-opacity:1.0000000;overflow:visible"/>
          </g>
        </g>
      </svg>
    """,
}
# ruff: enable[E501]
