"""Example to show the `ComboBox` widget."""

from __future__ import annotations

from msl.qt import ComboBox, QtWidgets, Slot, application, to_qicon


class Window(QtWidgets.QWidget):
    """Main Window."""

    def __init__(self) -> None:
        """Main Window to contain ComboBoxes."""
        super().__init__()

        self.c1: ComboBox = ComboBox(
            items=["\U0001f600", "\U0001f641", "\U0001f914"],
            text_changed=self.on_text_changed,
        )
        self.c2: ComboBox = ComboBox(
            items=["Red", "Orange", "Yellow", "Green", "Blue"],
            initial="Green",
            text_changed=self.on_text_changed,
        )
        self.c3: ComboBox = ComboBox(
            items={
                "data-only": 6,
                "icon-only": to_qicon(20),
                "icon-and-data": (to_qicon(12), "icon"),
            },
            index_changed=self.on_index_changed,
        )
        self.c4: ComboBox = ComboBox(tooltip="Empty, no items")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.c1)
        layout.addWidget(self.c2)
        layout.addWidget(self.c3)
        layout.addWidget(self.c4)
        self.setLayout(layout)

    @Slot(int)
    def on_index_changed(self, index: int) -> None:
        """Slot called when the index changes."""
        data = self.c3.itemData(index)
        print(f"index={index}, data={data}")

    @Slot(str)
    def on_text_changed(self, text: str) -> None:
        """Slot called when the text changes."""
        print(f"text: {text}")


def show() -> None:
    """Create the QApplication and show the main window."""
    app = application()
    w = Window()
    w.show()
    _ = app.exec()


if __name__ == "__main__":
    show()
