import pytest

from msl.qt import (
    application,
    QtCore,
    Thread,
    Worker,
    Signal,
    Slot,
    binding,
)


def test_invalid_constructor():

    class MyWorker(Worker):
        def __init__(self):
            super(MyWorker, self).__init__()

    with pytest.raises(TypeError, match=r'must not be instantiated'):
        Thread(MyWorker())

    with pytest.raises(TypeError, match=r'not a Worker subclass'):
        Thread(QtCore.QTimer)


def test_worker_raises_exception():

    class MyWorker(Worker):

        def __init__(self, seconds, raise_exception):
            super(MyWorker, self).__init__()
            self.seconds = seconds
            self.raise_exception = raise_exception
            self.result = -1

        def process(self):
            QtCore.QThread.sleep(self.seconds)
            if self.raise_exception:
                raise OSError('Cannot open file')
            self.result = self.seconds

    class MyThread(Thread):

        def __init__(self):
            super(MyThread, self).__init__(MyWorker)

        def error_handler(self, exception, traceback):
            assert 'Cannot open file' == str(exception)

    app = application()
    threads = [MyThread() for i in range(10)]

    # check that calling the methods that require
    # self._thread to be created do not raise an exception
    assert all([not thread.is_running() for thread in threads])
    assert all([not thread.is_finished() for thread in threads])
    for t in threads:
        assert t.quit() is None
        assert t.wait() is None
        assert t.stop() is None

    # start certain threads
    for index, thread in enumerate(threads):
        if index % 2:
            thread.start(index, index > 5)  # only raise the exception if index > 5

    assert all([thread.is_running() for i, thread in enumerate(threads) if i % 2])
    assert all([not thread.is_running() for i, thread in enumerate(threads) if not i % 2])
    assert all([not thread.is_finished() for thread in threads])

    # The following tests that a RuntimeError exception is not raised
    #   RuntimeError: Internal C++ object (*.QtCore.QThread) already deleted.
    #
    # The fact that this test finishes also shows that the QThread did properly quit
    # after an exception is raised by the Worker
    while any([thread.is_running() for thread in threads]):
        for thread in threads:
            thread.wait(100)
        app.processEvents()

    # another check that calling wait() won't block forever
    for thread in threads:
        thread.wait()

    assert all([not thread.is_running() for thread in threads])

    # the threads that started and did not raise an error are finished
    # the threads that never started or that raised an exception are not finished
    assert all([thread.is_finished() for i, thread in enumerate(threads) if i in [1, 3, 5]])
    assert all([not thread.is_finished() for i, thread in enumerate(threads) if not i % 2])

    # get the result from each worker
    for index, thread in enumerate(threads):
        if index == 1 or index == 3 or index == 5:
            assert thread.result == index
        elif not index % 2:
            with pytest.raises(AttributeError, match=r'You must start the Thread'):
                r = thread.result
        else:
            assert thread.result == -1


def test_finished():

    class MyWorker(Worker):

        def __init__(self, index):
            super(MyWorker, self).__init__()
            self.index = index
            self.squared = None

        def process(self):
            QtCore.QThread.msleep(500)
            self.squared = self.index ** 2

    class MyThread(Thread):

        def __init__(self):
            super(MyThread, self).__init__(MyWorker)

    def slot1():
        values.append(t.squared)

    def slot2():
        values.append(t.squared)

    values = []
    app = application()
    t = MyThread()
    t.finished.connect(slot1)
    t.finished.connect(slot2)
    t.start(4)
    assert len(values) == 0
    while t.is_running():
        t.wait(10)
        app.processEvents()

    # allow some time for the event loop to emit the finished() signal to the slots
    for i in range(10):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [16, 16]
    t.stop()


