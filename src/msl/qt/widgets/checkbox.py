"""A [QCheckBox][QtWidgets.QCheckBox] widget.

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('CheckBox')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8<-- "src/msl/examples/qt/checkbox.py"
        ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt.binding import QtWidgets, binding

if TYPE_CHECKING:
    from typing import Callable

    from msl.qt.binding import QtCore


class CheckBox(QtWidgets.QCheckBox):
    """A [QCheckBox][QtWidgets.QCheckBox] widget."""

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
        """A [QCheckBox][QtWidgets.QCheckBox] widget.

        This widget simply provides more configuration options in its constructor
        than its parent [QCheckBox][QtWidgets.QCheckBox] does.

        Args:
            checkable: Whether the checkbox can be (un)checked.
            initial: The initial checked state of the checkbox.
            state_changed: A callable function to use as a [Slot][msl.qt.binding.Slot]
                for the [checkStateChanged][QtWidgets.QCheckBox.checkStateChanged]
                [Signal][msl.qt.binding.Signal]. The function receives the
                [CheckState][QtCore.Qt.CheckState] from the [Signal][msl.qt.binding.Signal].
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
            if binding.qt_version_info[:2] >= (6, 7):
                _ = self.checkStateChanged.connect(state_changed)
            else:
                _ = self.stateChanged.connect(state_changed)

        if tooltip:
            self.setToolTip(tooltip)
