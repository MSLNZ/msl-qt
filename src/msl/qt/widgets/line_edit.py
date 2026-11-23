"""A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size.

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('LineEdit')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8<-- "src/msl/examples/qt/line_edit.py"
        ```
"""

from __future__ import annotations

import warnings
from contextlib import suppress
from typing import TYPE_CHECKING

from msl.qt.binding import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    from typing import Any, Callable


class LineEdit(QtWidgets.QLineEdit):
    """A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size."""

    def __init__(
        self,
        *,
        align: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignLeft,
        parent: QtWidgets.QWidget | None = None,
        read_only: bool = False,
        rescale: bool = False,
        text: str | None = None,
        text_changed: Callable[[str], Any] | None = None,
        tooltip: str | None = None,
    ) -> None:
        """A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size.

        Args:
            align: How to align the text.
            parent: The parent widget.
            read_only: Whether the displayed text is read only.
            rescale: Whether the displayed text rescales its font size when the widget is resized.
            text: The initial text to display.
            text_changed: A callable function to use as a [Slot][msl.qt.binding.Slot] for the
                [textChanged][QtWidgets.QLineEdit.textChanged] [Signal][msl.qt.binding.Signal].
                The function receives the text (as a [str][]) from the [Signal][msl.qt.binding.Signal].
            tooltip: The tooltip to display for the line edit.
        """
        super().__init__(parent=parent)
        self.setAlignment(align)
        self.setReadOnly(read_only)

        self._min_height: int = self.sizeHint().height()
        self._rescalable: bool = rescale
        self.rescale = rescale

        if text:
            self.setText(text)

        if text_changed:
            _ = self.textChanged.connect(text_changed)

        if tooltip:
            self.setToolTip(tooltip)

    @property
    def rescale(self) -> bool:
        """[bool][] &mdash; Get/set whether the font size rescales based on the widget size."""
        return self._rescalable

    @rescale.setter
    def rescale(self, enabled: bool) -> None:
        self._rescalable = bool(enabled)
        if enabled:
            self.setMinimumHeight(self._min_height)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
            _ = self.textChanged.connect(self._rescale_font)
        else:
            self.setMinimumHeight(0)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

            # maybe the slot was not connected
            with suppress(RuntimeError, TypeError), warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                _ = self.textChanged.disconnect(self._rescale_font)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Override [resizeEvent][QtWidgets.QWidget.resizeEvent] to change the font size."""
        super().resizeEvent(event)
        if self._rescalable:
            self._rescale_font(self.text())

    def _rescale_font(self, text: str) -> None:
        """Rescale the font size based on the size of the widget.

        Args:
            text: The text from a textChanged() signal or from the setText() method.
        """
        if not text:
            return

        # Newton's method seems to be better than QFontMetrics
        self._rescale_font_newton(text)
        # self._rescale_font_metrics(text)  # noqa: ERA001

    def _rescale_font_metrics(self, text: str) -> None:
        """This algorithm uses QFontMetrics to calculate the scaling factor."""
        size = self.size()
        font = self.font()
        rect = QtGui.QFontMetrics(font).boundingRect(text)
        factor_w = size.width() / max(1.0, rect.width())
        factor_h = size.height() / max(1.0, rect.height())
        factor = min(factor_w, factor_h)
        font.setPointSizeF(font.pointSizeF() * factor - 1.0)
        self.setFont(font)

    def _rescale_font_newton(self, text: str) -> None:
        """This algorithm uses Newton's method to find the optimal font size."""
        font = self.font()
        size = self.size()
        width, height = size.width(), size.height()

        fm = QtGui.QFontMetrics

        def f(x: float) -> float:
            x = max(0.1, x)
            font.setPointSizeF(x)
            br = fm(font).boundingRect(text)
            return float(min(width - br.width(), height - br.height()))

        def f_prime(x: float, dx: float) -> float:
            x = max(x, dx + 1.0)
            return (f(x + dx) - f(x - dx)) / dx

        current = font.pointSizeF()
        step = 1.0
        for _ in range(100):
            previous = current
            df = f_prime(current, step)
            if df == 0:
                step *= 2.0
                continue
            current -= f(current) / df
            current = max(2.0, current)
            delta = abs(previous - current) / current
            if delta < 0.01:  # noqa: PLR2004
                break
        font.setPointSizeF(max(0.1, current - 2.0))  # under fill the widget
        self.setFont(font)
