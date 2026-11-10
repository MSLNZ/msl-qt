"""A [QCheckBox][QtWidgets.QCheckBox] widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt._qt import QtWidgets

if TYPE_CHECKING:
    from typing import Callable

    from msl.qt._qt import QtCore


class CheckBox(QtWidgets.QCheckBox):
    """A [QCheckBox][QtWidgets.QCheckBox]."""

    def __init__(
        self,
        *,
        checkable: bool = True,
        initial: bool | QtCore.Qt.CheckState = False,
        state_changed: Callable[[QtCore.Qt.CheckState], None] | None = None,
        text: str | None = None,
        tooltip: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A [QCheckBox][QtWidgets.QCheckBox].

        Args:
            checkable: Whether the checkbox can be (un)checked.
            initial: The initial checked state of the checkbox.
            state_changed: A callable function to use as a slot for the
                [stateChanged][QtWidgets.QCheckBox.stateChanged] signal.
            text: The text to display next to the checkbox.
            tooltip: The tooltip to display for the checkbox.
            parent: The parent widget.
        """
        super().__init__(text or "", parent=parent)

        if isinstance(initial, bool):
            self.setChecked(initial)
        else:
            self.setCheckState(initial)

        self.setCheckable(checkable)

        if state_changed:
            _ = self.checkStateChanged.connect(state_changed)

        if tooltip:
            self.setToolTip(tooltip)
