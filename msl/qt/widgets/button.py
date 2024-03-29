"""
A :class:`~QtWidgets.QToolButton` to display text, an icon and a menu.
"""
from .. import Qt
from .. import QtCore
from .. import QtGui
from .. import QtWidgets
from .. import convert


class Button(QtWidgets.QToolButton):

    def __init__(self, *, text=None, icon=None, icon_size=None, left_click=None,
                 right_click=None, is_text_under_icon=True, tooltip=None, parent=None):
        """A :class:`~QtWidgets.QToolButton` to display text, an icon and a menu.

        Parameters
        ----------
        text : :class:`str`, optional
            The text to display on the button.
        icon : :class:`object`, optional
            Any icon object that is supported by :func:`~.convert.to_qicon`.
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

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                           QtWidgets.QSizePolicy.Policy.Fixed)

    def add_menu_item(self, *, text=None, triggered=None, icon=None, shortcut=None, tooltip=None):
        """Add a new item to the action menu.

        Parameters
        ----------
        text : :class:`str`, optional
            The text to display for this item.
        triggered : :obj:`callable`, optional
            The function to be called when this item is selected.
            If :data:`None` then the item is displayed, but it is disabled.
        icon : :class:`object`, optional
            Any icon object that is supported by :func:`~.convert.to_qicon`.
        shortcut : :class:`str`, optional
          The keyboard shortcut to use to select this item, e.g., ``'CTRL+A'``
        tooltip : :class:`str`, optional
          The tooltip to display for this item.
        """
        if self._menu is None:
            self._create_menu()
        action = QtGui.QAction(self)
        if triggered is not None:
            action.triggered.connect(triggered)  # noqa: QAction.triggered
        else:
            action.setDisabled(True)
        if text is not None:
            action.setText(text)
        if shortcut is not None:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        if icon is not None:
            action.setIcon(convert.to_qicon(icon))
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
        self.clicked.connect(fcn)  # noqa: QToolButton.clicked

    def set_right_click(self, fcn):
        """The function to be called for a mouse right-click event.

        Parameters
        ----------
        fcn : :obj:`callable`
            The function to be called for a mouse right-click event.
        """
        self.customContextMenuRequested.connect(fcn)  # noqa: QToolButton.customContextMenuRequested

    def _create_menu(self):
        self._menu = ButtonMenu(self)
        self._menu.setToolTipsVisible(True)
        self.setMenu(self._menu)
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.MenuButtonPopup)

    def _set_icon(self, icon, icon_size):
        icon = convert.to_qicon(icon)  # make sure that it's a QIcon
        if icon_size is not None:
            pixmap = convert.rescale_icon(icon, icon_size)
            self.setIconSize(pixmap.size())
            icon = convert.to_qicon(pixmap)
        elif icon.availableSizes():
            style = self.style()
            metric = style.pixelMetric(style.PixelMetric.PM_ButtonIconSize)
            s = icon.availableSizes()[0]
            size = QtCore.QSize(max(s.width(), metric), max(s.height(), metric))
            if self.iconSize().width() < size.width() or \
                    self.iconSize().height() < size.height():
                self.setIconSize(size)
        self.setIcon(icon)


class ButtonMenu(QtWidgets.QMenu):
    """Display the :class:`QtWidgets.QMenu` underneath the :class:`Button`."""

    def showEvent(self, event):
        """Overrides :meth:`QtWidgets.QWidget.showEvent`."""
        point = self.parent().mapToGlobal(QtCore.QPoint(0, 0))
        offset = self.parent().width() - self.width()
        self.move(point + QtCore.QPoint(offset, self.parent().height()))
        super(ButtonMenu, self).showEvent(event)
