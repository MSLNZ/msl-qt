"""Example script to repeatedly write data to a file until aborted by the user."""

# pyright: reportImplicitOverride=false
from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING

from msl.qt import LoopUntilAbort, prompt

if TYPE_CHECKING:
    from io import TextIOWrapper


class Loop(LoopUntilAbort):
    """Repeatedly write data to a file until aborted by the user."""

    def __init__(self) -> None:
        """Initialize the `LoopUntilAbort` class and create a file to write data to.

        Use a 250-ms delay between successive calls to the `loop` method.
        """
        super().__init__(loop_delay=250)

        self.output_path: str = tempfile.gettempdir() + "/msl-qt-loop-until-abort.txt"
        self.f: TextIOWrapper = open(self.output_path, mode="w")
        _ = self.f.write(f"Started at {self.current_time}\n")

    def loop(self) -> None:
        """Overrides `LoopUntilAbort.loop()`.

        This method gets called repeatedly in a loop (every `loop_delay` ms).
        """
        _ = self.f.write(f"Iteration: {self.iteration}\n")
        _ = self.f.write(f"Elapsed time: {self.elapsed_time}\n")
        self.set_label_text(f"The current time is\n{self.current_time}")

    def cleanup(self) -> None:
        """Overrides `LoopUntilAbort.cleanup()`.

        This method gets called when the LoopExample window is closing.
        """
        _ = self.f.write(f"Stopped at {self.current_time}\n")
        self.f.close()

        prompt.information(f"The data was save to\n{self.output_path}")


def show() -> None:
    """Show the widget and start the loop."""
    loop = Loop()
    loop.start()


if __name__ == "__main__":
    show()
