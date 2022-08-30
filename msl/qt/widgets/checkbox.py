"""
A :class:`~QtWidgets.QCheckBox` with more options in the constructor.
"""
from msl.qt import QtWidgets


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, *, checkable=True, initial=False, state_changed=None,
                 text=None, tooltip=None, parent=None):
        """A :class:`~QtWidgets.QCheckBox` with more options in the constructor.

        Parameters
        ----------
        checkable : :class:`bool`, optional
            Whether the checkbox can be (un)checked.
        initial : :class:`bool` or :attr:`Qt.CheckState`, optional
            The initial state of the checkbox.
        state_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QCheckBox.stateChanged` signal.
        text : :class:`str`, optional
            The text to display next to the checkbox.
        tooltip : :class:`str`, optional
            The tooltip to display for the checkbox.
        parent : :class:`~QtWidgets.QWidget`, optional
            The parent widget.
        """
        super().__init__(text=text, parent=parent)
        if isinstance(initial, bool):
            self.setChecked(initial)
        else:
            self.setCheckState(initial)

        self.setCheckable(checkable)

        if state_changed:
            self.stateChanged.connect(state_changed)

        if tooltip:
            self.setToolTip(tooltip)
