"""Base classes for starting a process in a new [QThread][QtCore.QThread]."""

from __future__ import annotations

import sys
import traceback as tb
from types import TracebackType
from typing import TYPE_CHECKING, Callable

from ._qt import QtCore, Signal, Slot
from .prompt import critical

if TYPE_CHECKING:
    from typing import Any, Callable

    from ._qt import SignalInstance


class Worker(QtCore.QObject):
    """Process an expensive or blocking operation in a thread that is separate from the main thread.

    You can access to the attributes of the [Worker][..Worker]
    as though they are attributes of the [Thread][...Thread].

    The `*args` and `**kwargs` parameters are passed to the constructor of the
    [Worker][..Worker] when the [start][..Thread.start] method is called.

    !!! example
        See [SleepWorker][msl.qt.sleep.SleepWorker] for an example.
    """

    finished: Signal = Signal()
    error: Signal = Signal(BaseException, TracebackType)

    def process(self) -> None:
        """The expensive or blocking operation to process.

        !!! warning
            You must override this method.
        """
        msg = "You must override the `Worker.process` method."
        raise NotImplementedError(msg)

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
    """A [Signal][QtCore.Signal] that is emitted when the thread is finished.

    Emitted when [Worker.process][...Worker.process] finishes.
    """

    def __init__(self, worker: type[Worker]) -> None:
        """Moves a [Worker][...Worker] to a new [QThread][QtCore.QThread].

        Args:
            worker: A [Worker][...Worker] subclass that has *not* been instantiated.

        !!! example
            See [Sleep][msl.qt.sleep.Sleep] for an example.
        """
        super().__init__()

        self._thread: QtCore.QThread | None = None
        self._worker: Worker | None = None
        self._finished: bool = False
        self._signals_slots: list[tuple[str, Callable[..., object]]] = []

        if not callable(worker):
            msg = "The Worker for the Thread must not be instantiated"  # type: ignore[unreachable] # pyright: ignore[reportUnreachable]
            raise TypeError(msg)

        if not issubclass(worker, Worker):  # pyright: ignore[reportUnnecessaryIsInstance]
            msg = "The Worker for the Thread is not a Worker subclass"  # type: ignore[unreachable] # pyright: ignore[reportUnreachable]
            raise TypeError(msg)

        self._worker_class: type[Worker] = worker

    def __getattr__(self, item: str) -> Any:  # noqa: ANN401
        """All other attributes are assumed to be those of the `Worker`."""
        if self._worker is not None:
            return getattr(self._worker, item)

        msg = "You must start the Thread before accessing an attribute of the Worker"
        raise AttributeError(msg)

    def error_handler(self, exception: BaseException, traceback: TracebackType) -> None:
        """Handle an exception.

        If an exception is raised by the [Worker][...Worker] then the default
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

        The `*args` and `**kwargs` are passed to the constructor of the [Worker][...Worker] class.
        """
        self._thread = QtCore.QThread()
        self._worker = self._worker_class(*args, **kwargs)
        _ = self._worker.moveToThread(self._thread)  # PyQt6 return None, PySide6 returns bool

        for signal, slot in self._signals_slots:
            getattr(self._worker, signal).connect(slot)

        _ = self._worker.error.connect(lambda *_: self._thread.exit(-1))  # pyright: ignore[reportOptionalMemberAccess, reportUnknownArgumentType, reportUnknownLambdaType]
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
                If `None` then this method will not time out and the thread must
                return from its `run` method.

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

    def worker_connect(self, signal: str | Signal | SignalInstance, slot: Callable[..., object]) -> None:
        """Connect a [Signal][QtCore.Signal] from the [Worker][...Worker] to a [Slot][QtCore.Slot].

        This method is intended to be called *before* a [Worker][...Worker] starts.
        Although, you can still call this method when a [Worker][...Worker] is running,
        it is easier (fewer characters to type) to access the attributes of a
        [Worker][...Worker] as though they are attributes of the [Thread][...Thread].

        Args:
            signal: The `signal` to connect the `slot` to. If a [str][], then the value is either
                the name of a class attribute of the [Worker][...Worker] or the `name`
                parameter that was used in the [Signal][QtCore.Signal] constructor.
            slot: A callable function to use as the [Slot][QtCore.Slot].
        """
        signal, slot = _check_signal_slot(signal, slot)
        if self.is_running():
            getattr(self._worker, signal).connect(slot)
        else:
            self._signals_slots.append((signal, slot))

    def worker_disconnect(self, signal: str | Signal | SignalInstance, slot: Callable[..., object]) -> None:
        """Disconnect a [Slot][QtCore.Slot] from a [Signal][QtCore.Signal] for the [Worker][...Worker].

        This method is intended to be called *before* a [Worker][...Worker] is restarted.
        Although, you can still call this method when a [Worker][...Worker] is running,
        it is easier (fewer characters to type) to access the attributes of a
        [Worker][...Worker] as though they are attributes of the [Thread][...Thread].

        Args:
            signal: The `signal` to disconnect the `slot` from. Must be the same
                value that was used in [worker_connect][..worker_connect].
            slot: Must be the same callable that was used in [worker_connect][..worker_connect].
        """
        signal, slot = _check_signal_slot(signal, slot)
        if self.is_running():
            getattr(self._worker, signal).disconnect(slot)
            return

        try:
            self._signals_slots.remove((signal, slot))
        except ValueError:
            if not self._signals_slots:
                msg = "No Worker signals were connected to slots"
                raise ValueError(msg) from None

            options = "\n".join(f"  {a!r} {b}" for a, b in self._signals_slots)
            msg = f"The slot {slot} is not connected to the signal {signal!r}.\nOptions\n{options}"
            raise ValueError(msg) from None

    def _check(self, method: Callable[..., Any], *args: int) -> bool | None:
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
        """Called when the [Worker][msl.qt.threading.Worker] finished successfully."""
        if self._thread is not None:
            self._thread.quit()
        self._finished = True


def _check_signal_slot(signal: str | Signal | SignalInstance, slot: object) -> tuple[str, Callable[..., object]]:
    """Check the input types and returns the appropriate types."""
    if not callable(slot):
        msg = "`slot` must be callable"
        raise TypeError(msg)

    if isinstance(signal, str):
        return signal, slot

    if isinstance(signal, Signal):
        if hasattr(signal, "signatures"):  # PyQt
            signature = str(signal.signatures[0])  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
            if "(" not in signature:
                msg = (
                    "Cannot determine the Signal name. Either pass in "
                    "the Signal name as a string or define a name "
                    "parameter in the Signal constructor."
                )
                raise TypeError(msg)
        else:
            signature = str(signal)
        return signature.split("(")[0], slot

    msg = "`signal` must be a QtCore.Signal or string"
    raise TypeError(msg)
