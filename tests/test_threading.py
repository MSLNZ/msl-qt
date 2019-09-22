import pytest

from msl.qt import QtCore, Thread, Worker, application


def test_invalid_constructor():

    class MyWorker(Worker):
        def __init__(self):
            super(MyWorker, self).__init__()

    with pytest.raises(TypeError) as err:
        Thread(MyWorker())
    assert str(err.value).endswith('must not be instantiated')

    with pytest.raises(TypeError) as err:
        Thread(QtCore.QTimer)
    assert str(err.value).endswith('not a Worker subclass')


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
                raise IOError('Cannot open file')
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
            with pytest.raises(AttributeError) as err:
                r = thread.result
            assert str(err.value).startswith('You must start the Thread')
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
    t.quit()
