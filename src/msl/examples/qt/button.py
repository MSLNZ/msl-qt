"""Example to show the [Button][msl.qt.widgets.button.Button] widget."""

from __future__ import annotations

from msl.qt import Button, QtWidgets, Slot, application


@Slot()
def left() -> None:
    """The Slot to handle a left click on the Button."""
    print("left click")


@Slot()
def right() -> None:
    """The Slot to handle a right click on the Button."""
    print("right click")


@Slot()
def item1() -> None:
    """The Slot to handle the first menu item clicked."""
    print("item #1 selected")


@Slot()
def item2() -> None:
    """The Slot to handle the second menu item clicked."""
    print("item #2 selected")


@Slot()
def item4() -> None:
    """The Slot to handle the fourth menu item clicked."""
    print("item #4 selected")


def show() -> None:
    """Create the QApplication and show the Button."""
    app = application()
    b = Button(text="My button", icon=32, icon_size=4.0, left_click=left, right_click=right, tooltip="Example button")
    b.add_menu_item(text="Item #1", triggered=item1, icon=43, tooltip="Item #1")
    b.add_menu_item(text="Item #2", triggered=item2, icon=47, tooltip="Second")
    b.add_menu_item(
        text="Item #3",
        icon=QtWidgets.QStyle.StandardPixmap.SP_DialogResetButton,
        tooltip="Visible but disabled (triggered not set)",
    )
    b.add_menu_separator()
    b.add_menu_item(text="Item #4", triggered=item4, tooltip="Fourth")
    b.show()
    _ = app.exec()


if __name__ == "__main__":
    show()
