"""Base classes for running a process in a background `QThread`."""

from __future__ import annotations

import sys
import time
import traceback as tb
from types import TracebackType
from typing import TYPE_CHECKING

from .binding import QtCore, Signal, Slot
from .prompt import critical

if TYPE_CHECKING:
    from typing import Any, Callable

    from .typing import SlotType


class Worker(QtCore.QObject):
    """Process a long running or blocking operation in a background thread."""

    finished: Signal = Signal()
    error: Signal = Signal(BaseException, TracebackType)

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        r"""Process a long running or blocking operation in a background thread.

        Subclass [Worker][...Worker] and override the [process()][...Worker.process] method.

        The `*args` and `**kwargs` parameters are passed to the constructor of the
        [Worker][...Worker] when the [Thread.start()][...Thread.start] method is called.

        !!! tip
            You can access the attributes of the [Worker][...Worker] as though
            they are attributes of the [Thread][...Thread] instance
            (see [\_\_getattr\_\_][...Thread.__getattr__]).

        !!! example
            See [SleepWorker][...SleepWorker] for an example.
        """
        super().__init__(parent=None)  # the parent must always be None

    def process(self) -> None:
        """The long running or blocking process to run.

        !!! warning
            You must override this method.
        """
        msg = "You must override the `Worker.process` method."
        raise NotImplementedError(msg)

    @Slot()
    def _process(self) -> None:
        try:
            self.process()
        except:  # noqa: E722
            _, value, traceback = sys.exc_info()
            self.error.emit(value, traceback)
        else:
            self.finished.emit()


