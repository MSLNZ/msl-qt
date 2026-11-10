"""A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size."""

from __future__ import annotations

import warnings
from contextlib import suppress
from typing import TYPE_CHECKING

from msl.qt._qt import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    from typing import Callable


class LineEdit(QtWidgets.QLineEdit):
    """A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size."""

    def __init__(
        self,
        *,
        align: QtCore.Qt.AlignmentFlag | None = None,
        read_only: bool = False,
        rescale: bool = False,
        text: str | None = None,
        text_changed: Callable[[str], None] | None = None,
        tooltip: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A [QLineEdit][QtWidgets.QLineEdit] that can rescale the font size based on the widget size.

        Args:
            align: How to align the text. Default is `AlignLeft`.
            read_only: Whether the displayed text is read only.
            rescale: Whether the displayed text should rescale when the size of the
                [QLineEdit][QtWidgets.QLineEdit] changes.
            text: The initial text to display.
            text_changed: A callable function to use as a slot for the
                [textChanged][QtWidgets.QLineEdit.textChanged] signal.
            tooltip: The tooltip to display for the line edit.
            parent: The parent widget.
        """
        super().__init__(parent=parent)
        self.setAlignment(align or QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setReadOnly(read_only)

        self._min_height: int = self.sizeHint().height()
        self._rescalable: bool = rescale
        self.set_rescalable(rescale)

        if text:
            self.setText(text)

        if text_changed:
            _ = self.textChanged.connect(text_changed)

        if tooltip:
            self.setToolTip(tooltip)

    def set_rescalable(self, enable: bool) -> None:  # noqa: FBT001
        """Whether to enable or disable the font rescaling as the size of [QLineEdit][QtWidgets.QLineEdit] changes.

        Args:
            enable: Whether to enable or disable the font rescaling.
        """
        self._rescalable = bool(enable)
        if enable:
            self.setMinimumHeight(self._min_height)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
            _ = self.textChanged.connect(self._rescale_font)
        else:
            self.setMinimumHeight(0)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

            # the slot was not connected
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
        font.setPointSizeF(current - 1.0)  # under fill the widget
        self.setFont(font)
