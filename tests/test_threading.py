# cSpell: ignore msleep
from __future__ import annotations

import pytest

from msl.qt import QtCore, Signal, Slot, Thread, Worker, application, binding


def test_invalid_constructor() -> None:

    class MyWorker(Worker):
        def __init__(self) -> None:
            super().__init__()

    with pytest.raises(TypeError, match=r"must not be instantiated"):
        _ = Thread(MyWorker())  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]

    with pytest.raises(TypeError, match=r"not a Worker subclass"):
        _ = Thread(QtCore.QTimer)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


def test_worker_raises_exception() -> None:  # noqa: C901

    class MyWorker(Worker):
        def __init__(self, seconds: int, *, raise_exception: bool) -> None:
            super().__init__()
            self.seconds: int = seconds
            self.raise_exception: bool = raise_exception
            self.result: int = -1

        def process(self) -> None:  # pyright: ignore[reportImplicitOverride]
            QtCore.QThread.sleep(self.seconds)
            if self.raise_exception:
                msg = "Cannot open file"
                raise OSError(msg)
            self.result = self.seconds

    class MyThread(Thread):
        def __init__(self) -> None:
            super().__init__(MyWorker)

        def error_handler(self, exception: BaseException, traceback: object) -> None:  # pyright: ignore[reportImplicitOverride]  # noqa: ARG002
            assert str(exception) == "Cannot open file"

    app = application()
    threads = [MyThread() for _ in range(10)]

    # check that calling the methods that require
    # self._thread to be created do not raise an exception
    assert all(not thread.is_running() for thread in threads)
    assert all(not thread.is_finished() for thread in threads)
    for t in threads:
        assert t.quit() is None  # type: ignore[func-returns-value]
        assert t.wait() is None
        assert t.stop() is None

    # start certain threads
    for index, thread in enumerate(threads):
        if index % 2:
            thread.start(index, raise_exception=index > 5)  # only raise the exception if index > 5

    assert all(thread.is_running() for i, thread in enumerate(threads) if i % 2)
    assert all(not thread.is_running() for i, thread in enumerate(threads) if not i % 2)
    assert all(not thread.is_finished() for thread in threads)

    # The following tests that a RuntimeError exception is not raised
    #   RuntimeError: Internal C++ object (*.QtCore.QThread) already deleted.
    #
    # The fact that this test finishes also shows that the QThread did properly quit
    # after an exception is raised by the Worker
    while any(thread.is_running() for thread in threads):
        for thread in threads:
            _ = thread.wait(100)
        app.processEvents()

    # another check that calling wait() won't block forever
    for thread in threads:
        _ = thread.wait()

    assert all(not thread.is_running() for thread in threads)

    # the threads that started and did not raise an error are finished
    # the threads that never started or that raised an exception are not finished
    assert all(thread.is_finished() for i, thread in enumerate(threads) if i in [1, 3, 5])
    assert all(not thread.is_finished() for i, thread in enumerate(threads) if not i % 2)

    # get the result from each worker
    for index, thread in enumerate(threads):
        if index in {1, 3, 5}:
            assert thread.result == index
        elif not index % 2:
            with pytest.raises(AttributeError, match=r"You must start the Thread"):
                _ = thread.result
        else:
            assert thread.result == -1


def test_finished() -> None:

    class MyWorker(Worker):
        def __init__(self, index: int) -> None:
            super().__init__()
            self.index: int = index
            self.squared: int | None = None

        def process(self) -> None:  # pyright: ignore[reportImplicitOverride]
            QtCore.QThread.msleep(500)
            self.squared = self.index**2

    class MyThread(Thread):
        def __init__(self) -> None:
            super().__init__(MyWorker)

    def slot1() -> None:
        values.append(t.squared)

    def slot2() -> None:
        values.append(t.squared)

    values: list[int] = []
    app = application()
    t = MyThread()
    _ = t.finished.connect(slot1)
    _ = t.finished.connect(slot2)
    t.start(4)
    assert len(values) == 0
    while t.is_running():
        _ = t.wait(10)
        app.processEvents()

    # allow some time for the event loop to emit the finished() signal to the slots
    for _ in range(10):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [16, 16]
    assert t.stop() is None


