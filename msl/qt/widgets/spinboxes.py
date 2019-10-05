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
from .. import QtWidgets


class DoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, *, parent=None, minimum=0, maximum=100, step=1, decimals=2, tooltip=None):
        """A :class:`~QtWidgets.QDoubleSpinBox` that emits
        :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` after a
        :meth:`~QtWidgets.QAbstractSpinBox.stepBy` signal.

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        minimum : :class:`float`, optional
            The minimum value.
        maximum : :class:`float`, optional
            The maximum value.
        step : :class:`float`, optional
            The step-by size.
        decimals : :class:`int`, optional
            The number of digits after the decimal place to use to show the value.
        tooltip : :class:`str`, optional
            The tooltip to use for the :class:`DoubleSpinBox`.
        """
        super(DoubleSpinBox, self).__init__(parent=parent)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSingleStep(step)
        self.setDecimals(decimals)
        if tooltip:
            self.setToolTip(tooltip)

    def stepBy(self, step):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.stepBy`.

         Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
         key presses to update the value of the spinbox and then emit the
         :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super(DoubleSpinBox, self).stepBy(step)
        self.editingFinished.emit()


class SpinBox(QtWidgets.QSpinBox):

    def __init__(self, *, parent=None, minimum=0, maximum=100, step=1, tooltip=None):
        """A :class:`~QtWidgets.QSpinBox` that emits
        :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` after a
        :meth:`~QtWidgets.QAbstractSpinBox.stepBy` signal.

        Parameters
        ----------
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        minimum : :class:`int`, optional
            The minimum value.
        maximum : :class:`int`, optional
            The maximum value.
        step : :class:`int`, optional
            The step-by size.
        tooltip : :class:`str`, optional
            The tooltip to use for the :class:`SpinBox`.
        """
        super(SpinBox, self).__init__(parent=parent)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSingleStep(step)
        if tooltip:
            self.setToolTip(tooltip)

    def stepBy(self, step):
        """Overrides :meth:`QtWidgets.QAbstractSpinBox.stepBy`.

         Allows Increment/Decrement button clicks and Up/Down/PageUp/PageDown
         key presses to update the value of the spinbox and then emit the
         :meth:`~QtWidgets.QAbstractSpinBox.editingFinished` signal.
        """
        super(SpinBox, self).stepBy(step)
        self.editingFinished.emit()
