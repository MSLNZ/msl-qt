"""Custom [QDoubleSpinBox][QtWidgets.QDoubleSpinBox] and [QSpinBox][QtWidgets.QSpinBox] classes.

In situations where the value of the spinbox is used to represent the position/value
of equipment in the laboratory one typically does not want to connect the
[valueChanged][QtWidgets.QDoubleSpinBox.valueChanged] signal of the spinbox to change the
value of the equipment because each numeric key press would be sent to the equipment.
For example, if you wanted to set the position of a translation stage to 123 then
typing the value 123 in the spinbox would send three move commands to the equipment:

* 1 &mdash; move to position 1
* 12 &mdash; move to position 12
* 123 &mdash; move to position 123

These custom [QAbstractSpinBox][QtWidgets.QAbstractSpinBox] subclasses will emit the
[editingFinished][QtWidgets.QAbstractSpinBox.editingFinished] signal when any of the
following events occur:

* the spinbox loses focus
* the Enter key is pressed
* the Up, Down, PageUp or PageDown keys are pressed
* the Increment and Decrement buttons are clicked
"""

# cSpell: ignore pyside
from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt._qt import QtGui, QtWidgets
from msl.qt.convert import number_to_si, si_to_number

if TYPE_CHECKING:
    from typing import Callable