def test_connect_signal_slot() -> None:  # noqa: C901, PLR0915
    class MyWorker(Worker):
        empty: Signal = Signal()
        renamed: Signal = Signal(name="new_name")
        data: Signal = Signal(float, name="floating_point")
        state: Signal = Signal(bool, int)

        def process(self) -> None:  # pyright: ignore[reportImplicitOverride]
            for index in range(10):
                if index in {2, 4}:
                    self.empty.emit()
                elif index == 3:
                    self.renamed.emit()
                elif index == 5:
                    self.new_name.emit()  # type: ignore[attr-defined] # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                elif index == 7:
                    self.state.emit(True, 1)  # noqa: FBT003
                elif index == 8:
                    self.data.emit(1.2)

    @Slot()
    def on_empty() -> None:
        values.append("empty")

    @Slot()
    def on_renamed_1() -> None:
        values.append("renamed-1")

    @Slot()
    def on_renamed_2() -> None:
        values.append("renamed-2")

    @Slot()
    def on_renamed_3() -> None:
        values.append("renamed-3")

    @Slot(float)
    def on_data(val: float) -> None:
        values.append(val)

    @Slot(float)
    def on_data_plus_10(val: float) -> None:
        values.append(val + 10)

    @Slot(bool, int)
    def on_state(b: bool, i: int) -> None:  # noqa: FBT001
        values.append((b, i))

    @Slot()
    def on_done() -> None:
        values.append("done")

    is_pyqt6 = binding.name == "PyQt6"
    values: list[str | float | tuple[bool, int]] = []

    app = application()
    t = Thread(MyWorker)

    with pytest.raises(TypeError, match=r"QtCore\.Signal or string"):
        t.worker_connect(b"empty", on_empty)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    with pytest.raises(TypeError, match=r"must be callable"):
        t.worker_connect("empty", None)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    with pytest.raises(ValueError, match=r"No Worker signals were connected to slots"):
        t.worker_disconnect("empty", on_empty)
    with pytest.raises(ValueError, match=r"No Worker signals were connected to slots"):
        t.worker_disconnect("empty", lambda: on_empty())  # noqa: PLW0108

    if is_pyqt6:
        # no 'name' attribute defined in the Signal constructor
        # must use the class attribute name
        with pytest.raises(TypeError, match=r"Cannot determine the Signal name"):
            t.worker_disconnect(MyWorker.empty, on_empty)
        t.worker_connect("empty", on_empty)
    else:
        t.worker_connect(MyWorker.empty, on_empty)

    t.worker_connect("empty", on_empty)
    t.worker_connect(MyWorker.renamed, on_renamed_1)
    t.worker_connect("renamed", on_renamed_3)
    t.worker_connect(MyWorker.renamed, lambda: values.append("renamed-4"))
    t.worker_connect("new_name", on_renamed_2)
    t.worker_connect(MyWorker.data, on_data)
    t.worker_connect("floating_point", on_data_plus_10)
    if is_pyqt6:
        # no 'name' defined in the Signal constructor
        # must use the class attribute name
        t.worker_connect("state", on_state)
    else:
        t.worker_connect(MyWorker.state, on_state)
    t.worker_connect("state", on_state)
    _ = t.finished.connect(on_done)
    t.start()

    # allow some time for the event loop to emit the finished() signal
    for _ in range(100):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [
        "empty",
        "empty",
        "renamed-1",
        "renamed-3",
        "renamed-4",
        "renamed-2",
        "empty",
        "empty",
        "renamed-1",
        "renamed-3",
        "renamed-4",
        "renamed-2",
        (True, 1),
        (True, 1),
        1.2,
        11.2,
        "done",
    ]

    assert t.stop() is None

    with pytest.raises(ValueError, match=r"not connected to the signal 'invalid'"):
        t.worker_disconnect("invalid", on_data)
    with pytest.raises(ValueError, match=r"not connected to the signal 'empty'"):
        t.worker_disconnect("empty", on_data)
    with pytest.raises(ValueError, match=r"not connected to the signal 'empty'"):
        t.worker_disconnect("empty", lambda: on_empty())  # noqa: PLW0108

    t.worker_disconnect("renamed", on_renamed_3)
    t.worker_disconnect(MyWorker.renamed, on_renamed_2)
    t.worker_disconnect("floating_point", on_data)
    if is_pyqt6:
        # no 'name' defined in the Signal constructor
        # must use the class attribute name
        t.worker_disconnect("empty", on_empty)
    else:
        t.worker_disconnect(MyWorker.empty, on_empty)

    values.clear()
    t.start()

    # allow some time for the event loop to emit the finished() signal
    for _ in range(100):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [
        "empty",
        "renamed-1",
        "renamed-4",
        "empty",
        "renamed-1",
        "renamed-4",
        (True, 1),
        (True, 1),
        11.2,
        "done",
    ]

    assert t.stop() is None
