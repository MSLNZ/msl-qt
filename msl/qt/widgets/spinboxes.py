"""
Custom :class:`QtWidgets.QDoubleSpinBox` and :class:`QtWidgets.QSpinBox` classes.

In situations where the value of the spinbox is used to represent the position/value
of equipment in the laboratory one typically does not want to connect the
:meth:`~QtWidgets.QDoubleSpinBox.valueChanged` signal of the spinbox to change the
value of the equipment because each numeric key press would be sent to the equipment.
For example, if you wanted to set the position/value of the equipment to 1234 then
typing the value 1234 in the spinbox would send:

* 1 :math:`\\rightarrow` set the value of the equipment to be 1
* 12 :math:`\\rightarrow` set the value of the equipment to be 12
* 123 :math:`\\rightarrow` set the value of the equipment to be 123
* 1234 :math:`\\rightarrow` set the value of the equipment to be 1234

These custom :class:`QAbstractSpinBox` subclasses will emit the
:meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal when any of the
following events occur:

* the spinbox loses focus
* the Enter key is pressed
* the Up, Down, PageUp or PageDown keys are pressed
* the Increment and Decrement buttons are clicked
"""
from enum import Enum

from ..convert import (
    si_to_number,
    number_to_si,
)
from .. import (
    QtWidgets,
    QtGui,
    binding,
)


class SpinBox(QtWidgets.QSpinBox):

    def __init__(self, *, parent=None, value=0, minimum=0, maximum=100, step=1,
                 unit='', tooltip='', value_changed=None, editing_finished=None):
        """A :class:`~QtWidgets.QSpinBox` that emits
        :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` after a
        :meth:`~QtWidgets.QAbstractSpinBox.stepBy` signal.

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        value : :class:`int`, optional
            The initial value.
        minimum : :class:`int`, optional
            The minimum value.
        maximum : :class:`int`, optional
            The maximum value.
        step : :class:`int`, optional
            The step-by size.
        unit : :class:`str` or :class:`enum.Enum`, optional
            The text to display after the value.
        tooltip : :class:`str`, optional
            The tooltip to use for the :class:`SpinBox`.
        value_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QSpinBox.valueChanged` signal.
        editing_finished
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super(SpinBox, self).__init__(parent=parent)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.setSingleStep(step)
        self.setToolTip(tooltip)
        if isinstance(unit, Enum):
            self.setSuffix(unit.value)
        else:
            self.setSuffix(unit)
        if value_changed:
            self.valueChanged.connect(value_changed)
        if editing_finished:
            self.editingFinished.connect(editing_finished)

    def stepBy(self, steps):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.stepBy`.

         Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
         key presses to update the value of the spinbox and then emit the
         :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super(SpinBox, self).stepBy(steps)
        self.editingFinished.emit()


class DoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, *, parent=None, value=0, minimum=0, maximum=100,
                 step=1, decimals=2, use_si_prefix=False, unit='', tooltip='',
                 value_changed=None, editing_finished=None):
        """A :class:`~QtWidgets.QDoubleSpinBox` that emits
        :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` after a
        :meth:`~QtWidgets.QAbstractSpinBox.stepBy` signal.

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        value : :class:`float`, optional
            The initial value.
        minimum : :class:`float`, optional
            The minimum value.
        maximum : :class:`float`, optional
            The maximum value.
        step : :class:`float`, optional
            The step-by size.
        decimals : :class:`int`, optional
            The number of digits after the decimal place to use to show the value.
        use_si_prefix : :class:`bool`, optional
            Whether to use an SI prefix to represent the number, e.g. a value of
            1.2e-9 would be represented as '1.2 n'
        unit : :class:`str` or :class:`enum.Enum`, optional
            The text to display after the value.
        tooltip : :class:`str`, optional
            The tooltip to use for the :class:`DoubleSpinBox`.
        value_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QDoubleSpinBox.valueChanged` signal.
        editing_finished
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super(DoubleSpinBox, self).__init__(parent=parent)
        self._using_pyside = binding.name.startswith('PySide')
        if use_si_prefix:
            self._validator = _SIPrefixValidator()
            si_prefix_limit = 0.99999999999999e27
            if minimum < -si_prefix_limit:
                minimum = -si_prefix_limit
            if maximum > si_prefix_limit:
                maximum = si_prefix_limit
        else:
            self._validator = None
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.setSingleStep(step)
        self.setDecimals(decimals)
        self.setToolTip(tooltip)
        if isinstance(unit, Enum):
            self.setSuffix(unit.value)
        else:
            self.setSuffix(unit)
        if value_changed:
            self.valueChanged.connect(value_changed)
        if editing_finished:
            self.editingFinished.connect(editing_finished)

    def validate(self, text, position):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.validate`."""
        if self._validator is None:
            return super(DoubleSpinBox, self).validate(text, position)
        # Don't pass self.cleanText() to the validator because it does not always return
        # what is expected. For example, if `text`='0.12f3' then self.cleanText() returns
        # '0.12f' (which has removed the 3 at the end) and this causes the validator to
        # return Acceptable and the displayed text in the DoubleSpinBox then becomes
        # '0.12f3' which is Invalid and one can no longer edit the value in the
        # DoubleSpinBox. It is okay to use self.cleanText() in the methods self.fixup(),
        # self.valueFromText() and self.stepBy()
        text = text.rstrip(self.suffix()).lstrip(self.prefix())
        state = self._validator.validate(text, position - len(self.prefix()))
        if self._using_pyside:
            return state
        # PyQt expects Tuple[QValidator.State, str, int] to be returned
        return state, text, position

    def fixup(self, text):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.fixup`."""
        if self._validator is None:
            return super(DoubleSpinBox, self).fixup(text)
        return self._validator.fixup(self.cleanText())

    def valueFromText(self, text):
        """Overrides :meth:`QtWidgets.QDoubleSpinBox.valueFromText`."""
        if self._validator is None:
            return super(DoubleSpinBox, self).valueFromText(text)
        return si_to_number(self.cleanText())

    def textFromValue(self, value):
        """Overrides :meth:`QtWidgets.QDoubleSpinBox.textFromValue`."""
        if self._validator is None:
            return super(DoubleSpinBox, self).textFromValue(value)
        val, si_prefix = number_to_si(value)
        return '{value:.{decimals}f} {si_prefix}'.format(value=val, decimals=self.decimals(), si_prefix=si_prefix)

    def setValue(self, value):
        """Overrides :meth:`QtWidgets.QDoubleSpinBox.setValue`."""
        if self._validator is None:
            super(DoubleSpinBox, self).setValue(value)
        else:
            coerced = max(min(si_to_number(str(value)), self.maximum()), self.minimum())
            self.lineEdit().setText(self.textFromValue(coerced))

    def stepBy(self, steps):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.stepBy`.

         Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
         key presses to update the value of the spinbox and then emit the
         :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.

         If an SI prefix is enabled then uses a step size that is rescaled
         for the current value.
        """
        if self._validator is None:
            super(DoubleSpinBox, self).stepBy(steps)
        else:
            number = si_to_number(self.cleanText())
            coerced = max(min(number, self.maximum()), self.minimum())
            _, si_prefix = number_to_si(coerced)
            value = number + si_to_number(str(steps * self.singleStep()) + si_prefix)
            self.setValue(value)
        self.editingFinished.emit()


