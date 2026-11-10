"""Illustrates the use of the [LoopUntilAbort][msl.qt.loop_until_abort.LoopUntilAbort] class.

Uses *single shot* mode using a random [Sleep][msl.qt.sleep.Sleep] time.
"""

# pyright: reportImplicitOverride=false
from __future__ import annotations

import random

from msl.qt import LoopUntilAbort, Sleep, Slot


class LoopExampleSleep(LoopUntilAbort):
    """Initialize the LoopUntilAbort class in single-shot mode."""

    def __init__(self) -> None:
        """Initialize the LoopUntilAbort class in single-shot mode."""
        super().__init__(single_shot=True)

        # create the Sleep thread which uses SleepWorker as the worker class
        self.sleep: Sleep = Sleep()

        # call self.update_status_bar_text when sleeping is finished
        _ = self.sleep.finished.connect(self.update_status_bar_text)

        # just for fun, add another slot to be called when sleeping is finished
        _ = self.sleep.finished.connect(self.countdown)

    @Slot()
    def countdown(self) -> None:
        """Slot to be called on a `Sleep.finished` signal."""
        if self.iteration == 5:  # stop being notified of the countdown
            _ = self.sleep.finished.disconnect(self.countdown)
        print("countdown: " + str(5 - self.iteration))

    @Slot()
    def update_status_bar_text(self) -> None:
        """Slot to be called on a `Sleep.finished` signal."""
        print("finished loop #: " + str(self.iteration))

        # you can access attributes from the SleepWorker class, i.e., self.sleep.seconds
        self.set_status_bar_text(f"Slept for {self.sleep.seconds:.3f} seconds")

        # run the loop one more time (only if the loop's QTimer still exists)
        # NOTE: do not call self.loop() directly, you should call self.loop_once()
        self.loop_once()

    def loop(self) -> None:
        """Overrides `LoopUntilAbort.loop()`."""
        print("started loop #: " + str(self.iteration))

        # pick a random number of seconds to sleep for
        sleep_for_this_many_seconds = random.randint(100, 2000) * 1e-3

        # the `sleep_for_this_many_seconds` parameter gets passed to the
        # constructor of the SleepWorker class and the Sleep thread starts
        self.sleep.start(sleep_for_this_many_seconds)

        # the self.sleep.start() call does not block (if it did the GUI would freeze)
        # so any code that is after it will be executed immediately -- this is why
        # the text of the "label" gets updated immediately
        self.set_label_text(f"Sleeping for {sleep_for_this_many_seconds:.3f} seconds")

    def cleanup(self) -> None:
        """Overrides `LoopUntilAbort.cleanup()`."""
        # Stop the Sleep thread before exiting the program.
        # Waiting for the thread to stop is a blocking call so the GUI will be frozen while it is closing.
        _ = self.sleep.stop()


def show() -> None:
    """Show the widget and start the loop."""
    loop = LoopExampleSleep()
    loop.start()


if __name__ == "__main__":
    show()
