"""Illustrates the use of the `LoopUntilAbort` class.

Uses single-shot mode using a random sleep time.
"""

# pyright: reportImplicitOverride=false
from __future__ import annotations

import random

from msl.qt import LoopUntilAbort, Sleep, Slot


class LoopSleep(LoopUntilAbort):
    """Illustrates the use of the `LoopUntilAbort` class in single-shot mode."""

    def __init__(self) -> None:
        """Initialize the `LoopUntilAbort` class in single-shot mode."""
        super().__init__(single_shot=True)

        # Create the `Sleep` thread, which uses `SleepWorker` as the `Worker` class
        self.sleep: Sleep = Sleep()

        # Call `self.update_status_bar_text` when sleeping is finished
        _ = self.sleep.finished.connect(self.update_status_bar_text)

        # To illustrate how to disconnect from a `Signal` we add another
        # `Slot` to be called when sleeping is finished
        _ = self.sleep.finished.connect(self.countdown)

    @Slot()
    def countdown(self) -> None:
        """Slot to be called on a `Sleep.finished` signal."""
        if self.iteration == 5:  # then stop being notified of the countdown
            _ = self.sleep.finished.disconnect(self.countdown)
        print(f"countdown: {5 - self.iteration}")

    @Slot()
    def update_status_bar_text(self) -> None:
        """Slot to be called on a `Sleep.finished` signal."""
        print(f"finished loop #: {self.iteration}")

        # You can access attributes from the `SleepWorker` class (i.e., self.sleep.seconds)
        self.set_status_bar_text(f"Slept for {self.sleep.seconds:.3f} seconds")

        # Run the loop one more time (only if the loop's `QTimer` still exists)
        # NOTE: Do not call `self.loop()` directly, you must call `self.loop_once()`
        self.loop_once()

    def loop(self) -> None:
        """Overrides `LoopUntilAbort.loop()`."""
        print(f"started loop  #: {self.iteration}")

        # Pick a random number of seconds to sleep for
        sleep_for_this_many_seconds = random.randint(100, 2000) * 1e-3

        # The `sleep_for_this_many_seconds` parameter gets passed to the
        # constructor of the `SleepWorker` class and the `Sleep` thread starts
        self.sleep.start(sleep_for_this_many_seconds)

        # The `self.sleep.start()` call does not block (if it did the GUI would freeze)
        # so setting the label text will be executed immediately
        text = (
            f"Sleeping for {sleep_for_this_many_seconds:.3f} seconds.\n"
            f"You can move and resize the window because it remains responsive."
        )
        self.set_label_text(text)

    def cleanup(self) -> None:
        """Overrides `LoopUntilAbort.cleanup()`."""
        # Stop the `Sleep` thread before exiting the program.
        # Waiting for the thread to stop is a blocking call,
        # so the GUI will be frozen while it is closing.
        _ = self.sleep.stop()


def show() -> None:
    """Show the widget and start the loop."""
    loop = LoopSleep()
    loop.start()


if __name__ == "__main__":
    show()
