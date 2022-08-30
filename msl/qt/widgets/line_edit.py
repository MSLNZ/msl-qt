"""
A :class:`~QtWidgets.QLineEdit` that can rescale the font size based on the
size of widget.
"""
from msl.qt import Qt
from msl.qt import QtGui
from msl.qt import QtWidgets


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, *, align=None, read_only=False, rescale=False,
                 text=None, text_changed=None, tooltip=None, parent=None):
        """A :class:`~QtWidgets.QLineEdit` that can rescale the font size based
        on the size of widget.

        Parameters
        ----------
        align : :attr:`Qt.AlignmentFlag`, optional
            How to align the text. Default is `Qt.AlignLeft`.
        read_only : :class:`bool`, optional
            Whether the displayed text is read only.
        rescale : :class:`bool`, optional
            Whether the displayed text should rescale when the size of the
            :class:`~QtWidgets.QLineEdit` changes.
        text : :class:`str`, optional
            The initial text to display.
        text_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QLineEdit.textChanged` signal.
        tooltip : :class:`str`, optional
            The tooltip to display for the line edit.
        parent : :class:`~QtWidgets.QWidget`, optional
            The parent widget.
        """
        super().__init__(parent=parent)
        self.setAlignment(align or Qt.AlignLeft)
        self.setReadOnly(read_only)

        self._min_height = self.sizeHint().height()
        self._rescalable = rescale
        self.set_rescalable(rescale)

        if text:
            self.setText(text)

        if text_changed:
            self.textChanged.connect(text_changed)

        if tooltip:
            self.setToolTip(tooltip)

    def set_rescalable(self, enable):
        """Whether to enable or disable the font rescaling as the size of
        the :class:`~QtWidgets.QLineEdit` changes.

        Parameters
        ----------
        enable : :class:`bool`
            Whether to enable or disable the font rescaling.
        """
        self._rescalable = bool(enable)
        if enable:
            self.setMinimumHeight(self._min_height)
            self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                               QtWidgets.QSizePolicy.Ignored)
            self.textChanged.connect(self._rescale_font)
        else:
            self.setMinimumHeight(0)
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Fixed)
            try:
                self.textChanged.disconnect(self._rescale_font)
            except RuntimeError:
                # the slot was not connected
                pass

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Override :meth:`QtWidgets.QWidget.resizeEvent` to change the font size."""
        super().resizeEvent(event)
        if self._rescalable:
            self._rescale_font(self.text())

    def _rescale_font(self, text) -> None:
        """Rescale the font size based on the size of the widget.

        Parameters
        ----------
        text : str
            The text from a textChanged() signal or from the setText() method.
        """
        if not text:
            return

        # Newton's method seems to be better than QFontMetrics
        self._rescale_font_newton(text)
        # self._rescale_font_metrics(text)

    def _rescale_font_metrics(self, text) -> None:
        """This algorithm uses QFontMetrics to calculate the scaling factor."""
        size = self.size()
        font = self.font()
        rect = QtGui.QFontMetrics(font).boundingRect(text)
        factor_w = size.width() / max(1.0, rect.width())
        factor_h = size.height() / max(1.0, rect.height())
        factor = min(factor_w, factor_h)
        font.setPointSizeF(font.pointSizeF() * factor - 1.0)
        self.setFont(font)

    def _rescale_font_newton(self, text) -> None:
        """This algorithm uses Newton's method to find the optimal font size."""
        font = self.font()
        size = self.size()
        width, height = size.width(), size.height()

        fm = QtGui.QFontMetrics

        def f(x):
            font.setPointSizeF(x)
            br = fm(font).boundingRect(text)
            return float(min(width - br.width(), height - br.height()))

        def fprime(x, dx):
            x = max(x, dx + 1.0)
            return (f(x + dx) - f(x - dx)) / dx

        current = font.pointSizeF()
        step = 1.0
        for i in range(100):
            previous = current
            df = fprime(current, step)
            if df == 0:
                step *= 2.0
                continue
            current -= f(current) / df
            current = max(2.0, current)
            delta = abs(previous - current) / current
            if delta < 0.01:  # within 1% of target
                break
        font.setPointSizeF(current - 1.0)  # under fill the widget
        self.setFont(font)