class SpinBox(QtWidgets.QSpinBox):
    """A [QSpinBox][QtWidgets.QSpinBox] to show an integer value."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        parent: QtWidgets.QWidget | None = None,
        value: int = 0,
        minimum: int = 0,
        maximum: int = 100,
        step: int = 1,
        unit: str | None = None,
        tooltip: str | None = None,
        value_changed: Callable[[int], None] | None = None,
        editing_finished: Callable[[], None] | None = None,
    ) -> None:
        """A [QSpinBox][QtWidgets.QSpinBox] to show an integer value.

        A [QSpinBox][QtWidgets.QSpinBox] that emits
        [editingFinished][QtWidgets.QAbstractSpinBox.editingFinished]
        after a [stepBy][QtWidgets.QAbstractSpinBox.stepBy] signal.

        Args:
            parent: The parent widget.
            value: The initial value.
            minimum: The minimum value.
            maximum: The maximum value.
            step: The step-by size.
            unit: The text to display after the value (i.e., the *unit* of the displayed value).
            tooltip: The text to use for the tooltip.
            value_changed: A callable function to use as a slot for the
                [valueChanged][QtWidgets.QSpinBox.valueChanged] signal.
            editing_finished: A callable function to use as a slot for the
                [editingFinished][QtWidgets.QAbstractSpinBox.editingFinished] signal.
        """
        super().__init__(parent=parent)
        self.setRange(minimum, maximum)
        self.setValue(value)
        self.setSingleStep(step)
        if tooltip:
            self.setToolTip(tooltip)
        if unit:
            self.setSuffix(unit)
        if value_changed:
            _ = self.valueChanged.connect(value_changed)
        if editing_finished:
            _ = self.editingFinished.connect(editing_finished)

    def stepBy(self, steps: int) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QAbstractSpinBox.stepBy`.

        Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
        key presses to update the value of the spinbox and then emit the
        `QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super().stepBy(steps)
        self.editingFinished.emit()


class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """A [QDoubleSpinBox][QtWidgets.QDoubleSpinBox] to show a float value."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        parent: QtWidgets.QWidget | None = None,
        value: float = 0,
        minimum: float = 0,
        maximum: float = 100,
        step: float = 1,
        decimals: int = 2,
        use_si_prefix: bool = False,
        unit: str | None = None,
        tooltip: str | None = None,
        value_changed: Callable[[float], None] | None = None,
        editing_finished: Callable[[], None] | None = None,
    ) -> None:
        """A [QDoubleSpinBox][QtWidgets.QDoubleSpinBox] to show a float value.

        A [QDoubleSpinBox][QtWidgets.QDoubleSpinBox] that emits
        [editingFinished][QtWidgets.QAbstractSpinBox.editingFinished] after a
        [stepBy][QtWidgets.QAbstractSpinBox.stepBy] signal.

        Args:
            parent: The parent widget.
            value: The initial value.
            minimum: The minimum value.
            maximum: The maximum value.
            step: The step-by size.
            decimals: The number of digits after the decimal place to use to show the value.
            use_si_prefix: Whether to use an SI prefix to represent the number,
                e.g., a value of `0.00431` would be represented as `4.31 m`.
            unit: The text to display after the value (i.e., the *unit* of the displayed value).
            tooltip: The text to use for the tooltip.
            value_changed: A callable function to use as a slot for the
                [valueChanged][QtWidgets.QDoubleSpinBox.valueChanged] signal.
            editing_finished: A callable function to use as a slot for the
                [editingFinished][QtWidgets.QAbstractSpinBox.editingFinished] signal.
        """
        super().__init__(parent=parent)
        if use_si_prefix:
            self._validator: _SIPrefixValidator | None = _SIPrefixValidator()
            si_prefix_limit = 0.99999999999999e27
            minimum = max(minimum, -si_prefix_limit)
            maximum = min(maximum, si_prefix_limit)
        else:
            self._validator = None
        self.setDecimals(decimals)  # must come before setValue
        self.setSingleStep(step)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        if tooltip:
            self.setToolTip(tooltip)
        if unit:
            self.setSuffix(unit)
        if value_changed:
            _ = self.valueChanged.connect(value_changed)
        if editing_finished:
            _ = self.editingFinished.connect(editing_finished)

    def validate(self, text: str, position: int) -> tuple[QtGui.QValidator.State, str, int]:  # pyright: ignore[reportImplicitOverride]
        """Overrides `QtWidgets.QAbstractSpinBox.validate`."""
        if self._validator is None:
            return super().validate(text, position)

        # Don't pass self.cleanText() to the validator because it does not always return what is
        # expected. For example, if `text`='0.12f3' then self.cleanText() returns '0.12f'
        # (which has removed the 3 at the end) and this causes the validator to return Acceptable
        # and the displayed text in the DoubleSpinBox then becomes '0.12f3' which is Invalid and
        # one can no longer edit the value in the DoubleSpinBox. It is okay to use self.cleanText()
        # in the methods self.fixup(), self.valueFromText() and self.stepBy()
        text = text.rstrip(self.suffix()).lstrip(self.prefix())
        state = self._validator.validate(text, position - len(self.prefix()))
        return state, text, position

    def fixup(self, text: str) -> str:  # pyright: ignore[reportImplicitOverride]
        """Overrides `QtWidgets.QAbstractSpinBox.fixup`."""
        if self._validator is None:
            return super().fixup(text)
        return self._validator.fixup(self.cleanText())

    def valueFromText(self, text: str) -> float:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QDoubleSpinBox.valueFromText`."""
        if self._validator is None:
            return super().valueFromText(text)
        return si_to_number(self.cleanText())

    def textFromValue(self, value: float) -> str:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QDoubleSpinBox.textFromValue`."""
        if self._validator is None:
            return super().textFromValue(value)
        val, si_prefix = number_to_si(value)
        return f"{val:.{self.decimals()}f} {si_prefix}"

    def setValue(self, value: float) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QDoubleSpinBox.setValue`."""
        if self._validator is None:
            super().setValue(value)
        else:
            coerced = max(min(si_to_number(str(value)), self.maximum()), self.minimum())
            self.lineEdit().setText(self.textFromValue(coerced))

    def stepBy(self, steps: int) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QAbstractSpinBox.stepBy`.

        Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
        key presses to update the value of the spinbox and then emit the
        `QtWidgets.QAbstractSpinBox.editingFinished` signal.

        If an SI prefix is enabled then uses a step size that is rescaled
        for the current value.
        """
        if self._validator is None:
            super().stepBy(steps)
        else:
            number = si_to_number(self.cleanText())
            coerced = max(min(number, self.maximum()), self.minimum())
            _, si_prefix = number_to_si(coerced)
            value = number + si_to_number(str(steps * self.singleStep()) + si_prefix)
            self.setValue(value)
        self.editingFinished.emit()


class _SIPrefixValidator(QtGui.QValidator):
    """Validate text that may or may not contain an SI prefix for the `DoubleSpinBox`."""

    def validate(self, string: str, position: int) -> QtGui.QValidator.State:  # pyright: ignore[reportImplicitOverride]  # noqa: C901, PLR0911
        """Overrides `QtGui.QValidator.validate`."""
        if not string:
            return self.State.Intermediate

        if len(string) == 1:
            if string.isdigit():
                return self.State.Acceptable
            if string in "+-.":
                return self.State.Intermediate
            return self.State.Invalid

        try:
            _ = si_to_number(string)
        except ValueError:
            pass
        else:
            return self.State.Acceptable

        string_lower = string.lower()

        # can only have one '.' and it must be before an 'e'
        if string[position - 1] == ".":
            if (string.count(".") == 1) and ("e" not in string_lower[: position - 1]):
                return self.State.Intermediate
            return self.State.Invalid

        # can only have one 'e' and everything before it must be in 0123456789 or +-.
        if string_lower[position - 1] == "e":
            if string_lower.count("e") == 1 and all(c.isdigit() or c in "+-." for c in string_lower[: position - 1]):
                return self.State.Intermediate
            return self.State.Invalid

        # a '+' or '-' symbol can only follow an 'e'
        if string[position - 1] in "+-":
            if string_lower[position - 2] == "e":
                return self.State.Intermediate
            return self.State.Invalid

        return self.State.Invalid

    def fixup(self, text: str) -> str:  # pyright: ignore[reportImplicitOverride]
        """Overrides `QtGui.QValidator.fixup`."""
        try:
            number, si = number_to_si(si_to_number(text))
        except ValueError:
            return ""
        else:
            return f"{number} {si}"