def test_connect_signal_slot():
    class MyWorker(Worker):
        empty = Signal()
        renamed = Signal(name='new_name')
        data = Signal(float, name='floating_point')
        state = Signal(bool, int)

        def process(self):
            for index in range(10):
                if index == 2 or index == 4:
                    self.empty.emit()
                elif index == 3:
                    self.renamed.emit()
                elif index == 5:
                    self.new_name.emit()
                elif index == 7:
                    self.state.emit(True, 1)
                elif index == 8:
                    self.data.emit(1.2)

    @Slot()
    def on_empty():
        values.append('empty')

    @Slot()
    def on_renamed_1():
        values.append('renamed-1')

    @Slot()
    def on_renamed_2():
        values.append('renamed-2')

    @Slot()
    def on_renamed_3():
        values.append('renamed-3')

    @Slot(float)
    def on_data(val):
        values.append(val)

    @Slot(float)
    def on_data_plus_10(val):
        values.append(val+10)

    @Slot(bool, int)
    def on_state(*args):
        values.append(args)

    @Slot()
    def on_done():
        values.append('done')

    is_pyqt6 = binding.name == 'PyQt6'
    values = []

    app = application()
    t = Thread(MyWorker)

    with pytest.raises(TypeError, match='QtCore.Signal or string'):
        t.worker_connect(b'empty', on_empty)
    with pytest.raises(TypeError, match='must be callable'):
        t.worker_connect('empty', None)
    with pytest.raises(ValueError, match='No Worker signals were connected to slots'):
        t.worker_disconnect('empty', on_empty)
    with pytest.raises(ValueError, match='No Worker signals were connected to slots'):
        t.worker_disconnect('empty', lambda: on_empty())

    if is_pyqt6:
        with pytest.raises(TypeError, match='Cannot determine the Signal name'):
            t.worker_disconnect(MyWorker.empty, on_empty)

    if is_pyqt6:
        # no 'name' defined in the Signal constructor
        # must use the class attribute name
        t.worker_connect('empty', on_empty)
    else:
        t.worker_connect(MyWorker.empty, on_empty)
    t.worker_connect('empty', on_empty)
    t.worker_connect(MyWorker.renamed, on_renamed_1)
    t.worker_connect('renamed', on_renamed_3)
    t.worker_connect(MyWorker.renamed, lambda: values.append('renamed-4'))
    t.worker_connect('new_name', on_renamed_2)
    t.worker_connect(MyWorker.data, on_data)
    t.worker_connect('floating_point', on_data_plus_10)
    if is_pyqt6:
        # no 'name' defined in the Signal constructor
        # must use the class attribute name
        t.worker_connect('state', on_state)
    else:
        t.worker_connect(MyWorker.state, on_state)
    t.worker_connect('state', on_state)
    t.finished.connect(on_done)
    t.start()

    # allow some time for the event loop to emit the finished() signal
    for i in range(100):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [
        'empty', 'empty',
        'renamed-1', 'renamed-3', 'renamed-4', 'renamed-2',
        'empty', 'empty',
        'renamed-1', 'renamed-3', 'renamed-4', 'renamed-2',
        (True, 1), (True, 1),
        1.2, 11.2,
        'done'
    ]

    t.stop()

    with pytest.raises(ValueError, match="not connected to the signal 'invalid'"):
        t.worker_disconnect('invalid', on_data)
    with pytest.raises(ValueError, match="not connected to the signal 'empty'"):
        t.worker_disconnect('empty', on_data)
    with pytest.raises(ValueError, match="not connected to the signal 'empty'"):
        t.worker_disconnect('empty', lambda: on_empty())

    t.worker_disconnect('renamed', on_renamed_3)
    t.worker_disconnect(MyWorker.renamed, on_renamed_2)
    t.worker_disconnect('floating_point', on_data)
    if is_pyqt6:
        # no 'name' defined in the Signal constructor
        # must use the class attribute name
        t.worker_disconnect('empty', on_empty)
    else:
        t.worker_disconnect(MyWorker.empty, on_empty)

    values.clear()
    t.start()

    # allow some time for the event loop to emit the finished() signal
    for i in range(100):
        QtCore.QThread.msleep(10)
        app.processEvents()

    assert values == [
        'empty',
        'renamed-1', 'renamed-4',
        'empty',
        'renamed-1', 'renamed-4',
        (True, 1), (True, 1),
        11.2,
        'done'
    ]

    t.stop()
