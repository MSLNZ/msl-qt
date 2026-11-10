"""A [QComboBox][QtWidgets.QComboBox] widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from msl.qt._qt import QtGui, QtWidgets

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Callable


class ComboBox(QtWidgets.QComboBox):
    """A [QComboBox][QtWidgets.QComboBox]."""

    def __init__(  # noqa: C901, PLR0912
        self,
        *,
        items: str | Sequence[str] | dict[str, QtGui.QIcon | object | tuple[QtGui.QIcon, object]] | None = None,
        initial: int | str | None = None,
        index_changed: Callable[[int], None] | None = None,
        text_changed: Callable[[str], None] | None = None,
        tooltip: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A [QComboBox][QtWidgets.QComboBox].

        Args:
            items: The item(s) to add to the combobox. If a string, adds the single item.
                If a sequence, adds all items. If a [dict][], then the keys are the text
                of each item and the values can either be a [QIcon][QtGui.QIcon] to use as
                the icon, any object to use as the `userData` parameter or an `(icon, userData)`
                [tuple][].
            initial: The index or text of the item to initially display. This value is set
                before the slots are registered.
            index_changed: A callable function to use as a slot for the
                [currentIndexChanged][QtWidgets.QComboBox.currentIndexChanged] signal.
            text_changed: A callable function to use as a slot for the
                [currentTextChanged][QtWidgets.QComboBox.currentTextChanged] signal.
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
