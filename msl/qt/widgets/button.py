"""
A :class:`~QtWidgets.QToolButton` to display text, an icon and a menu.
"""
from .. import (
    QtWidgets,
    QtCore,
    Qt,
    QtGui,
    io,
)


class Button(QtWidgets.QToolButton):

    def __init__(self, *, text=None, icon=None, icon_size=None, left_click=None,
                 right_click=None, is_text_under_icon=True, tooltip=None, parent=None):
        """A :class:`~QtWidgets.QToolButton` to display text, an icon and a menu.

        Parameters
        ----------
        text : :class:`str`, optional
            The text to display on the button.
        icon : :class:`object`, optional
            Any icon object that is supported by :func:`~msl.qt.io.get_icon`.
        icon_size : :class:`int`, :class:`float`, :class:`tuple` of :class:`int` or :class:`QtCore.QSize`, optional
            Rescale the icon to the specified `size`.
            If the value is :data:`None` then do not rescale the icon.
            If an :class:`int` then set the width and the height to be the `size` value.
            If a :class:`float` then a scaling factor.
            If a :class:`tuple` then the (width, height) values.
        left_click : :obj:`callable`, optional
            The function to be called for a mouse left-click event.
        right_click : :obj:`callable`, optional
            The function to be called for a mouse right-click event.
        is_text_under_icon : :class:`bool`, optional
            If displaying an icon and text then whether to place the text
            under, :data:`True`, or beside, :data:`False`, the icon.
        tooltip : :class:`str`, optional
            The tooltip to display for the button.
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        """
        super(Button, self).__init__(parent=parent)

        self._menu = None

        if text and icon:
            if is_text_under_icon:
                self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            else:
                self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.setText(text)
            self._set_icon(icon, icon_size)
        elif text and not icon:
            self.setToolButtonStyle(Qt.ToolButtonTextOnly)
            self.setText(text)
        elif not text and icon:
            self.setToolButtonStyle(Qt.ToolButtonIconOnly)
            self._set_icon(icon, icon_size)

        # the left-click event handler
        if left_click is not None:
            self.set_left_click(left_click)

        # setContextMenuPolicy allows for right-click events
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        if right_click is not None:
            self.set_right_click(right_click)

        if tooltip is not None:
            self.setToolTip(tooltip)

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

    def add_menu_item(self, *, text=None, triggered=None, icon=None, shortcut=None, tooltip=None):
        """Add a new item to the action menu.

        Parameters
        ----------
        text : :class:`str`, optional
            The text to display for this item.
        triggered : :obj:`callable`, optional
            The function to be called when this item is selected.
            If :data:`None` then the item is displayed but it is disabled.
        icon : :class:`object`, optional
            Any icon object that is supported by :func:`~msl.qt.io.get_icon`.
        shortcut : :class:`str`, optional
          The keyboard shortcut to use to select this item, e.g., ``'CTRL+A'``
        tooltip : :class:`str`, optional
          The tooltip to display for this item.
        """
        if self._menu is None:
            self._create_menu()
        action = QtWidgets.QAction(self)
        if triggered is not None:
            action.triggered.connect(triggered)
        else:
            action.setDisabled(True)
        if text is not None:
            action.setText(text)
        if shortcut is not None:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        if icon is not None:
            action.setIcon(io.get_icon(icon))
        if tooltip is not None:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        self._menu.addAction(action)

    def add_menu_separator(self):
        """Insert a separator between menu items."""
        if self._menu is None:
            self._create_menu()
        self._menu.addSeparator()

    def set_left_click(self, fcn):
        """The function to be called for a mouse left-click event.

        Parameters
        ----------
        fcn : :obj:`callable`
            The function to be called for a mouse left-click event.
        """
        self.clicked.connect(fcn)

    def set_right_click(self, fcn):
        """The function to be called for a mouse right-click event.

        Parameters
        ----------
        fcn : :obj:`callable`
            The function to be called for a mouse right-click event.
        """
        self.customContextMenuRequested.connect(fcn)

    def _create_menu(self):
        self._menu = ButtonMenu(self)
        self._menu.setToolTipsVisible(True)
        self.setMenu(self._menu)
        self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

    def _set_icon(self, icon, icon_size):
        icon = io.get_icon(icon)  # make sure that it's a QIcon
        if icon_size is not None:
            icon = io.rescale_icon(icon, icon_size)
            self.setIconSize(icon.size())
        elif icon.availableSizes():
            available = icon.availableSizes()[-1]
            if self.iconSize().width() < available.width() or \
                    self.iconSize().height() < available.height():
                self.setIconSize(available)
        self.setIcon(icon)


class ButtonMenu(QtWidgets.QMenu):
    """Display the :class:`QtWidgets.QMenu` underneath the :class:`Button`."""

    def showEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.showEvent`."""
        point = self.parent().mapToGlobal(QtCore.QPoint(0, 0))
        offset = self.parent().width() - self.width()
        self.move(point + QtCore.QPoint(offset, self.parent().height()))
        super(ButtonMenu, self).showEvent(event)
