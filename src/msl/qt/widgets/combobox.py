"""A [QComboBox][QtWidgets.QComboBox] widget.

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('ComboBox')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8<-- "src/msl/examples/qt/combobox.py"
        ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt.binding import QtGui, QtWidgets

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Callable


class ComboBox(QtWidgets.QComboBox):
    """A [QComboBox][QtWidgets.QComboBox]."""

    def __init__(  # noqa: C901, PLR0912
        self,
        *,
        items: str | Sequence[str] | dict[str, QtGui.QIcon | object | tuple[QtGui.QIcon, object]] | None = None,
        initial: int | str | None = None,
        index_changed: Callable[[int], Any] | None = None,
        text_changed: Callable[[str], Any] | None = None,
        tooltip: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A [QComboBox][QtWidgets.QComboBox].

        This widget simply provides more configuration options in its constructor
        than its parent [QComboBox][QtWidgets.QComboBox] does.

        Args:
            items: The item(s) to add to the combobox. If a string, adds the single item.
                If a sequence, adds all items. If a [dict][], then the keys are the text
                of each item and the values can either be a [QIcon][QtGui.QIcon] to use as
                the icon, any object to use as the `userData` parameter or an
                `(icon, userData)` [tuple][].
            initial: The index or text of the item to initially display. This value is
                set before the [Slot][msl.qt.binding.Slot]s are connected.
            index_changed: A callable function to use as a [Slot][msl.qt.binding.Slot]
                for the [currentIndexChanged][QtWidgets.QComboBox.currentIndexChanged]
                [Signal][msl.qt.binding.Signal]. The function receives the index value
                (as an [int][]) that is selected.
            text_changed: A callable function to use as a [Slot][msl.qt.binding.Slot]
                for the [currentTextChanged][QtWidgets.QComboBox.currentTextChanged]
                [Signal][msl.qt.binding.Signal]. The function receives the text value
                (as a [str][]) that is selected.
            tooltip: The tooltip to display for the combobox.
            parent: The parent widget.
        """
        super().__init__(parent=parent)

        if items:
            if isinstance(items, str):
                self.addItem(items)
            elif isinstance(items, (list, tuple)):
                self.addItems(items)
            elif isinstance(items, dict):
                for key, value in items.items():
                    if isinstance(value, QtGui.QIcon):
                        self.addItem(value, key)
                    elif isinstance(value, (list, tuple)):
                        icon, data = None, None
                        for item in value:  # pyright: ignore[reportUnknownVariableType]
                            if isinstance(item, QtGui.QIcon):
                                icon = item
                            else:
                                data = item  # pyright: ignore[reportUnknownVariableType]
                        if icon:
                            self.addItem(icon, key, userData=data)
                        else:
                            self.addItem(key, userData=data)
                    else:
                        self.addItem(key, userData=value)
            else:
                msg = f"Unsupported type {type(items)} for 'items' parameter"
                raise TypeError(msg)

        if initial:
            if isinstance(initial, int):
                self.setCurrentIndex(initial)
            else:
                self.setCurrentText(initial)

        if index_changed:
            _ = self.currentIndexChanged.connect(index_changed)

        if text_changed:
            _ = self.currentTextChanged.connect(text_changed)

        if tooltip:
            self.setToolTip(tooltip)
