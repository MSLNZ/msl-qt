"""
A button that can display text and/or an icon, with an optional action menu.
"""
from PyQt5 import QtWidgets, QtCore, QtGui

from msl.qt.io import get_icon, rescale_image


class Button(QtWidgets.QToolButton):

    def __init__(self, text=None, image=None, image_size=None, left_click=None,
                 right_click=None, is_text_under_image=True, tooltip=None, parent=None):
        """A button that can display text and/or an icon, with an optional action menu.

        Parameters
        ----------
        text : :obj:`str`, optional
            The text to display on the button.
        image : :obj:`object`, optional
            Any image object that is supported by :func:`~msl.qt.io.get_icon`.
        image_size : :obj:`int`, :obj:`float`, :obj:`tuple` of :obj:`int` or :obj:`~QtCore.QSize`, optional
            Rescale the image to the specified `size`.
            If the value is :obj:`None` then do not rescale the image.
            If an :obj:`int` then set the width and the height to be the `size` value.
            If a :obj:`float` then a scaling factor.
            If a :obj:`tuple` then the (width, height) values.
        left_click : :obj:`callable`, optional
            The function to be called for a mouse left-click event.
        right_click : :obj:`callable`, optional
            The function to be called for a mouse right-click event.
        is_text_under_image : :obj:`bool`, optional
            If displaying an image and text then whether to place the text
            under, :obj:`True`, or beside, :obj:`False`, the image.
        tooltip : :obj:`str`, optional
            The tooltip to display for the button.
        parent : :class:`~QtWidgets.QWidget`, optional
            The parent widget.
        """
        QtWidgets.QToolButton.__init__(self, parent)

        self._menu = None

        if image is not None:
            image = rescale_image(image, image_size)

        if text and image:
            if is_text_under_image:
                self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            else:
                self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.setText(text)
            self._set_icon(image)
        elif text and not image:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
            self.setText(text)
        elif not text and image:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
            self._set_icon(image)

        # the left-click event handler
        if left_click is not None:
            self.set_left_click(left_click)

        # setContextMenuPolicy allows for right-click events
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        if right_click is not None:
            self.set_right_click(right_click)

        if tooltip is not None:
            self.setToolTip(tooltip)

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

    def add_menu_item(self, text=None, triggered=None, image=None, shortcut=None, tooltip=None):
        """Add a new item to the action menu.

        Parameters
        ----------
        text : :obj:`str`, optional
            The text to display for this item.
        triggered : :obj:`callable`, optional
            The function to be called when this item is selected.
            If :obj:`None` then the item is displayed but it is disabled.
        image : :obj:`object`, optional
            Any image object that is supported by :func:`~msl.qt.io.get_icon`.
        shortcut : :obj:`str`, optional
          The keyboard shortcut to use to select this item, e.g., ``CTRL+A``
        tooltip : :obj:`str`, optional
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
            action.setShortcut(shortcut)
        if image is not None:
            action.setIcon(get_icon(image))
        if tooltip is not None:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
            # the tooltip of a QAction in a QMenu is not shown. Here's a work-around.
            self._menu.hovered.connect(self._show_menu_tooltip)
        self._menu.addAction(action)

    def add_menu_separator(self):
        """Insert a separator between menu items."""
        if self._menu is None:
            self._create_menu()
        self._menu.addSeparator()

    def _show_menu_tooltip(self, action):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), action.toolTip())

    def _create_menu(self):
        self._menu = QtWidgets.QMenu(self)
        self.setMenu(self._menu)
        self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)

    def _set_icon(self, image):
        self.setIcon(get_icon(image))
        self.setIconSize(image.size())