class _SIPrefixValidator(QtGui.QValidator):
    """Validate text that may or may not contain an SI prefix for the :class:`DoubleSpinBox`."""

    def validate(self, string, position):
        """Overrides :meth:`QtGui.QValidator.validate`."""
        if not string:
            return self.State.Intermediate

        if len(string) == 1:
            if string.isdigit():
                return self.State.Acceptable
            if string in '+-.':
                return self.State.Intermediate
            return self.State.Invalid

        try:
            si_to_number(string)
        except ValueError:
            pass
        else:
            return self.State.Acceptable

        string_lower = string.lower()

        # can only have one '.' and it must be before an 'e'
        if string[position-1] == '.':
            if (string.count('.') == 1) and ('e' not in string_lower[:position-1]):
                return self.State.Intermediate
            return self.State.Invalid

        # can only have one 'e' and everything before it must be in 0123456789 or +-.
        if string_lower[position-1] == 'e':
            if string_lower.count('e') == 1 and all(c.isdigit() or c in '+-.' for c in string_lower[:position-1]):
                return self.State.Intermediate
            return self.State.Invalid

        # a '+' or '-' symbol can only follow an 'e'
        if string[position-1] in '+-':
            if string_lower[position-2] == 'e':
                return self.State.Intermediate
            return self.State.Invalid

        return self.State.Invalid

    def fixup(self, text):
        """Overrides :meth:`QtGui.QValidator.fixup`."""
        try:
            return '{} {}'.format(*number_to_si(si_to_number(text)))
        except ValueError:
            return ''