class Thread(QtCore.QObject):
    """Moves a [Worker][msl.qt.threading.Worker] to a new [QThread][QtCore.QThread]."""

    finished: Signal = Signal()
    """A [Signal][] that is emitted when the thread is finished.

    Emitted when [Worker.process()][...Worker.process] finishes.
    """

    def __init__(self, worker: type[Worker]) -> None:
        """Moves a [Worker][...Worker] to a new [QThread][QtCore.QThread].

        Args:
            worker: A [Worker][...Worker] subclass that has *not* been instantiated.

        !!! example
            See [Sleep][...Sleep] for an example.
        """
        super().__init__()

        self._thread: QtCore.QThread | None = None
        self._worker: Worker | None = None
        self._finished: bool = False
        self._signals_slots: list[tuple[str, SlotType, QtCore.Qt.ConnectionType]] = []

        if not callable(worker):
            msg = "The Worker for the Thread must not be instantiated"  # type: ignore[unreachable] # pyright: ignore[reportUnreachable]
            raise TypeError(msg)

        if not issubclass(worker, Worker):  # pyright: ignore[reportUnnecessaryIsInstance]
            msg = "The Worker for the Thread is not a Worker subclass"  # type: ignore[unreachable] # pyright: ignore[reportUnreachable]
            raise TypeError(msg)

        self._worker_class: type[Worker] = worker

    def __getattr__(self, item: str) -> Any:  # noqa: ANN401
        """All missing attributes of [Thread][...Thread] are passed to the [Worker][...Worker] instance."""
        if item == "__wrapped__":
            # When pytest collects tests/test_thread_worker_connect_for_docstring.py
            # the value of the `item` argument can be "__wrapped__".
            # If PyQt6 is used as the binding, the following error occurs
            #   RuntimeError: wrapped C/C++ object of type ... has been deleted
            return None

        if self._worker is not None:
            return getattr(self._worker, item)

        msg = "You must start the Thread before accessing an attribute of the Worker"
        raise AttributeError(msg)

    @Slot(BaseException, TracebackType)
    def error_handler(self, exception: BaseException, traceback: TracebackType) -> None:
        """Slot to handle an exception.

        If an exception is raised while the [Worker][...Worker] is running the process, the default
        behaviour is to show the error message in a [critical][msl.qt.prompt.critical] dialog window.
        You can override this method to implement your own error handler.

        Args:
            exception: The exception instance
            traceback: The traceback object.
        """
        critical("".join(tb.format_exception(type(exception), exception, traceback)))

    def is_finished(self) -> bool:
        """Check if the thread is finished.

        Returns:
            Whether the thread is finished.
        """
        if self._thread is None:
            return self._finished
        return bool(self._check(self._thread.isFinished))

    def is_running(self) -> bool:
        """Check if the thread is running.

        Returns:
            Whether the thread is running.
        """
        if self._thread is None:
            return False
        return bool(self._check(self._thread.isRunning))

    def quit(self) -> None:
        """Tells the thread's event loop to exit."""
        if self._thread is not None:
            _ = self._check(self._thread.quit)

    def start(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Start processing the [Worker][...Worker] in a [QThread][QtCore.QThread].

        The `*args` and `**kwargs` are passed to the constructor of the [Worker][...Worker] subclass.
        """
        self._thread = QtCore.QThread()
        self._worker = self._worker_class(*args, **kwargs)
        _ = self._worker.moveToThread(self._thread)  # PyQt6 return None, PySide6 returns bool

        for signal, slot, typ in self._signals_slots:
            getattr(self._worker, signal).connect(slot, type=typ)

        _ = self._worker.error.connect(self._on_worker_error)
        _ = self._worker.error.connect(self.error_handler)
        _ = self._worker.finished.connect(self._worker_finished)
        _ = self._worker.finished.connect(self._worker.deleteLater)
        _ = self._thread.started.connect(self._worker._process)  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
        _ = self._thread.finished.connect(self._thread.deleteLater)
        _ = self._thread.finished.connect(self.finished)
        self._thread.start()

    def stop(self, milliseconds: int | None = None) -> bool | None:
        """Calls [quit][..quit] then [wait][..wait]."""
        self.quit()
        return self.wait(milliseconds=milliseconds)

    def wait(self, milliseconds: int | None = None) -> bool | None:
        """Wait for the thread to either finish or timeout.

        Args:
            milliseconds: The number of milliseconds to wait before a timeout occurs.
                If `None`, then wait until the thread finishes.

        Returns:
            `True` if the thread finished, `False` if the thread timed out
                or `None` if the thread is not running.
        """
        if self._thread is None:
            return None

        out: bool | None
        if milliseconds is None:
            out = self._check(self._thread.wait)
        else:
            out = self._check(self._thread.wait, int(milliseconds))
        return out

    def worker_connect(
        self,
        signal: str | Signal,
        slot: SlotType,
        type: QtCore.Qt.ConnectionType = QtCore.Qt.ConnectionType.AutoConnection,  # noqa: A002
    ) -> None:
        """Connect a [Signal][] of the [Worker][...Worker] to a [Slot][].

        This method is intended to be called *before* the [Thread][...Thread]
        starts. The `signal` is connected to the `slot` *after* the
        [QObject.moveToThread()](https://doc.qt.io/qt-6/qobject.html#moveToThread)
        function is called, which occurs in the [start()][...Thread.start] method.
        You may also call this method while the [Thread][...Thread] is running.

        ??? abstract "Click to view an example"
            ```python
            --8<-- "tests/test_thread_worker_connect_for_docstring.py:1:24"
            ```

        Args:
            signal: The `signal` to connect the `slot` to. If a [str][], then the value
                is either the name of a class attribute of the [Worker][...Worker] or
                the `name` parameter that was specified in the [Signal][] constructor.
            slot: A callable function to use as the [Slot][].
            type: The type of connection to use between the `signal` and `slot`.
        """
        if not callable(slot):
            msg = "The `slot` must be callable"  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
            raise TypeError(msg)

        signal_name = _signal_to_str(signal)
        self._signals_slots.append((signal_name, slot, type))
        if self.is_running():
            getattr(self._worker, signal_name).connect(slot, type=type)

    def worker_disconnect(self, signal: str | Signal | None = None, slot: SlotType | None = None) -> None:
        """Disconnect [Signal][]s from [Slot][]s for the [Worker][...Worker].

        Removes the signal-slot connections that were created by calling [worker_connect][..worker_connect].

        Args:
            signal: The signal to disconnect from the `slot`. If `None`, all signals that
                were connected by calling [worker_connect][..worker_connect] are disconnected
                (in which case the `slot` parameter is ignored).
            slot: The slot to be disconnected from the `signal`. If `None`, disconnect all slots
                from the specified `signal` that were connected via [worker_connect][..worker_connect],
                otherwise the value must be the same callable object that was passed to
                [worker_connect][..worker_connect].
        """
        if signal is None:
            if self.is_running():
                for signal_name, slt, _ in self._signals_slots:
                    getattr(self._worker, signal_name).disconnect(slt)
            self._signals_slots.clear()
            return

        signal_name = _signal_to_str(signal)
        indices: list[int] = []
        for i, (name, slt, _) in enumerate(self._signals_slots):
            if (name == signal_name) and ((slot is None) or (slot is slt)):
                indices.append(i)

        if not indices:
            if slot is None:
                msg = f"The signal {signal_name!r} does not have connected slots created from `worker_connect`"
            else:
                msg = f"The slot {slot} is not connected to the signal {signal!r} using `worker_connect`"
            raise ValueError(msg)

        for i in reversed(indices):
            signal_name, slt, _ = self._signals_slots.pop(i)
            if self.is_running():
                getattr(self._worker, signal_name).disconnect(slt)

    def _check(self, method: Callable[..., bool | None], *args: int) -> bool | None:
        """Wrap all calls to the QThread in a try-except block to silently ignore the following error.

        RuntimeError: Internal C++ object (*.QtCore.QThread) already deleted.
        """
        try:
            result: bool | None = method(*args)
        except RuntimeError:
            self._thread = None
            return None
        else:
            return result

    @Slot()
    def _worker_finished(self) -> None:
        """Slot that is called when the Worker finished successfully."""
        if self._thread is not None:
            self._thread.quit()
        self._finished = True

    @Slot(BaseException, TracebackType)
    def _on_worker_error(self, *_: object) -> None:
        """Slot to handle an exception from the Worker."""
        if self._thread is not None:
            self._thread.exit(-1)


class SleepWorker(Worker):
    """The [Worker][..Worker] class for [Sleep][..Sleep]."""

    def __init__(self, seconds: float) -> None:
        """The [Worker][..Worker] class for [Sleep][..Sleep].

        Delays execution for a certain number of seconds without
        freezing the graphical user interface.

        Args:
            seconds: The number of seconds to sleep for.
        """
        super().__init__()
        self.seconds: float = seconds

    def process(self) -> None:  # pyright: ignore[reportImplicitOverride]
        """Overrides [process()][...Worker.process] to call the blocking [time.sleep][] function."""
        time.sleep(self.seconds)


class Sleep(Thread):
    """Sleep without freezing the graphical user interface."""

    def __init__(self) -> None:
        """Sleep without freezing the graphical user interface."""
        super().__init__(SleepWorker)


def _signal_to_str(signal: str | Signal) -> str:
    """Convert `signal` to a str."""
    if isinstance(signal, str):
        return signal

    if not isinstance(signal, Signal):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = "The `signal` parameter must be a string or an unbound QtCore Signal"  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
        raise TypeError(msg)

    if hasattr(signal, "signatures"):  # PyQt6
        signature = str(signal.signatures[0])  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
        if "(" not in signature:
            msg = (
                "Cannot determine the Signal name. Either pass in the Signal name as "
                "a string or define a `name` parameter in the Signal constructor."
            )
            raise TypeError(msg)
    else:  # PySide6
        signature = str(signal)

    return signature.split("(")[0]
