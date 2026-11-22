"""Example to show the `CheckBox` widget."""

from __future__ import annotations

from msl.qt import CheckBox, Qt, QtWidgets, Slot, application


class Window(QtWidgets.QWidget):
    """Main Window."""

    def __init__(self) -> None:
        """Main Window that contains different kinds of CheckBoxes."""
        super().__init__()

        self.c1: CheckBox = CheckBox(initial=True, tooltip="No displayed text")
        self.c2: CheckBox = CheckBox(checkable=False, text="uncheckable")
        self.c3: CheckBox = CheckBox(
            text="On/off checkable",
            initial=Qt.CheckState.Unchecked,
            state_changed=self.on_bi_state_changed,
            tooltip="CheckBox that may be in one of two states",
        )
        self.c4: CheckBox = CheckBox(
            text="Partially checkable",
            initial=Qt.CheckState.PartiallyChecked,
            state_changed=self.on_tri_state_changed,
            tooltip="CheckBox that may be in one of three states",
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.c1)
        layout.addWidget(self.c2)
        layout.addWidget(self.c3)
        layout.addWidget(self.c4)
        self.setLayout(layout)

    @staticmethod
    @Slot(Qt.CheckState)
    def on_bi_state_changed(state: Qt.CheckState) -> None:
        """Slot to handle the state-changed signal."""
        print(f"The state of 'On/off checkable' is now {state!r}")

    @staticmethod
    @Slot(Qt.CheckState)
    def on_tri_state_changed(state: Qt.CheckState) -> None:
        """Slot to handle the state-changed signal."""
        print(f"The state of 'Partially checkable' is now {state!r}")


def show() -> None:
    """Create the QApplication and show the Window that contains the CheckBoxes."""
    app = application()
    w = Window()
    w.show()
    _ = app.exec()


if __name__ == "__main__":
    show()
