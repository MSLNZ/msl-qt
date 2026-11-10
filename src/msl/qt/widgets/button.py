"""A [QToolButton][QtWidgets.QToolButton] to display text, an icon and a menu."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from msl.qt._qt import Qt, QtCore, QtGui, QtWidgets
from msl.qt.convert import rescale_icon, to_qicon

if TYPE_CHECKING:
    from typing import Callable

    from msl.qt.typing import Size


class Button(QtWidgets.QToolButton):
    """A custom [QToolButton][QtWidgets.QToolButton] to display text, an icon and a menu."""

    def __init__(
        self,
        *,
        text: str | None = None,
        icon: object = None,
        icon_size: Size | None = None,
        left_click: Callable[[], None] | None = None,
        right_click: Callable[[], None] | None = None,
        is_text_under_icon: bool = True,
        tooltip: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """A custom [QToolButton][QtWidgets.QToolButton] to display text, an icon and a menu.

        Args:
            text: The text to display on the button.
            icon: Any icon object that is supported by [to_qicon][msl.qt.convert.to_qicon].
            icon_size: Rescale the icon to the specified `size`.
                If the value is `None` then do not rescale the icon.
                If an [int][] then set the width and the height to be the `size` value.
                If a [float][] then a scaling factor.
                If a [tuple][] then the (width, height) values.
            left_click: The function to be called for a mouse left-click event.
            right_click: The function to be called for a mouse right-click event.
            is_text_under_icon: If displaying an icon and text then whether to place the text
                under (`True`) or beside (`False`) the icon.
            tooltip: The tooltip to display for the button.
            parent: The parent widget.
        """
        super().__init__(parent=parent)

        self._menu: _ButtonMenu | None = None

        if text and icon:
            if is_text_under_icon:
                self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            else:
                self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.setText(text)
            self._set_icon(icon, icon_size)
        elif text and not icon:
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            self.setText(text)
        elif not text and icon:
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            self._set_icon(icon, icon_size)

        # the left-click event handler
        if left_click is not None:
            self.set_left_click(left_click)

        # setContextMenuPolicy allows for right-click events
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        if right_click is not None:
            self.set_right_click(right_click)

        if tooltip is not None:
            self.setToolTip(tooltip)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)

    def add_menu_item(
        self,
        *,
        text: str | None = None,
        triggered: Callable[[], None] | None = None,
        icon: object | None = None,
        shortcut: str | None = None,
        tooltip: str | None = None,
    ) -> None:
        """Add a new item to the action menu.

        Args:
            text: The text to display for this item.
            triggered: The function to be called when this item is selected.
                If `None` then the item is displayed, but it is disabled.
            icon: Any icon object that is supported by [to_qicon][msl.qt.convert.to_qicon].
            shortcut: The keyboard shortcut to use to select this item, e.g., `"CTRL+A"`.
            tooltip: The tooltip to display for this item.
        """
        if self._menu is None:
            self._menu = self._create_menu()

        action = QtGui.QAction(self)
        if triggered is not None:
            _ = action.triggered.connect(triggered)
        else:
            action.setDisabled(True)
        if text is not None:
            action.setText(text)
        if shortcut is not None:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        if icon is not None:
            action.setIcon(to_qicon(icon))
        if tooltip is not None:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)

        self._menu.addAction(action)

    def add_menu_separator(self) -> None:
        """Insert a separator between menu items."""
        if self._menu is None:
            self._menu = self._create_menu()
        _ = self._menu.addSeparator()

    def set_left_click(self, fcn: Callable[[], None]) -> None:
        """The function to be called for a mouse left-click event.

        Args:
            fcn: The function to be called for a mouse left-click event.
        """
        _ = self.clicked.connect(fcn)

    def set_right_click(self, fcn: Callable[[], None]) -> None:
        """The function to be called for a mouse right-click event.

        Args:
            fcn: The function to be called for a mouse right-click event.
        """
        _ = self.customContextMenuRequested.connect(fcn)

    def _create_menu(self) -> _ButtonMenu:
        menu = _ButtonMenu(self)
        menu.setToolTipsVisible(True)
        self.setMenu(menu)
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        return menu

    def _set_icon(self, icon: object, icon_size: Size | None) -> None:
        icon = to_qicon(icon)  # make sure that it's a QIcon
        if icon_size is not None:
            pixmap = rescale_icon(icon, icon_size)
            self.setIconSize(pixmap.size())
        elif icon.availableSizes():
            style = self.style()
            metric = style.pixelMetric(style.PixelMetric.PM_ButtonIconSize)
            s = icon.availableSizes()[0]
            size = QtCore.QSize(max(s.width(), metric), max(s.height(), metric))
            if self.iconSize().width() < size.width() or self.iconSize().height() < size.height():
                self.setIconSize(size)
        self.setIcon(icon)


class _ButtonMenu(QtWidgets.QMenu):
    """Display the [QMenu][QtWidgets.QMenu] underneath the [Button][..Button]."""

    def showEvent(self, event: QtGui.QShowEvent) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: N802
        """Overrides `QtWidgets.QWidget.showEvent`."""
        parent = cast("Button", self.parent())
        point = parent.mapToGlobal(QtCore.QPoint(0, 0))
        offset = parent.width() - self.width()
        self.move(point + QtCore.QPoint(offset, parent.height()))
        super().showEvent(event)
