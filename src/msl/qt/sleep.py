"""Sleep without freezing the graphical user interface (GUI)."""

from __future__ import annotations

import time

from .threading import Thread, Worker


class Sleep(Thread):
    """Sleep without freezing the graphical user interface (GUI)."""

    def __init__(self) -> None:
        """Sleep without freezing the graphical user interface (GUI).

        !!! example
            ```python
            from msl.examples.qt import LoopExampleSleep

            loop = LoopExampleSleep()
            loop.start()
            ```

        ??? example
            <!-- fmt: off -->
            ```python
            --8<-- "src/msl/examples/qt/loop_until_abort_sleep.py
            ```
            <!-- fmt: on -->

        """
        super().__init__(SleepWorker)


class SleepWorker(Worker):
    """The [Worker][msl.qt.threading.Worker] class for [Sleep][..Sleep]."""

    def __init__(self, seconds: float) -> None:
        """The [Worker][msl.qt.threading.Worker] class for [Sleep][..Sleep].

        Delays execution for a certain number of seconds without
        freezing the graphical user interface (GUI).

        Args:
            seconds: The number of seconds to sleep for.
        """
        super().__init__()
        self.seconds: float = seconds

    def process(self) -> None:  # pyright: ignore[reportImplicitOverride]
        """Calls [time.sleep][]."""
        time.sleep(self.seconds)
